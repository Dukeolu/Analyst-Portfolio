"""
Shared simulation library for Case 01 (Operations & Supply Chain).

Generates a synthetic-but-realistic 2-year weekly demand history for a
mid-size distributor, then simulates a periodic-review inventory policy
(reorder point + fixed order quantity) so that stockouts and excess
inventory emerge naturally from policy choices rather than being
hand-scripted. Used by both the data-generation step (status-quo policy)
and the recommendation step (safety-stock-based policy), so the two runs
are directly comparable on the same underlying demand.
"""
import numpy as np
import pandas as pd

N_WEEKS = 104  # 2 years
START_DATE = pd.Timestamp("2024-01-07")  # first week-ending Sunday
REGIONS = ["Northeast", "Midwest", "South", "West"]
HOLDING_RATE_ANNUAL = 0.22  # inventory carrying cost, % of unit cost per year
SERVICE_Z = 1.645  # z-score for a 95% cycle service level

CATEGORIES = {
    # category: (base_weekly_demand_range, unit_cost_range, margin_range,
    #            lead_time_days_mean, lead_time_days_std, n_skus)
    "Electronics Accessories": ((20, 220), (6, 40), (0.30, 0.42), 42, 12, 34),
    "Home & Kitchen":          ((15, 160), (8, 55), (0.35, 0.50), 28, 8,  32),
    "Office Supplies":         ((30, 300), (2, 18), (0.40, 0.55), 10, 3,  30),
    "Personal Care":           ((25, 240), (3, 22), (0.38, 0.52), 18, 5,  28),
    "Outdoor & Sporting":      ((10, 120), (10, 70), (0.32, 0.46), 35, 10, 28),
    "Pet Supplies":            ((15, 150), (5, 35), (0.36, 0.48), 21, 6,  28),
}

SEASONAL_FACTOR = {
    1: 0.88, 2: 0.85, 3: 0.92, 4: 0.97, 5: 1.00, 6: 1.02,
    7: 1.00, 8: 1.03, 9: 1.05, 10: 1.12, 11: 1.35, 12: 1.28,
}


def build_sku_master(seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    sku_n = 1
    for cat, (dmd_rng, cost_rng, margin_rng, lt_mean, lt_std, n_skus) in CATEGORIES.items():
        # Pareto-style skew: most SKUs are low-volume, a few are runaway sellers
        volume_shape = rng.pareto(a=1.8, size=n_skus) + 1
        volume_shape = volume_shape / volume_shape.max()
        for i in range(n_skus):
            base_demand = dmd_rng[0] + volume_shape[i] * (dmd_rng[1] - dmd_rng[0])
            unit_cost = round(rng.uniform(*cost_rng), 2)
            margin = rng.uniform(*margin_rng)
            unit_price = round(unit_cost / (1 - margin), 2)
            # demand volatility: high-volume "hit" SKUs are often *more* volatile
            # (promotions, seasonality spikes), not less -- this is the trap.
            demand_cv = float(np.clip(rng.normal(0.35 + 0.35 * volume_shape[i], 0.12), 0.15, 1.3))
            lead_time_days = max(5, rng.normal(lt_mean, lt_std * 0.4))
            lead_time_std_days = max(1.5, rng.normal(lt_std, lt_std * 0.3))
            rows.append({
                "sku": f"SKU-{sku_n:04d}",
                "category": cat,
                "unit_cost": unit_cost,
                "unit_price": unit_price,
                "base_weekly_demand": round(base_demand, 1),
                "demand_cv": round(demand_cv, 3),
                "lead_time_days_mean": round(lead_time_days, 1),
                "lead_time_days_std": round(lead_time_std_days, 1),
            })
            sku_n += 1
    return pd.DataFrame(rows)


def generate_weekly_demand(sku_master: pd.DataFrame, seed: int = 11) -> pd.DataFrame:
    """Long-format weekly demand per SKU: columns [week, sku, demand]."""
    rng = np.random.default_rng(seed)
    weeks = pd.date_range(START_DATE, periods=N_WEEKS, freq="W-SUN")
    records = []
    for _, sku_row in sku_master.iterrows():
        base = sku_row["base_weekly_demand"]
        cv = sku_row["demand_cv"]
        sigma = np.sqrt(np.log(1 + cv**2))
        mu = np.log(base) - sigma**2 / 2
        for wk in weeks:
            seasonal = SEASONAL_FACTOR[wk.month]
            demand = rng.lognormal(mean=mu, sigma=sigma) * seasonal
            records.append((wk, sku_row["sku"], max(0, round(demand))))
    return pd.DataFrame(records, columns=["week", "sku", "demand"])


def simulate_inventory(sku_master: pd.DataFrame, demand_df: pd.DataFrame,
                        reorder_points: dict, order_weeks_cover: float = 4.0,
                        starting_cover_weeks: float = 3.0, seed: int = 23) -> pd.DataFrame:
    """
    Periodic-review (weekly) simulation of a reorder-point policy.
    order_weeks_cover: each replenishment order covers this many weeks of
    average demand (kept constant across policy scenarios, so only the
    *reorder point* -- i.e. how early you trigger -- differs between runs).
    Returns a long panel: week, sku, demand, fulfilled, on_hand_end, stockout.
    """
    rng = np.random.default_rng(seed)
    demand_wide = demand_df.pivot(index="sku", columns="week", values="demand")
    weeks = list(demand_wide.columns)
    panel_rows = []

    for _, sku_row in sku_master.iterrows():
        sku = sku_row["sku"]
        rp = reorder_points[sku]
        order_qty = max(1, sku_row["base_weekly_demand"] * order_weeks_cover)
        lt_mean_wk = sku_row["lead_time_days_mean"] / 7
        lt_std_wk = sku_row["lead_time_days_std"] / 7

        on_hand = order_qty + rp  # reasonable starting stock
        pipeline = {}  # arrival_week_index -> qty
        for wi, wk in enumerate(weeks):
            # receive anything arriving this week
            arriving = pipeline.pop(wi, 0)
            on_hand += arriving

            demand = demand_wide.loc[sku, wk]
            fulfilled = min(demand, on_hand)
            stockout = fulfilled < demand
            on_hand -= fulfilled

            # inventory position = on_hand + everything still in the pipeline
            position = on_hand + sum(pipeline.values())
            if position <= rp:
                lt_weeks = max(1, round(rng.normal(lt_mean_wk, lt_std_wk)))
                arrival_wi = wi + lt_weeks
                pipeline[arrival_wi] = pipeline.get(arrival_wi, 0) + order_qty

            panel_rows.append((wk, sku, demand, fulfilled, on_hand, stockout))

    return pd.DataFrame(panel_rows, columns=["week", "sku", "demand", "fulfilled", "on_hand_end", "stockout"])
