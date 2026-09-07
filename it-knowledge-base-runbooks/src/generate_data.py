"""
Generates a simulated 6-month slice of Meridian Manufacturing help desk
tickets, tagged by whether the specific issue is one a well-written KB
article could plausibly let the user resolve themselves — used to decide
which 5 KB articles are actually worth writing (highest deflectable
volume), not just the 5 easiest to write.
"""
import csv
import random

random.seed(11)

# (category, issue, self_service_eligible, avg_resolution_minutes, monthly_volume)
# Volumes and eligibility are a judgment call disclosed in data/README.md — the same
# kind of ticket categories established in the help desk triage case (Case IT-01),
# broken down one level further into the specific issue driving each ticket.
ISSUE_CATALOG = [
    ("Password Reset", "Forgot network password", True, 4.5, 62),
    ("Password Reset", "Account locked after failed attempts", True, 6.0, 24),
    ("Account Access", "New software access request", False, 12.0, 18),
    ("Account Access", "Shared drive permission request", False, 9.0, 14),
    ("Email & Calendar", "Can't set up email on phone", True, 9.5, 31),
    ("Email & Calendar", "Shared calendar not syncing", False, 14.0, 9),
    ("Hardware", "Printer won't print / shows offline", True, 11.0, 38),
    ("Hardware", "Monitor / dock not detected", False, 16.0, 12),
    ("Software Install", "Standard software request (pre-approved list)", True, 7.0, 27),
    ("Software Install", "Non-standard software request (needs approval)", False, 22.0, 8),
    ("Network & VPN", "Can't connect to office VPN", True, 13.5, 44),
    ("Network & VPN", "Can't connect to office wifi", True, 8.0, 29),
    ("Network & VPN", "VPN gateway down (site-wide)", False, 95.0, 2),
]

rows = []
ticket_id = 1
for category, issue, eligible, avg_minutes, monthly_volume in ISSUE_CATALOG:
    for month in range(1, 7):
        n_this_month = max(0, round(random.gauss(monthly_volume, monthly_volume * 0.18)))
        for _ in range(n_this_month):
            resolution_minutes = max(2.0, random.gauss(avg_minutes, avg_minutes * 0.25))
            rows.append({
                "ticket_id": f"KB-{ticket_id:05d}",
                "month": month,
                "category": category,
                "issue": issue,
                "self_service_eligible": "Y" if eligible else "N",
                "resolution_minutes": round(resolution_minutes, 1),
            })
            ticket_id += 1

with open("data/raw/tickets_6mo.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

total = len(rows)
eligible = sum(1 for r in rows if r["self_service_eligible"] == "Y")
print(f"Wrote {total} tickets over 6 months ({eligible} self-service-eligible, {100*eligible/total:.1f}%)")

from collections import defaultdict
by_issue = defaultdict(lambda: [0, 0.0])
for r in rows:
    if r["self_service_eligible"] == "Y":
        key = (r["category"], r["issue"])
        by_issue[key][0] += 1
        by_issue[key][1] += r["resolution_minutes"]

print("\nSelf-service-eligible issues, ranked by total ticket volume (6 months):")
for (cat, issue), (count, total_min) in sorted(by_issue.items(), key=lambda x: -x[1][0]):
    print(f"  {count:>4} tickets  {total_min:>7.0f} min total  {cat} / {issue}")
