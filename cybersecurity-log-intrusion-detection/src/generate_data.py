"""
Generates simulated authentication + firewall logs for Meridian Manufacturing
(the same simulated company as the IT Support case, viewed here from a
security angle) -- 30 days of VPN gateway authentication events across 200
employee accounts, seeded with two distinct attack patterns and one
realistic false-positive source, built to test whether the security team's
current detection rule actually catches what it's supposed to.

Ground truth (used only for evaluation, never given to the detection rules):
  - 4 "loud brute force" campaigns: one attacker IP hammers ONE username with
    25-45 failed attempts in a short burst. 2 of the 4 guess correctly and
    succeed (account takeover); 2 fail out.
  - 2 "low-and-slow credential stuffing" campaigns: one attacker IP tries
    1-2 failed attempts each against ~85-95 distinct usernames spread across
    an 18-hour window (no single account ever sees a fast burst), then
    succeeds against one weak-password account as its last attempt, followed
    shortly by a second, anomalous successful login on that same account
    from a *different* external IP (the attacker moving to a "clean" proxy).
  - A large legitimate "office NAT" source IP shared by ~120 of the 200
    employees, generating high daily *volume* and touching many distinct
    usernames -- a realistic false-positive risk for any naive
    "many distinct usernames from one IP" detection rule.
  - Ordinary background noise: individual remote-worker IPs, occasional
    single failed logins from typos.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG = np.random.default_rng(23)

N_USERS = 200
USERNAMES = [f"user{str(i).zfill(4)}" for i in range(1, N_USERS + 1)]
START = datetime(2025, 6, 1)
N_DAYS = 30

COUNTRIES_LEGIT = ["United States"] * 8 + ["Canada"]  # legit traffic is almost all US, some CA
COUNTRIES_ATTACK = ["Russia", "Vietnam", "Brazil", "Nigeria", "Romania", "Indonesia"]

NAT_IP = "203.0.113.5"          # shared corporate office NAT egress IP
NAT_USERS = USERNAMES[:120]     # 120 of 200 employees work from the office
REMOTE_USERS = USERNAMES[120:]  # 80 work remote, each with a mostly-stable home IP

remote_ip_map = {u: f"198.51.100.{(i % 250) + 1}" for i, u in enumerate(REMOTE_USERS)}

events = []
event_id = 1


def add_event(ts, username, source_ip, country, success):
    global event_id
    events.append({
        "event_id": f"AUTH-{event_id:06d}",
        "timestamp": ts.isoformat(timespec="seconds"),
        "username": username,
        "source_ip": source_ip,
        "source_country": country,
        "event_type": "login_success" if success else "login_failed",
    })
    event_id += 1


# ------------------------------------------------------------ background traffic
for day in range(N_DAYS):
    date = START + timedelta(days=day)
    is_weekend = date.weekday() >= 5
    daily_login_prob = 0.35 if is_weekend else 0.88

    for user in USERNAMES:
        if RNG.random() > daily_login_prob:
            continue
        ip = NAT_IP if user in NAT_USERS else remote_ip_map[user]
        country = RNG.choice(COUNTRIES_LEGIT)
        hour = RNG.normal(13, 3.2)
        hour = min(max(hour, 6), 22)
        ts = date + timedelta(hours=float(hour), minutes=float(RNG.uniform(0, 59)))

        # occasional typo: one failed attempt before success
        if RNG.random() < 0.045:
            add_event(ts - timedelta(minutes=1), user, ip, country, success=False)
        add_event(ts, user, ip, country, success=True)

# ------------------------------------------------------------ Pattern A: loud brute force (x4)
attack_a_ips = []
attack_a_compromises = []  # (username, success_ts, source_ip)
for i in range(4):
    target_user = RNG.choice(USERNAMES)
    attacker_ip = f"185.220.10{i}.{RNG.integers(10, 250)}"
    attack_a_ips.append(attacker_ip)
    country = RNG.choice(COUNTRIES_ATTACK)
    day = RNG.integers(2, N_DAYS - 2)
    start_ts = START + timedelta(days=int(day), hours=float(RNG.uniform(0, 23)))
    n_attempts = RNG.integers(25, 46)
    succeeds = i < 2  # first 2 of the 4 guess correctly

    cursor = start_ts
    for attempt in range(n_attempts):
        cursor += timedelta(seconds=float(RNG.uniform(10, 25)))
        is_last = attempt == n_attempts - 1
        will_succeed = succeeds and is_last
        add_event(cursor, target_user, attacker_ip, country, success=will_succeed)
        if will_succeed:
            attack_a_compromises.append((target_user, cursor, attacker_ip))

# ------------------------------------------------------------ Pattern B: low-and-slow credential stuffing (x2)
attack_b_ips = []
compromise_events = []  # (username, first_success_ts, second_clean_ip, second_success_ts)
for i in range(2):
    attacker_ip = f"91.207.{RNG.integers(1,254)}.{RNG.integers(1,254)}"
    attack_b_ips.append(attacker_ip)
    country = RNG.choice(COUNTRIES_ATTACK)
    day = RNG.integers(2, N_DAYS - 2)
    campaign_start = START + timedelta(days=int(day), hours=1)
    n_targets = int(RNG.integers(85, 96))
    targets = list(RNG.choice(USERNAMES, size=n_targets, replace=False))
    weak_password_user = targets[-1]  # the last one tried is the one that succeeds

    # spread attempts across an 18-hour window, 1-2 attempts per target
    window_seconds = 18 * 3600
    times = sorted(RNG.uniform(0, window_seconds, size=n_targets))
    for target, offset in zip(targets, times):
        ts = campaign_start + timedelta(seconds=float(offset))
        is_weak_target = target == weak_password_user
        add_event(ts, target, attacker_ip, country, success=False)
        if RNG.random() < 0.15 and not is_weak_target:
            # a second failed attempt against some targets, still not enough to trip a burst rule
            add_event(ts + timedelta(minutes=float(RNG.uniform(2, 8))), target, attacker_ip, country, success=False)

    # a couple more failed guesses specifically against the weak-password account
    # shortly before the final successful guess (still low-and-slow, not a burst)
    for k in range(2):
        add_event(campaign_start + timedelta(seconds=window_seconds - 300 + k * 90),
                  weak_password_user, attacker_ip, country, success=False)

    # final, successful guess against the weak-password account, from the same attack IP
    first_success_ts = campaign_start + timedelta(seconds=window_seconds - 60)
    add_event(first_success_ts, weak_password_user, attacker_ip, country, success=True)

    # the anomalous second login: same account, new "clean" external IP, odd hour
    clean_ip = f"45.155.{RNG.integers(1,254)}.{RNG.integers(1,254)}"
    clean_country = RNG.choice(COUNTRIES_ATTACK)
    second_success_ts = first_success_ts + timedelta(minutes=float(RNG.uniform(25, 90)))
    add_event(second_success_ts, weak_password_user, clean_ip, clean_country, success=True)

    compromise_events.append((weak_password_user, first_success_ts, clean_ip, second_success_ts))

auth_df = pd.DataFrame(events).sort_values("timestamp").reset_index(drop=True)
auth_df.to_csv("data/raw/auth_events.csv", index=False)

# ------------------------------------------------------------ firewall log (daily, per source IP)
# Every auth attempt implies an allowed connection to the VPN gateway (443) --
# the gateway is internet-facing by design. Attacker IPs additionally
# generate a burst of *blocked* connection attempts to other closed ports on
# their attack day, representing reconnaissance/port scanning.
fw_rows = []
auth_df["date"] = pd.to_datetime(auth_df["timestamp"]).dt.date
gw_daily = auth_df.groupby(["date", "source_ip"]).size().reset_index(name="connection_count")
for _, r in gw_daily.iterrows():
    fw_rows.append({"log_date": str(r["date"]), "source_ip": r["source_ip"], "port": 443,
                     "connection_count": int(r["connection_count"]), "blocked": 0})

for ip in attack_a_ips + attack_b_ips:
    day_events = auth_df[auth_df["source_ip"] == ip]
    scan_date = pd.to_datetime(day_events["timestamp"]).dt.date.iloc[0]
    for port in RNG.choice([22, 3389, 8080, 5900], size=int(RNG.integers(2, 4)), replace=False):
        fw_rows.append({"log_date": str(scan_date), "source_ip": ip, "port": int(port),
                         "connection_count": int(RNG.integers(3, 12)), "blocked": 1})

fw_df = pd.DataFrame(fw_rows).sort_values(["log_date", "source_ip"]).reset_index(drop=True)
fw_df.to_csv("data/raw/firewall_events.csv", index=False)

# ------------------------------------------------------------ ground truth (for evaluation only)
ground_truth = []
for ip in attack_a_ips:
    ground_truth.append({"source_ip": ip, "pattern": "loud_brute_force"})
for ip in attack_b_ips:
    ground_truth.append({"source_ip": ip, "pattern": "low_and_slow_stuffing"})
gt_df = pd.DataFrame(ground_truth)
gt_df.to_csv("data/raw/ground_truth_attack_ips.csv", index=False)

compromise_df = pd.DataFrame(compromise_events,
                              columns=["username", "first_success_ts", "second_clean_ip", "second_success_ts"])
compromise_df["pattern"] = "low_and_slow_stuffing"
compromise_a_df = pd.DataFrame(attack_a_compromises, columns=["username", "first_success_ts", "source_ip"])
compromise_a_df["pattern"] = "loud_brute_force"
all_compromises = pd.concat([
    compromise_df[["username", "first_success_ts", "pattern"]],
    compromise_a_df[["username", "first_success_ts", "pattern"]],
], ignore_index=True)
all_compromises.to_csv("data/raw/ground_truth_compromised_accounts.csv", index=False)

print(f"Total auth events: {len(auth_df)}")
print(f"Failed: {(auth_df.event_type=='login_failed').sum()}, Success: {(auth_df.event_type=='login_success').sum()}")
print(f"Attack A IPs: {attack_a_ips}")
print(f"Attack B IPs: {attack_b_ips}")
print(f"Compromised accounts: {compromise_df['username'].tolist()}")
print(f"Firewall log rows: {len(fw_df)}")
