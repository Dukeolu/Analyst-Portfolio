"""
Picks which 5 KB articles are worth writing (highest deflectable ticket
volume, not the 5 easiest topics) and quantifies the impact of publishing
them under a stated, disclosed self-service adoption assumption.
"""
import csv
from collections import defaultdict

TECH_HOURLY_COST = 45.0          # same disclosed rate used elsewhere in this portfolio
SELF_SERVICE_ADOPTION_RATE = 0.25  # stated assumption: 25% of users hitting one of these
                                    # issues use the KB instead of filing a ticket, once the
                                    # article is published and linked from the ticket-submission
                                    # portal for that issue type — a deliberately conservative
                                    # figure, not an aspirational one

with open("data/raw/tickets_6mo.csv") as f:
    rows = list(csv.DictReader(f))

by_issue = defaultdict(lambda: [0, 0.0])
for r in rows:
    if r["self_service_eligible"] == "Y":
        key = (r["category"], r["issue"])
        by_issue[key][0] += 1
        by_issue[key][1] += float(r["resolution_minutes"])

ranked = sorted(by_issue.items(), key=lambda x: -x[1][1])  # rank by total minutes, not ticket count
top5 = ranked[:5]

print("=" * 78)
print("TOP 5 SELF-SERVICE-ELIGIBLE ISSUES BY TOTAL TECHNICIAN TIME (6 months observed)")
print("=" * 78)
total_tickets_6mo = 0
total_minutes_6mo = 0.0
for (cat, issue), (count, minutes) in top5:
    print(f"  {count:>4} tickets   {minutes:>7.0f} min total   {cat} / {issue}")
    total_tickets_6mo += count
    total_minutes_6mo += minutes

annual_tickets = total_tickets_6mo * 2
annual_minutes = total_minutes_6mo * 2
annual_hours = annual_minutes / 60

deflected_tickets = annual_tickets * SELF_SERVICE_ADOPTION_RATE
deflected_hours = annual_hours * SELF_SERVICE_ADOPTION_RATE
deflected_dollars = deflected_hours * TECH_HOURLY_COST

print(f"\nCombined addressable volume (these 5 issues, annualized): {annual_tickets:.0f} tickets/yr, "
      f"{annual_hours:.0f} technician-hours/yr")
print(f"\nAt a stated {SELF_SERVICE_ADOPTION_RATE:.0%} self-service adoption rate:")
print(f"  Tickets deflected/yr: {deflected_tickets:.0f}")
print(f"  Technician-hours saved/yr: {deflected_hours:.1f}")
print(f"  Dollar impact/yr: ${deflected_dollars:,.0f}")

with open("data/raw/deflection_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["category", "issue", "tickets_6mo", "minutes_6mo", "tickets_annual", "minutes_annual"])
    for (cat, issue), (count, minutes) in top5:
        writer.writerow([cat, issue, count, round(minutes, 0), count * 2, round(minutes * 2, 0)])
    writer.writerow(["TOTAL", "", total_tickets_6mo, round(total_minutes_6mo, 0), annual_tickets, round(annual_minutes, 0)])

with open("data/raw/deflection_impact.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["metric", "value"])
    writer.writerow(["self_service_adoption_rate_pct", SELF_SERVICE_ADOPTION_RATE * 100])
    writer.writerow(["annual_addressable_tickets", annual_tickets])
    writer.writerow(["annual_addressable_hours", round(annual_hours, 1)])
    writer.writerow(["annual_deflected_tickets", round(deflected_tickets, 0)])
    writer.writerow(["annual_deflected_hours", round(deflected_hours, 1)])
    writer.writerow(["annual_dollar_impact", round(deflected_dollars, 0)])

print("\nWrote data/raw/deflection_summary.csv and data/raw/deflection_impact.csv")
