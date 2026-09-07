"""
Generates simulated new-hire onboarding data for Meridian Manufacturing —
one year of new-hire volume, run twice: once through the historical manual
process, once through the new automated script, so the comparison is
apples-to-apples on the same hire population.

Deliberately seeded findings:
  - The manual process's error-prone step is department/role security-group
    assignment (easy to fat-finger or forget one of 2-4 groups by hand) and,
    for remote-eligible hires, VPN group provisioning specifically.
  - The automated script is driven by a lookup table, not memory, so those
    error rates go to 0% by construction — the honest claim is "structural
    elimination of a manual-entry error," not "the script is smarter."
"""
import csv
import random

random.seed(7)

DEPARTMENTS = ["Warehouse & Ops", "Office/Admin", "Sales", "Finance", "IT", "HR", "Engineering"]
ROLES_BY_DEPT = {
    "Warehouse & Ops": ["Warehouse Associate", "Forklift Operator", "Shift Supervisor"],
    "Office/Admin": ["Administrative Assistant", "Office Coordinator"],
    "Sales": ["Account Executive", "Sales Coordinator"],
    "Finance": ["AP Clerk", "Financial Analyst"],
    "IT": ["Help Desk Technician", "Systems Administrator"],
    "HR": ["HR Generalist", "Recruiter"],
    "Engineering": ["Manufacturing Engineer", "QA Technician"],
}
# Ground-truth group requirements per department — this is the lookup table
# the automated script reads from directly (src/onboarding_automation.ps1's $groupMap).
REQUIRED_GROUPS = {
    "Warehouse & Ops": ["GRP-WMS-Users", "GRP-Warehouse-Floor", "GRP-Timeclock"],
    "Office/Admin": ["GRP-Office365-Standard", "GRP-SharedDrive-Admin"],
    "Sales": ["GRP-CRM-Users", "GRP-Office365-Standard", "GRP-SharedDrive-Sales"],
    "Finance": ["GRP-ERP-Finance", "GRP-Office365-Standard", "GRP-SharedDrive-Finance"],
    "IT": ["GRP-Office365-Standard", "GRP-IT-Admins", "GRP-VPN-Standard"],
    "HR": ["GRP-HRIS-Users", "GRP-Office365-Standard", "GRP-SharedDrive-HR-Restricted"],
    "Engineering": ["GRP-PLM-Users", "GRP-Office365-Standard", "GRP-SharedDrive-Engineering"],
}
REMOTE_ELIGIBLE_ROLES = {"Financial Analyst", "Account Executive", "Systems Administrator",
                          "HR Generalist", "Recruiter", "Manufacturing Engineer", "Sales Coordinator"}

N_HIRES = 148  # disclosed annual new-hire volume assumption for a ~650-employee manufacturer

hires = []
for i in range(1, N_HIRES + 1):
    dept = random.choices(
        DEPARTMENTS, weights=[30, 12, 14, 10, 6, 8, 20], k=1
    )[0]
    role = random.choice(ROLES_BY_DEPT[dept])
    remote_eligible = role in REMOTE_ELIGIBLE_ROLES and random.random() < 0.7
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hires.append({
        "hire_id": f"NH-{i:04d}",
        "start_date": f"2025-{month:02d}-{day:02d}",
        "department": dept,
        "role": role,
        "remote_eligible": "Y" if remote_eligible else "N",
        "required_group_count": len(REQUIRED_GROUPS[dept]) + (1 if remote_eligible else 0),
    })

hires.sort(key=lambda h: h["start_date"])
with open("data/raw/new_hires.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(hires[0].keys()))
    writer.writeheader()
    writer.writerows(hires)

# --- Manual process log (historical, pre-automation) -----------------------
# Per-step hands-on-keyboard time in minutes, each drawn from a realistic
# distribution; the group-assignment and VPN steps also get a chance of
# being incomplete (the deliberately seeded error mode).
manual_rows = []
for h in hires:
    remote = h["remote_eligible"] == "Y"
    t_account = max(2.0, random.gauss(5.0, 1.2))
    t_groups = max(3.0, random.gauss(8.0, 2.5))
    # groups_complete: manual entry from memory/a printed cheat-sheet, ~15% miss at least one group
    groups_complete = random.random() > 0.15
    t_home_dir = max(1.5, random.gauss(4.0, 1.0))
    t_mailbox = max(2.0, random.gauss(6.0, 1.5))
    if remote:
        t_vpn = max(1.0, random.gauss(3.0, 1.0))
        vpn_day1 = random.random() > 0.22  # ~22% of remote-eligible hires historically missed VPN on day 1
    else:
        t_vpn = 0.0
        vpn_day1 = True  # not applicable, doesn't count against the rate
    t_welcome_email = max(1.5, random.gauss(3.0, 0.8))
    t_ticket_logging = max(1.0, random.gauss(2.0, 0.5))
    total = t_account + t_groups + t_home_dir + t_mailbox + t_vpn + t_welcome_email + t_ticket_logging
    manual_rows.append({
        "hire_id": h["hire_id"],
        "handson_minutes_account": round(t_account, 1),
        "handson_minutes_groups": round(t_groups, 1),
        "handson_minutes_home_dir": round(t_home_dir, 1),
        "handson_minutes_mailbox": round(t_mailbox, 1),
        "handson_minutes_vpn": round(t_vpn, 1),
        "handson_minutes_welcome_email": round(t_welcome_email, 1),
        "handson_minutes_ticket_logging": round(t_ticket_logging, 1),
        "total_handson_minutes": round(total, 1),
        "all_required_groups_assigned_first_try": "Y" if groups_complete else "N",
        "vpn_ready_day1": "Y" if (not remote or vpn_day1) else "N",
        "remote_eligible": h["remote_eligible"],
    })

with open("data/raw/manual_onboarding_log.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(manual_rows[0].keys()))
    writer.writeheader()
    writer.writerows(manual_rows)

# --- Automated process log --------------------------------------------------
# Hands-on time is now just: run the script, watch it complete, review the
# output report. Groups and VPN are always correct because they're read from
# the same lookup table every time — not a smarter script, a structural fix.
automated_rows = []
for h in hires:
    t_run_script = max(0.5, random.gauss(1.2, 0.3))     # launching it + entering the CSV path
    t_review_report = max(0.5, random.gauss(1.5, 0.4))  # reading the completion report, confirming no errors
    total = t_run_script + t_review_report
    automated_rows.append({
        "hire_id": h["hire_id"],
        "handson_minutes_run_script": round(t_run_script, 1),
        "handson_minutes_review_report": round(t_review_report, 1),
        "total_handson_minutes": round(total, 1),
        "all_required_groups_assigned_first_try": "Y",   # by construction — lookup-table driven
        "vpn_ready_day1": "Y",                            # by construction
        "remote_eligible": h["remote_eligible"],
    })

with open("data/raw/automated_onboarding_log.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(automated_rows[0].keys()))
    writer.writeheader()
    writer.writerows(automated_rows)

print(f"Wrote {len(hires)} new-hire records, manual log, and automated log.")
manual_miss_rate = sum(1 for r in manual_rows if r["all_required_groups_assigned_first_try"] == "N") / len(manual_rows)
remote_rows = [r for r in manual_rows if r["remote_eligible"] == "Y"]
vpn_miss_rate = sum(1 for r in remote_rows if r["vpn_ready_day1"] == "N") / len(remote_rows)
print(f"Manual group-assignment miss rate: {manual_miss_rate:.1%}")
print(f"Manual VPN-day1 miss rate (remote-eligible only, n={len(remote_rows)}): {vpn_miss_rate:.1%}")
