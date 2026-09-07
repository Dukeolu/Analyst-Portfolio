"""
Compares the manual (historical) and automated new-hire onboarding processes
across the same 148-hire population: hands-on technician time and the two
error rates the manual process was actually failing on.
"""
import csv

TECH_HOURLY_COST = 45.0  # stated, disclosed fully-loaded IT technician cost — same assumption used in
                          # the help desk triage case, for consistency across the portfolio

with open("data/raw/manual_onboarding_log.csv") as f:
    manual = list(csv.DictReader(f))
with open("data/raw/automated_onboarding_log.csv") as f:
    automated = list(csv.DictReader(f))

n = len(manual)
manual_avg = sum(float(r["total_handson_minutes"]) for r in manual) / n
auto_avg = sum(float(r["total_handson_minutes"]) for r in automated) / n
minutes_saved_per_hire = manual_avg - auto_avg

manual_group_miss = sum(1 for r in manual if r["all_required_groups_assigned_first_try"] == "N")
manual_group_miss_rate = manual_group_miss / n

remote_manual = [r for r in manual if r["remote_eligible"] == "Y"]
manual_vpn_miss = sum(1 for r in remote_manual if r["vpn_ready_day1"] == "N")
manual_vpn_miss_rate = manual_vpn_miss / len(remote_manual)

# Rework cost: a missed group or missed VPN setup generates a follow-up access-request
# ticket, disclosed at 20 minutes of technician time to diagnose and fix — smaller than
# the original task since it's usually a single group/policy add, not the full process.
REWORK_MINUTES = 20.0
annual_rework_incidents = manual_group_miss + manual_vpn_miss
annual_rework_hours = annual_rework_incidents * REWORK_MINUTES / 60

annual_handson_hours_manual = manual_avg * n / 60
annual_handson_hours_auto = auto_avg * n / 60
annual_hours_saved = annual_handson_hours_manual - annual_handson_hours_auto + annual_rework_hours
annual_dollar_saved = annual_hours_saved * TECH_HOURLY_COST

print("=" * 72)
print(f"New-hire volume analyzed: {n} hires/year (stated assumption)")
print("=" * 72)
print(f"\nHands-on technician time per hire:")
print(f"  Manual process:    {manual_avg:.1f} min/hire")
print(f"  Automated process: {auto_avg:.1f} min/hire")
print(f"  Reduction:         {minutes_saved_per_hire:.1f} min/hire "
      f"({100*minutes_saved_per_hire/manual_avg:.1f}%)")

print(f"\nError rates (manual process only — automated is 0% by construction, lookup-table driven):")
print(f"  Missed >=1 required security group on first try: {manual_group_miss_rate:.1%} "
      f"({manual_group_miss} of {n} hires)")
print(f"  Missed day-1 VPN access (remote-eligible only, n={len(remote_manual)}): "
      f"{manual_vpn_miss_rate:.1%} ({manual_vpn_miss} of {len(remote_manual)})")

print(f"\nAnnual impact ({n} hires/year, ${TECH_HOURLY_COST:.0f}/hr fully-loaded technician cost):")
print(f"  Hands-on time, manual:    {annual_handson_hours_manual:.1f} hrs/yr")
print(f"  Hands-on time, automated: {annual_handson_hours_auto:.1f} hrs/yr")
print(f"  Rework avoided ({annual_rework_incidents} incidents x {REWORK_MINUTES:.0f} min): "
      f"{annual_rework_hours:.1f} hrs/yr")
print(f"  Total hours saved/yr: {annual_hours_saved:.1f}")
print(f"  Total dollar impact/yr: ${annual_dollar_saved:,.0f}")

with open("data/raw/onboarding_comparison_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["metric", "value"])
    writer.writerow(["hires_per_year", n])
    writer.writerow(["manual_avg_minutes_per_hire", round(manual_avg, 1)])
    writer.writerow(["automated_avg_minutes_per_hire", round(auto_avg, 1)])
    writer.writerow(["minutes_saved_per_hire", round(minutes_saved_per_hire, 1)])
    writer.writerow(["manual_group_miss_rate_pct", round(manual_group_miss_rate * 100, 1)])
    writer.writerow(["manual_vpn_miss_rate_pct", round(manual_vpn_miss_rate * 100, 1)])
    writer.writerow(["annual_rework_incidents", annual_rework_incidents])
    writer.writerow(["annual_handson_hours_manual", round(annual_handson_hours_manual, 1)])
    writer.writerow(["annual_handson_hours_automated", round(annual_handson_hours_auto, 1)])
    writer.writerow(["annual_hours_saved_total", round(annual_hours_saved, 1)])
    writer.writerow(["annual_dollar_saved", round(annual_dollar_saved, 0)])

print("\nWrote data/raw/onboarding_comparison_summary.csv")
