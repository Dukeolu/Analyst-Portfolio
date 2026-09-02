"""
Case 03 -- Step 1: generate the raw budget-vs-actual dataset.

Real budget/actual P&L data by region and category is about as
commercially sensitive as it gets, so -- as in Cases 01 and 02 -- this
simulates it instead. Two deliberate variance drivers are seeded into an
otherwise-on-plan business (see lib_finance_sim.py): a ramping supplier
cost overrun in Electronics Accessories (import-heavy, echoing the long
variable lead times in Case 01), and discount creep in Outdoor & Sporting
in two competitive regions. Everything else moves with ordinary noise
around budget.

Output: data/raw/budget_vs_actual.csv (576 rows: 4 regions x 6 categories
x 24 months).
"""
from pathlib import Path
from lib_finance_sim import build_budget, simulate_actuals

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

budget = build_budget(seed=3)
df = simulate_actuals(budget, seed=29)
df.to_csv(OUT_DIR / "budget_vs_actual.csv", index=False)

print(f"rows: {len(df):,}")
total_budget_profit = df["budget_profit"].sum()
total_actual_profit = df["actual_profit"].sum()
print(f"total budget profit (24mo): ${total_budget_profit:,.0f}")
print(f"total actual profit (24mo): ${total_actual_profit:,.0f}")
print(f"total variance: ${total_actual_profit - total_budget_profit:,.0f}")
print("\nworst 5 region x category combos by total variance:")
worst = df.groupby(["category", "region"])["profit_variance"].sum().sort_values().head(5)
print(worst.round(0))
