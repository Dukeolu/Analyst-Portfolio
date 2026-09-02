"""
Case 03 -- Step 3: the actual "solution" step.

Decomposes total profit variance into three additive effects (volume,
discount, COGS -- same math as the Excel Margin Bridge, cross-checked
against it) and then answers the business question directly: if the four
worst combos had simply held their budgeted discount% and COGS% -- no
change in volume, no heroics, just staying on plan -- how much profit
comes back?
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

df = pd.read_csv(RAW / "budget_vs_actual.csv")
ranked = pd.read_csv(PROCESSED / "variance_ranked.csv")

# ---------------------------------------------------------------- network-wide bridge
df["volume_effect"] = (df["actual_revenue"] - df["budget_revenue"]) * (1 - df["budget_discount_pct"]) * (1 - df["budget_cogs_pct"])
df["discount_effect"] = df["actual_revenue"] * (df["budget_discount_pct"] - df["actual_discount_pct"]) * (1 - df["budget_cogs_pct"])
df["cogs_effect"] = df["actual_net_revenue"] * (df["budget_cogs_pct"] - df["actual_cogs_pct"])

bridge = pd.DataFrame([{
    "budget_profit": df["budget_profit"].sum(),
    "volume_effect": df["volume_effect"].sum(),
    "discount_effect": df["discount_effect"].sum(),
    "cogs_effect": df["cogs_effect"].sum(),
    "actual_profit": df["actual_profit"].sum(),
}])
bridge["check_sum_matches_actual"] = (
    bridge["budget_profit"] + bridge["volume_effect"] + bridge["discount_effect"] + bridge["cogs_effect"]
    - bridge["actual_profit"]
).round(2)
bridge.to_csv(PROCESSED / "margin_bridge.csv", index=False)

# ---------------------------------------------------------------- counterfactual: fix the top 4 leak combos
TOP_N = 4
worst = ranked.sort_values("variance").head(TOP_N)[["category", "region"]]

df_cf = df.merge(worst.assign(is_leak=True), on=["category", "region"], how="left")
df_cf["is_leak"] = df_cf["is_leak"].fillna(False)

# counterfactual: leak rows use BUDGET discount%/COGS% applied to ACTUAL revenue
# (i.e. "same sales, same effort -- just hold the line on price and cost discipline")
cf_discount = df_cf["budget_discount_pct"].where(df_cf["is_leak"], df_cf["actual_discount_pct"])
cf_cogs = df_cf["budget_cogs_pct"].where(df_cf["is_leak"], df_cf["actual_cogs_pct"])
cf_net_rev = df_cf["actual_revenue"] * (1 - cf_discount)
cf_profit = cf_net_rev - cf_net_rev * cf_cogs

actual_total = df_cf["actual_profit"].sum()
counterfactual_total = cf_profit.sum()
recovered_annual = (counterfactual_total - actual_total) / 2  # 24mo data -> annualize

leak_detail = worst.merge(
    ranked[["category", "region", "variance", "variance_pct"]], on=["category", "region"]
)

summary = pd.DataFrame([{
    "combos_fixed": TOP_N,
    "share_of_total_leak_addressed_pct": round(100 * abs(leak_detail["variance"].sum()) / abs(ranked[ranked.variance < 0]["variance"].sum()), 1),
    "actual_profit_24mo": round(actual_total, 0),
    "counterfactual_profit_24mo": round(counterfactual_total, 0),
    "profit_recovered_24mo": round(counterfactual_total - actual_total, 0),
    "profit_recovered_annualized": round(recovered_annual, 0),
}])
summary.to_csv(PROCESSED / "recovery_scenario.csv", index=False)

print("Margin bridge (network-wide, 24mo):")
print(bridge.T)
print("\nRecovery scenario (fixing the top 4 leak combos):")
print(summary.T)
