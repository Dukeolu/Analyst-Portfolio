"""
Simulates a messy raw warehouse shipping log -- the kind of export a script
would actually have to pull and clean before it's usable, not a tidy
analysis-ready CSV. Deliberately includes: inconsistent status casing,
duplicate rows, missing warehouse values, mixed date-string formats, and a
few nonsensical unit values.

Seeded finding: warehouse "West-3" has a real on-time-rate drop in the
final week of the log (a scanner/system issue), which the weekly report
script is meant to catch and flag automatically.
"""
import numpy as np
import pandas as pd

RNG_SEED = 33
N_WEEKS = 10
WEEK_END_LATEST = pd.Timestamp("2026-08-30")  # a Sunday

WAREHOUSES = ["Northeast-1", "Midwest-2", "West-3", "South-4"]
CATEGORIES = ["Electronics", "Home Goods", "Apparel", "Outdoor", "Office Supplies"]
ORDERS_PER_DAY_MEAN = 140

STATUS_CASE_VARIANTS = {
    "Shipped": ["Shipped", "shipped", "SHIPPED", " Shipped"],
    "Delayed": ["Delayed", "delayed", "DELAYED"],
    "Cancelled": ["Cancelled", "cancelled", "Canceled"],
}


def _rand_status_str(rng, canonical):
    return rng.choice(STATUS_CASE_VARIANTS[canonical])


def _rand_date_str(rng, ts):
    # simulate two different upstream systems exporting dates differently
    if rng.random() < 0.5:
        return ts.strftime("%Y-%m-%d")
    return ts.strftime("%m/%d/%Y")


def build_raw_log(seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    start = WEEK_END_LATEST - pd.Timedelta(weeks=N_WEEKS) + pd.Timedelta(days=1)
    days = pd.date_range(start, WEEK_END_LATEST, freq="D")

    rows = []
    order_seq = 1
    for day in days:
        week_end = day + pd.Timedelta(days=(6 - day.weekday() if day.weekday() != 6 else 0))
        # normalize to the Sunday that closes this day's week
        week_end = day + pd.Timedelta(days=(6 - day.dayofweek))
        is_final_week = (WEEK_END_LATEST - week_end).days <= 0

        n_orders = int(rng.poisson(ORDERS_PER_DAY_MEAN))
        for _ in range(n_orders):
            warehouse = rng.choice(WAREHOUSES)
            category = rng.choice(CATEGORIES)
            units = int(rng.integers(1, 12))

            promised_ship = day + pd.Timedelta(days=int(rng.integers(1, 4)))

            # baseline delay behavior
            base_delay_p = 0.08
            if warehouse == "West-3" and is_final_week:
                base_delay_p = 0.42  # the seeded issue
            cancel_p = 0.015

            roll = rng.random()
            if roll < cancel_p:
                status = "Cancelled"
                actual_ship = pd.NaT
            elif roll < cancel_p + base_delay_p:
                status = "Delayed"
                # either still not shipped (NaT) or shipped late
                if rng.random() < 0.5:
                    actual_ship = pd.NaT
                else:
                    actual_ship = promised_ship + pd.Timedelta(days=int(rng.integers(1, 6)))
            else:
                status = "Shipped"
                actual_ship = promised_ship - pd.Timedelta(days=int(rng.integers(0, 2)))

            row = {
                "order_id": f"WO{order_seq:07d}",
                "warehouse": warehouse,
                "category": category,
                "order_date": _rand_date_str(rng, day),
                "promised_ship_date": _rand_date_str(rng, promised_ship),
                "actual_ship_date": _rand_date_str(rng, actual_ship) if pd.notna(actual_ship) else "",
                "status": _rand_status_str(rng, status),
                "units": units,
            }
            order_seq += 1
            rows.append(row)

            # inject occasional messiness: duplicate row, missing warehouse, bad units
            if rng.random() < 0.02:
                dup = dict(row)
                rows.append(dup)  # exact duplicate
            if rng.random() < 0.01:
                row2 = dict(row)
                row2["order_id"] = f"WO{order_seq:07d}"; order_seq += 1
                row2["warehouse"] = ""  # missing
                rows.append(row2)
            if rng.random() < 0.005:
                row3 = dict(row)
                row3["order_id"] = f"WO{order_seq:07d}"; order_seq += 1
                row3["units"] = -1  # bad data entry
                rows.append(row3)

    return pd.DataFrame(rows)
