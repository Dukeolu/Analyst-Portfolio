"""
Two detection rules evaluated against the same 30-day auth log:

1. `naive_burst_rule` -- the security team's current rule: flag a source IP
   if it generates >= FAIL_THRESHOLD failed logins within a WINDOW_MINUTES
   rolling window. Catches fast, loud brute force. Structurally blind to an
   attacker who never sends more than a couple of failed attempts to any one
   account.

2. `fanout_rule` -- proposed rule: flag a source IP if, within a 24-hour
   window, it generates *failed* attempts against at least MIN_DISTINCT_FAILED
   distinct usernames AND its overall failure rate (fails / total attempts)
   is at least MIN_FAILURE_RATE. The failure-rate gate is what keeps this
   rule from misfiring on the shared office NAT IP, which touches far more
   distinct usernames per day than any attacker IP but almost always
   succeeds.

3. `account_takeover_rule` -- flags a successful login if the same username
   had >= MIN_RECENT_FAILS failed attempts in the preceding LOOKBACK_HOURS,
   regardless of source IP -- catches "brute-force-then-success" directly.

An earlier draft of the fan-out rule (kept here as `naive_fanout_rule_v1`,
commented in the notebook) flagged on *any* attempt, not just failures --
which fired on the NAT IP every single day. This module ships the corrected
version; the notebook shows the before/after.
"""
import pandas as pd


def naive_burst_rule(auth: pd.DataFrame, fail_threshold: int = 5, window_minutes: int = 10) -> set:
    failed = auth[auth.event_type == "login_failed"].copy()
    failed["timestamp"] = pd.to_datetime(failed["timestamp"])
    flagged = set()
    for ip, grp in failed.groupby("source_ip"):
        times = grp["timestamp"].sort_values().tolist()
        window = []
        for t in times:
            window.append(t)
            window = [w for w in window if (t - w).total_seconds() <= window_minutes * 60]
            if len(window) >= fail_threshold:
                flagged.add(ip)
                break
    return flagged


def fanout_rule_v1_naive(auth: pd.DataFrame, min_distinct: int = 15) -> set:
    """Draft 1: fan-out on ANY attempt (success or fail). Fires on the NAT IP."""
    auth = auth.copy()
    auth["date"] = pd.to_datetime(auth["timestamp"]).dt.date
    grouped = auth.groupby(["date", "source_ip"])["username"].nunique().reset_index(name="n_distinct")
    flagged_daily = grouped[grouped["n_distinct"] >= min_distinct]
    return set(flagged_daily["source_ip"].unique())


def fanout_rule_v2_refined(auth: pd.DataFrame, min_distinct_failed: int = 15,
                            min_failure_rate: float = 0.5) -> set:
    """Draft 2: fan-out on FAILED usernames specifically, gated by an overall
    failure-rate threshold -- excludes high-volume-but-mostly-successful
    sources like the office NAT IP."""
    auth = auth.copy()
    auth["date"] = pd.to_datetime(auth["timestamp"]).dt.date
    flagged = set()
    for (date, ip), grp in auth.groupby(["date", "source_ip"]):
        failed = grp[grp.event_type == "login_failed"]
        n_distinct_failed = failed["username"].nunique()
        failure_rate = len(failed) / len(grp)
        if n_distinct_failed >= min_distinct_failed and failure_rate >= min_failure_rate:
            flagged.add(ip)
    return flagged


def account_takeover_rule(auth: pd.DataFrame, min_recent_fails: int = 3, lookback_hours: int = 24) -> pd.DataFrame:
    auth = auth.copy()
    auth["timestamp"] = pd.to_datetime(auth["timestamp"])
    auth = auth.sort_values("timestamp")
    flags = []
    for username, grp in auth.groupby("username"):
        grp = grp.sort_values("timestamp")
        fail_times = []
        for _, row in grp.iterrows():
            cutoff = row["timestamp"] - pd.Timedelta(hours=lookback_hours)
            fail_times = [t for t in fail_times if t >= cutoff]
            if row["event_type"] == "login_success" and len(fail_times) >= min_recent_fails:
                flags.append({"username": username, "timestamp": row["timestamp"],
                               "source_ip": row["source_ip"], "recent_fail_count": len(fail_times)})
            if row["event_type"] == "login_failed":
                fail_times.append(row["timestamp"])
    return pd.DataFrame(flags)


if __name__ == "__main__":
    auth = pd.read_csv("data/raw/auth_events.csv")
    ground_truth = pd.read_csv("data/raw/ground_truth_attack_ips.csv")
    attack_ips = set(ground_truth["source_ip"])
    all_ips = set(auth["source_ip"])
    benign_ips = all_ips - attack_ips

    print(f"Total distinct source IPs: {len(all_ips)} ({len(attack_ips)} attacker, {len(benign_ips)} benign)")
    print()

    naive = naive_burst_rule(auth)
    print(f"[Naive burst rule] flagged {len(naive)} IPs: {naive}")
    print(f"  True positives: {naive & attack_ips}")
    print(f"  False positives: {naive - attack_ips}")
    print(f"  Missed attackers (false negatives): {attack_ips - naive}")
    print()

    v1 = fanout_rule_v1_naive(auth)
    print(f"[Fan-out v1, naive -- any attempt] flagged {len(v1)} IPs")
    print(f"  True positives: {v1 & attack_ips}")
    print(f"  False positives: {v1 - attack_ips}")
    print()

    v2 = fanout_rule_v2_refined(auth)
    print(f"[Fan-out v2, refined -- failed only + failure-rate gate] flagged {len(v2)} IPs: {v2}")
    print(f"  True positives: {v2 & attack_ips}")
    print(f"  False positives: {v2 - attack_ips}")
    print(f"  Missed attackers (false negatives): {attack_ips - v2}")
    print()

    combined = naive | v2
    print(f"[Naive + refined fan-out combined] catches: {combined & attack_ips} ({len(combined & attack_ips)}/{len(attack_ips)})")
    print(f"  Combined false positives: {combined - attack_ips}")
    print()

    takeovers = account_takeover_rule(auth)
    print(f"[Account takeover rule] flagged {len(takeovers)} success events:")
    print(takeovers.to_string(index=False))
    gt_compromised = pd.read_csv("data/raw/ground_truth_compromised_accounts.csv")
    print(f"\nGround-truth compromised accounts (first success): {gt_compromised['username'].tolist()}")
