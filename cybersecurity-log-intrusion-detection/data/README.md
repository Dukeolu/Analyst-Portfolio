# Data — Log Analysis & Intrusion Detection

Simulated for this portfolio. Meridian Manufacturing (the same simulated company as the IT Support case, viewed here from a security angle), its employees, and every log event here are fictional — a real company's authentication and firewall logs would be far too sensitive to publish, even anonymized (they'd reveal usernames, IP addressing, and real attack history).

## Files

### `raw/auth_events.csv` (4,887 rows)

VPN gateway authentication log, 30 days (2025-06-01 to 2025-06-30), 200 employee accounts.

| Column | Description |
|---|---|
| `event_id` | Event ID |
| `timestamp` | Event timestamp |
| `username` | Account attempting to log in |
| `source_ip` | Source IP address |
| `source_country` | GeoIP country for the source IP (legitimate traffic is almost entirely US/Canada; attacker traffic is assigned other countries) |
| `event_type` | `login_success` or `login_failed` |

### `raw/firewall_events.csv` (1,793 rows)

Perimeter firewall connection log, aggregated daily by source IP and port.

| Column | Description |
|---|---|
| `log_date` | Date |
| `source_ip` | Source IP |
| `port` | Destination port (443 = the VPN gateway; others = closed ports probed during reconnaissance) |
| `connection_count` | Number of connection attempts that day |
| `blocked` | 1 if these connections were blocked (closed port), 0 if allowed (443, the VPN gateway is open by design) |

### `raw/ground_truth_attack_ips.csv` and `raw/ground_truth_compromised_accounts.csv`

Used only to evaluate the detection rules — never fed into the rules themselves. Lists the 6 simulated attacker source IPs and the 4 accounts that were actually compromised.

## How it was generated (`src/generate_data.py`)

Two distinct attack patterns were seeded into an otherwise ordinary month of VPN login traffic:

- **4 "loud" brute-force campaigns** — one attacker IP sends 25–45 failed login attempts against a single username within a short burst (minutes). 2 of the 4 guess the password correctly on the final attempt (account takeover); the other 2 fail to guess it.
- **2 "low-and-slow" credential-stuffing campaigns** — one attacker IP tries 1–2 failed attempts each against ~85–95 distinct usernames, spread across an 18-hour window (deliberately too slow to trip a burst-based rule), then succeeds against one weak-password account as its last attempt, followed 25–90 minutes later by a second, anomalous successful login on that same account from a *different* external IP — simulating the attacker moving to a "clean" proxy after finding working credentials.

A realistic false-positive source is also built in: **~120 of the 200 employees work from the office and share one NAT egress IP** (`203.0.113.5`), so that single address legitimately contacts far more distinct usernames per day than any individual attacker — but with a low failure rate, since it's almost entirely genuine, successful logins. Both attacker IP groups additionally generate port-scanning traffic in the firewall log on their attack day, corroborating the auth-log signal from a second source.

## Limitations

- This is simulated data with two deliberately seeded attack patterns; a real environment would have a much wider variety of attack techniques (password spraying across multiple organizations, credential-stuffing from leaked-password lists, insider threats) that this dataset doesn't attempt to represent.
- GeoIP country is a simplified stand-in for real geolocation data, and the specific countries used are illustrative, not a claim about where real attacks originate.
- The dataset covers exactly one attack "episode" of each type; a real 30-day window at a company this size would likely see many more (mostly unsuccessful, automated) attack attempts, at a lower and steadier background rate than the two clean bursts modeled here.
- The account-takeover rule's precision/recall figures (see the main README) are specific to this dataset's exact parameters (200 accounts, 4.5% typo rate, 3-fail/24h threshold) and would need re-tuning against a real environment's actual failed-login base rate.
