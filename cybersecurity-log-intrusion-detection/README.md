# Does the Current Alert Rule Actually Catch the Attacks That Matter? — Meridian Manufacturing (simulated)

**Skills:** Python &middot; SQL &middot; log analysis &middot; detection-rule design &middot; SIEM-style correlation

## The business problem

Meridian Manufacturing's (simulated) security team relies on one alerting rule for its internet-facing VPN gateway: block a source IP after 5 failed logins within 10 minutes. It's never been tested against anything except the attacks it obviously catches. The real question the team needs answered: does this rule actually catch a patient attacker who never sends more than a couple of failed attempts to any one account — and if it doesn't, what would a better rule cost in false positives, given that the company's own office network would look suspicious to a naive version of that fix?

## The data

30 days of simulated VPN authentication logs (4,887 events, 200 employee accounts, 89 distinct source IPs) plus a corresponding perimeter firewall connection log. Full schema and generation methodology: [`data/README.md`](data/README.md).

## Data preparation

Authentication and firewall records are generated directly (`src/generate_data.py`) rather than pulled from a real SIEM — a real company's logs would reveal usernames, real IP addressing, and genuine attack history that can't be published even anonymized. Because it's generated rather than exported, there's no missing-value or duplicate cleanup here; the preparation work was seeding two realistic, distinct attack patterns (a loud brute-force burst and a slow, distributed credential-stuffing campaign) against a backdrop of ordinary login noise, and deliberately including a genuine false-positive risk — a shared office NAT IP used by 120 of the 200 employees — so the detection-rule evaluation isn't testing against a strawman with no plausible false positives.

## Analysis

1. **The current rule, reproduced exactly** (`src/detection_rules.py::naive_burst_rule`, and approximated in SQL as `sql/queries.sql` Q2) — flag a source IP with 5+ failed logins in any rolling 10-minute window, evaluated against the 6 known attacker IPs.
2. **A proposed fan-out rule, built and refined in two passes** — flag a source IP that contacts an unusually large number of distinct usernames in a day. The first draft (any attempt) is shown failing against the office NAT IP; the refined version (failed attempts only, gated by a minimum failure rate) is shown fixing it.
3. **An account-takeover rule** (`src/detection_rules.py::account_takeover_rule`) — flag a successful login within 24 hours of 3+ recent failed attempts on the same account, evaluated against the 4 confirmed compromised accounts.
4. **Firewall corroboration** (`sql/queries.sql` Q4) — cross-reference flagged auth-log IPs against independent port-scanning activity in the firewall log.

## Key findings

1. **The current rule's catch rate on a slow attack is essentially a coin flip.** It correctly catches all 4 loud brute-force IPs, but of the two near-identical low-and-slow credential-stuffing campaigns, it caught **one by chance** (its randomly-timed attempts happened to cluster tightly enough to trip the threshold) and **missed the other entirely**. A rule whose detection of a given attack pattern depends on random timing luck isn't one the team can rely on.
2. **The obvious fix has a real false-positive problem.** A first-draft "flag an IP touching 15+ distinct usernames a day" rule does catch both low-and-slow attackers — but it also flags the company's own shared office network address, which legitimately touches over 100 distinct usernames daily. An alert like that would very quickly get tuned out or ignored.
3. **Gating on failure rate, not just fan-out, fixes it.** Requiring both 15+ distinct *failed* usernames **and** an overall failure rate of 50%+ catches exactly the 2 real attacker IPs and zero false positives — because the office IP's traffic is almost all successful logins, while an attacker guessing passwords fails on nearly every attempt.
4. **Run together, the two rule families catch everything.** The current burst rule plus the refined fan-out rule catch **100% (6 of 6)** of known attacker IPs with **zero false positives** — neither rule alone gets there.
5. **The account-takeover rule has perfect recall but imperfect precision, and that's not entirely a flaw.** It flags all 4 genuinely compromised accounts (100% recall), plus 2 additional accounts that were targeted by a failed brute-force attempt but never actually compromised (66.7% precision). Those 2 "false positives" are accounts that just absorbed 40+ failed guesses — a reasonable case for a mandatory password reset regardless of whether the attacker ultimately succeeded, not really a false alarm to tune away.

| Metric | Value |
|---|---|
| Total auth events analyzed | 4,887 over 30 days |
| Current rule recall on attacker IPs | 5/6 (83.3%) |
| Refined fan-out + current rule, combined | 6/6 (100%), 0 false positives |
| Account-takeover rule recall / precision | 100% / 66.7% |
| Firewall corroboration | 6/6 attacker IPs also show port-scanning; 0 false positives |

## Recommendations

1. **Deploy the refined fan-out rule alongside the existing burst rule**, not instead of it — each catches attack patterns the other misses.
2. **Do not ship the naive "any attempt" version of the fan-out rule** — it would generate a daily alert on the company's own office network and get disabled or ignored within days.
3. **Add the account-takeover rule and treat every flag as requiring a password reset**, whether or not the specific login looks legitimate — the 2 "imprecise" flags in this analysis were accounts that survived an attack, not accounts that were never at risk.
4. **Use the firewall log as a corroborating signal, not a standalone one** — it independently confirms every flagged attacker IP with zero false positives, making it a cheap, high-confidence second check before escalating an alert.

## Expected impact

Deploying the refined rule set closes a detection gap that, on the evidence of this 30-day window, allowed a slow, patient attacker to operate essentially undetected — including one confirmed account compromise that would have gone completely unflagged under the current rule alone. The combined rule set achieves full detection of all 6 attacker IPs in this analysis with zero additional false-positive burden on the security team, and the account-takeover rule adds account-level visibility (including surfacing the attacker's follow-on "clean" pivot IP) that no IP-based rule alone provides.

> **The pitch in one line:** the current rule isn't wrong, it's incomplete — and the fix that closes the gap costs nothing in false positives once it's built correctly the second time.

## Limitations / next analysis

- The attack patterns and the false-positive scenario are simulated and deliberately seeded — a real environment would need to validate the refined fan-out thresholds (15 distinct failed usernames, 50% failure rate) against its own actual traffic before deploying them, since a different organization's shared-IP and typo-rate patterns would shift where the line should be drawn.
- This analysis covers one attack episode of each type in a single 30-day window; a production deployment would want to backtest these rules against a longer history, ideally including known-benign "busy day" traffic spikes (e.g., a password-expiration wave forcing many resets at once) that could plausibly trigger false positives this dataset doesn't include.
- The account-takeover rule is IP-agnostic on purpose (it flags success-after-failure regardless of source), which is why it correctly keeps flagging an account's subsequent legitimate logins until the failure count ages out of the 24-hour window — a real deployment should pair this with automatic ticket deduplication per account per day, since this analysis generated 11 alert events for 6 accounts, not one alert per account.
- The two attacker "clean pivot" IPs used for the second, post-compromise login are never independently flagged by either IP-level rule (they generate no failed attempts at all) — they were only surfaced as a byproduct of the account-takeover rule. A production system should specifically log and flag "new source IP for this account within N hours of a suspicious event" as its own signal, which this analysis doesn't build out as a standalone rule.
- Real intrusion detection would also draw on endpoint and network telemetry beyond auth and perimeter-firewall logs (DNS queries, process execution, lateral movement) that this two-log-source analysis doesn't have access to.

## Repo structure

```
cybersecurity-log-intrusion-detection/
├── README.md                          this file
├── requirements.txt
├── data/
│   ├── README.md                      data model, generation methodology, limitations
│   └── raw/
│       ├── auth_events.csv
│       ├── firewall_events.csv
│       ├── ground_truth_attack_ips.csv
│       └── ground_truth_compromised_accounts.csv
├── src/
│   ├── generate_data.py               builds the simulated auth + firewall logs
│   └── detection_rules.py             the naive/refined fan-out rule, burst rule, account-takeover rule
├── sql/
│   ├── build_db.py                    loads the CSVs into SQLite
│   ├── queries.sql                    the 5 labelled analysis queries
│   └── run_queries.py                 runs and prints all 5
├── notebooks/
│   ├── build_notebook.py              builds the notebook programmatically
│   └── intrusion_detection_analysis.ipynb   the executed analysis notebook
└── visuals/
    ├── rule_comparison.png
    ├── build_exhibit.py
    └── intrusion-detection-exhibit.html   self-contained visual summary (site link)
```
