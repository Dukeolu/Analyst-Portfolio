"""
Case 01 -- Step 1: generate the raw dataset the analysis starts from.

Simulates two years of weekly order and inventory data for a distributor
running a naive, flat "N weeks of average demand" reorder-point policy --
the status quo this case study is investigating. Real inventory-level data
this granular is almost never published openly (it's commercially
sensitive), so this project simulates it with realistic structure instead:
Pareto-skewed SKU volume, demand volatility that scales with popularity,
category-specific lead times, and holiday seasonality.

Outputs (data/raw/):
  skus.csv                SKU master (category, cost, price, current policy)
  orders.csv              Weekly order lines by SKU x region
  inventory_snapshots.csv Weekly on-hand inventory by SKU
"""
import numpy as np
import pandas as pd
from pathlib import Path
from lib_sim import build_sku_master, generate_weekly_demand, simulate_inventory, REGIONS

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sku_master = build_sku_master(seed=7)
demand_df = generate_weekly_demand(sku_master, seed=11)

# --- status-quo policy: a flat "3 weeks of average demand" reorder point,
# set the same way regardless of how volatile that SKU's demand actually is.
sku_master["reorder_point_current"] = (sku_master["base_weekly_demand"] * 3).round(0)
reorder_points = dict(zip(sku_master["sku"], sku_master["reorder_point_current"]))

panel = simulate_inventory(sku_master, demand_df, reorder_points, order_weeks_cover=4.0, seed=23)

# --- explode weekly SKU demand into SKU x region order lines ---------------
rng = np.random.default_rng(31)
region_weights = {
    sku: rng.dirichlet(np.ones(len(REGIONS)) * rng.uniform(0.8, 3.0))
    for sku in sku_master["sku"]
}

panel = panel.merge(sku_master[["sku", "category", "unit_cost", "unit_price"]], on="sku")

order_rows = []
order_id = 100000
for row in panel.itertuples(index=False):
    weights = region_weights[row.sku]
    fill_rate = (row.fulfilled / row.demand) if row.demand > 0 else 1.0
    for region, w in zip(REGIONS, weights):
        qty_ordered = row.demand * w
        if qty_ordered < 0.5:
            continue
        qty_fulfilled = qty_ordered * fill_rate
        order_id += 1
        order_rows.append((
            order_id, row.week.date().isoformat(), row.sku, row.category, region,
            round(qty_ordered), round(qty_fulfilled),
            row.unit_cost, row.unit_price,
        ))

orders = pd.DataFrame(order_rows, columns=[
    "order_id", "order_date", "sku", "category", "region",
    "qty_ordered", "qty_fulfilled", "unit_cost", "unit_price",
])
orders["revenue"] = (orders["qty_fulfilled"] * orders["unit_price"]).round(2)

inventory_snapshots = panel.merge(
    sku_master[["sku", "reorder_point_current"]], on="sku"
)[["week", "sku", "on_hand_end", "reorder_point_current"]].rename(
    columns={"week": "week_ending", "on_hand_end": "on_hand_qty"}
)
inventory_snapshots["week_ending"] = inventory_snapshots["week_ending"].dt.date.astype(str)
inventory_snapshots["on_hand_qty"] = inventory_snapshots["on_hand_qty"].round(1)

sku_master.to_csv(OUT_DIR / "skus.csv", index=False)
orders.to_csv(OUT_DIR / "orders.csv", index=False)
inventory_snapshots.to_csv(OUT_DIR / "inventory_snapshots.csv", index=False)

print(f"skus:                {len(sku_master):,} rows")
print(f"orders:               {len(orders):,} rows")
print(f"inventory_snapshots:  {len(inventory_snapshots):,} rows")
print(f"date range: {orders['order_date'].min()} .. {orders['order_date'].max()}")
overall_fill_rate = orders["qty_fulfilled"].sum() / orders["qty_ordered"].sum()
print(f"overall network fill rate (status quo): {overall_fill_rate:.1%}")
