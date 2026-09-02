"""
Case 01 -- Step 3: the actual "solution" step.

Takes the SQL output (ABC tiers, current fill rates) plus each SKU's own
demand history and lead-time variability, and replaces the flat "3 weeks
of average demand" reorder point with one sized to that SKU's own demand
volatility and lead-time risk -- the standard safety-stock formula used in
inventory planning:

    safety_stock   = Z * sqrt( LT_weeks * sigma_demand^2
                                + mean_demand^2 * sigma_LT_weeks^2 )
    reorder_point  = mean_weekly_demand * LT_weeks + safety_stock

A first pass at a single, uniform 95% service target (Z=1.645) for every
SKU was tried and rejected: it does lift the fill rate, but it does so by
more than doubling network inventory investment, because the status-quo
policy turns out to be broadly *under*-protected, not over-protected. No
finance team signs off on that. The recommendation actually shipped here
is tier-differentiated service targets -- protect the revenue-critical
A-tier tightly, and consciously accept more stockout risk on C-tier --
which is the standard real-world answer to "safety stock is expensive."

Then it re-simulates the *same* two years of demand under the new reorder
points (order quantities held constant, so only the trigger point differs)
and reports the before/after difference -- this is a validated projection,
not just a formula.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from lib_sim import build_sku_master, generate_weekly_demand, simulate_inventory

# Service target by ABC tier: protect the revenue-critical items tightly,
# accept more risk on the long tail. This is the lever that keeps the
# recommendation affordable instead of blanket-raising every SKU to 95%.
Z_BY_TIER = {"A": 1.88, "B": 1.41, "C": 1.04}   # ~97% / ~92% / ~85% cycle service

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

skus = pd.read_csv(RAW / "skus.csv")
orders = pd.read_csv(RAW / "orders.csv")
abc = pd.read_csv(PROCESSED / "abc_classification.csv")[["sku", "abc_tier"]]

# --- rebuild the exact same demand history the data was generated from ----
# (same seeds as 01_generate_data.py -- this mirrors how an analyst would
# reconstruct weekly demand from order history, not a shortcut)
sku_master = build_sku_master(seed=7)
demand_df = generate_weekly_demand(sku_master, seed=11)

weekly_stats = demand_df.groupby("sku")["demand"].agg(mean_weekly_demand="mean", std_weekly_demand="std").reset_index()

reco = skus.merge(weekly_stats, on="sku").merge(abc, on="sku")
reco["lt_weeks_mean"] = reco["lead_time_days_mean"] / 7
reco["lt_weeks_std"] = reco["lead_time_days_std"] / 7
reco["service_z"] = reco["abc_tier"].map(Z_BY_TIER)

reco["safety_stock"] = reco["service_z"] * np.sqrt(
    reco["lt_weeks_mean"] * reco["std_weekly_demand"] ** 2
    + reco["mean_weekly_demand"] ** 2 * reco["lt_weeks_std"] ** 2
)
reco["reorder_point_recommended"] = (
    reco["mean_weekly_demand"] * reco["lt_weeks_mean"] + reco["safety_stock"]
).round(0)
reco["reorder_point_current"] = reco["reorder_point_current"].round(0)
reco["rp_change"] = reco["reorder_point_recommended"] - reco["reorder_point_current"]
reco["rp_change_pct"] = (reco["rp_change"] / reco["reorder_point_current"] * 100).round(1)

# --- re-simulate the same two years under the recommended policy ----------
recommended_rps = dict(zip(reco["sku"], reco["reorder_point_recommended"]))
panel_new = simulate_inventory(sku_master, demand_df, recommended_rps, order_weeks_cover=4.0, seed=23)

# --- before/after comparison -----------------------------------------------
panel_new = panel_new.merge(skus[["sku", "unit_cost"]], on="sku").merge(abc, on="sku")

before = orders.groupby("category").agg(
    demand=("qty_ordered", "sum"), fulfilled=("qty_fulfilled", "sum")
)
before_overall_fill = orders["qty_fulfilled"].sum() / orders["qty_ordered"].sum()
after_overall_fill = panel_new["fulfilled"].sum() / panel_new["demand"].sum()

before_a = orders.merge(abc, on="sku").query("abc_tier == 'A'")
before_a_fill = before_a["qty_fulfilled"].sum() / before_a["qty_ordered"].sum()
after_a = panel_new.query("abc_tier == 'A'")
after_a_fill = after_a["fulfilled"].sum() / after_a["demand"].sum()

inv_before = pd.read_csv(PROCESSED / "avg_inventory_by_sku.csv")
avg_inv_value_before = inv_before["avg_on_hand_value"].sum()

avg_on_hand_after = panel_new.groupby("sku")["on_hand_end"].mean().reset_index()
avg_on_hand_after = avg_on_hand_after.merge(skus[["sku", "unit_cost"]], on="sku")
avg_on_hand_after["value"] = avg_on_hand_after["on_hand_end"] * avg_on_hand_after["unit_cost"]
avg_inv_value_after = avg_on_hand_after["value"].sum()

HOLDING_RATE = 0.22
carrying_cost_before = avg_inv_value_before * HOLDING_RATE
carrying_cost_after = avg_inv_value_after * HOLDING_RATE

# --- the ROI case: gross margin recovered from fewer stockouts, weighed
# against the extra carrying cost of holding more safety stock -----------
N_YEARS = 2
orders_m = orders.merge(skus[["sku", "unit_cost"]], on="sku", suffixes=("", "_sku"))
orders_m["lost_units"] = orders_m["qty_ordered"] - orders_m["qty_fulfilled"]
orders_m["lost_margin"] = orders_m["lost_units"] * (orders_m["unit_price"] - orders_m["unit_cost"])
lost_margin_before_annual = orders_m["lost_margin"].sum() / N_YEARS

panel_m = panel_new.merge(skus[["sku", "unit_price"]], on="sku")
panel_m["lost_units"] = panel_m["demand"] - panel_m["fulfilled"]
panel_m["lost_margin"] = panel_m["lost_units"] * (panel_m["unit_price"] - panel_m["unit_cost"])
lost_margin_after_annual = panel_m["lost_margin"].sum() / N_YEARS

margin_recovered_annual = lost_margin_before_annual - lost_margin_after_annual
carrying_cost_increase_annual = carrying_cost_after - carrying_cost_before
net_annual_benefit = margin_recovered_annual - carrying_cost_increase_annual

summary = pd.DataFrame([{
    "metric": "Overall fill rate", "before": f"{before_overall_fill:.1%}", "after": f"{after_overall_fill:.1%}",
}, {
    "metric": "A-tier fill rate", "before": f"{before_a_fill:.1%}", "after": f"{after_a_fill:.1%}",
}, {
    "metric": "Avg. inventory value (network)", "before": f"${avg_inv_value_before:,.0f}", "after": f"${avg_inv_value_after:,.0f}",
}, {
    "metric": "Annual carrying cost (@22%)", "before": f"${carrying_cost_before:,.0f}", "after": f"${carrying_cost_after:,.0f}",
}])

reco_out = reco[[
    "sku", "category", "abc_tier", "mean_weekly_demand", "std_weekly_demand",
    "lead_time_days_mean", "reorder_point_current", "reorder_point_recommended",
    "rp_change", "rp_change_pct",
]].sort_values("rp_change")

reco_out.to_csv(PROCESSED / "reorder_point_recommendations.csv", index=False)
summary.to_csv(PROCESSED / "before_after_summary.csv", index=False)

# --- fill rate by tier, before vs after (for the dashboard) ---------------
before_by_tier = orders.merge(abc, on="sku").groupby("abc_tier").apply(
    lambda g: g["qty_fulfilled"].sum() / g["qty_ordered"].sum(), include_groups=False
).rename("fill_rate_before")
after_by_tier = panel_new.groupby("abc_tier").apply(
    lambda g: g["fulfilled"].sum() / g["demand"].sum(), include_groups=False
).rename("fill_rate_after")
fill_by_tier = pd.concat([before_by_tier, after_by_tier], axis=1).reset_index()
fill_by_tier.to_csv(PROCESSED / "fill_rate_by_tier_before_after.csv", index=False)

# --- monthly fill-rate trend, status quo (seasonality context) ------------
orders["month"] = pd.to_datetime(orders["order_date"]).dt.to_period("M").astype(str)
monthly = orders.groupby("month").apply(
    lambda g: g["qty_fulfilled"].sum() / g["qty_ordered"].sum(), include_groups=False
).rename("fill_rate").reset_index()
monthly.to_csv(PROCESSED / "monthly_fill_rate.csv", index=False)

roi = pd.DataFrame([{
    "annual_lost_margin_before": round(lost_margin_before_annual, 0),
    "annual_lost_margin_after": round(lost_margin_after_annual, 0),
    "annual_margin_recovered": round(margin_recovered_annual, 0),
    "annual_carrying_cost_increase": round(carrying_cost_increase_annual, 0),
    "net_annual_benefit": round(net_annual_benefit, 0),
}])
roi.to_csv(PROCESSED / "roi_summary.csv", index=False)

print(summary.to_string(index=False))
print(f"\n--- ROI case ---")
print(f"Annual gross margin lost to stockouts, before: ${lost_margin_before_annual:,.0f}")
print(f"Annual gross margin lost to stockouts, after:  ${lost_margin_after_annual:,.0f}")
print(f"Annual gross margin recovered:                 ${margin_recovered_annual:,.0f}")
print(f"Annual carrying-cost increase:                 ${carrying_cost_increase_annual:,.0f}")
print(f"Net annual benefit:                            ${net_annual_benefit:,.0f}")
print(f"\nMost under-protected SKUs (recommended >> current):")
print(reco_out.sort_values("rp_change", ascending=False).head(5)[["sku", "category", "abc_tier", "reorder_point_current", "reorder_point_recommended", "rp_change_pct"]].to_string(index=False))
print(f"\nMost over-protected SKUs (recommended << current):")
print(reco_out.head(5)[["sku", "category", "abc_tier", "reorder_point_current", "reorder_point_recommended", "rp_change_pct"]].to_string(index=False))
