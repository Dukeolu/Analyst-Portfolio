"""
Generates a simulated IT help desk ticket dataset for Meridian Manufacturing
(simulated, ~650-employee mid-size manufacturer with one central IT help desk).

The story this data is built to reveal: the help desk assigns every ticket to
"next available technician" (round robin) regardless of the technician's
specialty. Flat SLA targets exist by priority, but nobody has checked whether
resolution time actually depends on whether the assigned tech's specialty
matches the ticket's category. It does, heavily -- and it's the dominant
driver of both SLA breaches and reopened tickets, more than priority itself.

Two tables:
  - technicians.csv : 8 techs, each with 1-2 specialty categories
  - tickets.csv      : ~950 tickets over 26 weeks (weekdays only), each
                        assigned to a technician chosen uniformly at random
                        (simulating "next available", ignoring specialty)

Resolution hours are simulated directly as elapsed wall-clock hours from
ticket creation (not business-hours-adjusted) -- a stated simplification,
disclosed in data/README.md and the case README's Limitations section.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG = np.random.default_rng(7)

# ---------------------------------------------------------------- technicians
TECHNICIANS = [
    ("T01", "Aisha Bello",     ["Password Reset", "Account Access"]),
    ("T02", "Marcus Chen",     ["Email & Calendar", "Account Access"]),
    ("T03", "Priya Anand",     ["Hardware"]),
    ("T04", "Diego Ramirez",   ["Hardware", "Software Install"]),
    ("T05", "Lena Kowalski",   ["Network & VPN"]),
    ("T06", "Sam Okafor",      ["Network & VPN", "Software Install"]),
    ("T07", "Oksana Petrenko", ["Software Install"]),
    ("T08", "Femi Adeyemi",    ["Password Reset", "Email & Calendar"]),
]

techs_df = pd.DataFrame(TECHNICIANS, columns=["tech_id", "tech_name", "specialty_categories"])
techs_df["specialty_categories"] = techs_df["specialty_categories"].apply(lambda x: ";".join(x))
techs_df.to_csv("data/raw/technicians.csv", index=False)

tech_specialty_map = {row.tech_id: set(row.specialty_categories.split(";")) for row in techs_df.itertuples()}

# ---------------------------------------------------------------- categories
# base_hours: typical resolution time for a *specialty-matched* technician
# weekly_volume: average tickets per weekday for this category
CATEGORIES = {
    "Password Reset":   {"base_hours": 0.4,  "weekly_volume": 9.0},
    "Account Access":   {"base_hours": 1.3,  "weekly_volume": 6.0},
    "Email & Calendar": {"base_hours": 1.8,  "weekly_volume": 6.5},
    "Hardware":         {"base_hours": 3.6,  "weekly_volume": 5.0},
    "Software Install": {"base_hours": 5.5,  "weekly_volume": 4.5},
    "Network & VPN":    {"base_hours": 7.5,  "weekly_volume": 4.0},
}

PRIORITIES = ["Low", "Medium", "High", "Critical"]
PRIORITY_WEIGHTS = [0.30, 0.42, 0.20, 0.08]
SLA_TARGET_HOURS = {"Low": 48, "Medium": 24, "High": 8, "Critical": 4}
# priority does give a modest real speed-up when techs try to expedite --
# but it's small next to the specialty-mismatch penalty below
PRIORITY_SPEEDUP = {"Low": 1.00, "Medium": 1.00, "High": 0.85, "Critical": 0.70}

MISMATCH_MULTIPLIER = 2.15   # off-specialty tickets take ~2.15x longer
BASE_REOPEN_RATE = 0.045
MISMATCH_REOPEN_RATE = 0.12

START = datetime(2025, 3, 3)   # a Monday
N_WEEKS = 26

rows = []
ticket_num = 1
tech_ids = [t[0] for t in TECHNICIANS]

for week in range(N_WEEKS):
    week_start = START + timedelta(weeks=week)
    for category, spec in CATEGORIES.items():
        # Poisson ticket count for the week, spread across 5 weekdays
        n_this_week = RNG.poisson(spec["weekly_volume"])
        for _ in range(n_this_week):
            day_offset = RNG.integers(0, 5)
            created = week_start + timedelta(days=int(day_offset),
                                              hours=float(RNG.uniform(8, 17)))
            # Monday backlog effect: tickets created on Monday take a bit longer
            monday_effect = 1.15 if created.weekday() == 0 else 1.0

            priority = RNG.choice(PRIORITIES, p=PRIORITY_WEIGHTS)
            tech_id = RNG.choice(tech_ids)  # "next available" -- ignores specialty
            matched = category in tech_specialty_map[tech_id]

            base = spec["base_hours"]
            mult = 1.0 if matched else MISMATCH_MULTIPLIER
            speed = PRIORITY_SPEEDUP[priority]
            noise = RNG.lognormal(mean=0.0, sigma=0.35)

            resolution_hours = round(base * mult * speed * monday_effect * noise, 2)
            resolution_hours = max(resolution_hours, 0.1)

            resolved = created + timedelta(hours=resolution_hours)
            sla_target = SLA_TARGET_HOURS[priority]
            sla_breached = resolution_hours > sla_target

            reopen_p = MISMATCH_REOPEN_RATE if not matched else BASE_REOPEN_RATE
            reopened = bool(RNG.random() < reopen_p)

            rows.append({
                "ticket_id": f"HD-{ticket_num:05d}",
                "created_at": created.isoformat(timespec="minutes"),
                "category": category,
                "priority": priority,
                "assigned_tech_id": tech_id,
                "resolved_at": resolved.isoformat(timespec="minutes"),
                "resolution_hours": resolution_hours,
                "sla_target_hours": sla_target,
                "sla_breached": sla_breached,
                "reopened": reopened,
            })
            ticket_num += 1

tickets_df = pd.DataFrame(rows).sort_values("created_at").reset_index(drop=True)
tickets_df.to_csv("data/raw/tickets.csv", index=False)

print(f"Technicians: {len(techs_df)}")
print(f"Tickets: {len(tickets_df)}")
print(f"Date range: {tickets_df['created_at'].min()} to {tickets_df['created_at'].max()}")
print(f"Overall SLA compliance: {(1 - tickets_df['sla_breached'].mean()) * 100:.1f}%")
print(f"Overall reopen rate: {tickets_df['reopened'].mean() * 100:.1f}%")
print(tickets_df.groupby("category")["resolution_hours"].median().sort_values())
