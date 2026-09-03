"""
Simulates one month of observed AP invoice cycle-time data for Brightpath
Distribution (fictional mid-size distributor, ~120 invoices/month, current
FLAT approval policy: <$500 = Dept Mgr only; >=$500 = Dept Mgr + Finance Mgr
+ Controller, regardless of size).

This is the raw "time-in-stage" log a BA would pull from email timestamps /
the accounting system during process discovery. Output feeds the Excel
workbook's Invoice Sample sheet (which computes everything else via formulas).
"""
import numpy as np
import csv
from pathlib import Path

rng = np.random.default_rng(42)
N = 120
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(exist_ok=True)

VENDORS_RECURRING = [
    "Ashford Packaging Co.", "Cascade Freight Partners", "Delmar Industrial Supply",
    "Fenwick Paper Group", "Harlow Fasteners Inc.", "Ironclad Pallet Systems",
    "Junction Fleet Fuel", "Kestrel Office Solutions", "Lattice Warehouse Equip.",
    "Meridian Cleaning Supply", "Norwood Uniform Services", "Overton Safety Gear",
]
VENDORS_ONEOFF = [
    "Blackstone Facility Repair", "Compass IT Contractors", "Driftwood Signage Co.",
    "Elmhurst Consulting Group", "Granite Fleet Maintenance", "Hawthorne Legal Services",
    "Ivyview Marketing Agency", "Juniper Equipment Rental",
]
DEPTS = ["Warehouse Ops", "Fleet & Logistics", "Facilities", "Sales & Marketing", "IT", "Finance"]

rows = []
tier_draw = rng.random(N)
for i in range(N):
    inv_id = f"INV-{2031 + i}"
    is_recurring = rng.random() < 0.75
    vendor = rng.choice(VENDORS_RECURRING) if is_recurring else rng.choice(VENDORS_ONEOFF)
    dept = rng.choice(DEPTS)

    # amount drawn to land roughly in the target tier mix: 18/55/20/7
    r = tier_draw[i]
    if r < 0.18:
        amount = rng.uniform(80, 499)
    elif r < 0.73:
        amount = rng.uniform(500, 9999)
    elif r < 0.93:
        amount = rng.uniform(10000, 49999)
    else:
        amount = rng.uniform(50000, 120000)
    amount = round(amount, 2)

    terms = "2/10 Net 30" if rng.random() < 0.40 else "Net 30"

    entry_mean = 1.2 if is_recurring else 1.6
    days_entry = max(0.1, round(rng.normal(entry_mean, 0.35), 1))

    days_dept = max(0.2, round(rng.normal(4.1, 1.6), 1))

    if amount >= 500:
        days_finance = max(0.2, round(rng.normal(3.8, 1.5), 1))
        days_controller = max(0.2, round(rng.normal(4.0, 1.6), 1))
    else:
        days_finance = 0.0
        days_controller = 0.0

    days_payment = max(0.1, round(rng.normal(1.0, 0.3), 1))

    rows.append([
        inv_id, vendor, "Recurring" if is_recurring else "One-off", dept,
        amount, terms, days_entry, days_dept, days_finance, days_controller, days_payment
    ])

with open(OUT / "invoice_sample.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Invoice ID", "Vendor", "Vendor Type", "Department", "Amount",
                "Payment Terms", "Days: Data Entry", "Days: Dept Mgr Approval",
                "Days: Finance Mgr Approval", "Days: Controller Approval", "Days: Payment Processing"])
    w.writerows(rows)

print(f"Wrote {N} rows to {OUT / 'invoice_sample.csv'}")
