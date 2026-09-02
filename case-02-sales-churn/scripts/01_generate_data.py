"""
Case 02 -- Step 1: generate the raw dataset.

Real customer-level churn data this granular is proprietary, so -- as in
Case 01 -- this simulates it instead, with realistic structure: a
month-by-month churn hazard driven by contract type, tenure stage
(elevated risk in the first 3 months, renewal-date spikes for annual
contracts), engagement, support-ticket friction, autopay, and price,
rather than assigning churn labels directly.

Output: data/raw/customers.csv (one row per customer, cross-sectional --
the same shape as the classic telco churn dataset).
"""
from pathlib import Path
from lib_churn_sim import build_customer_base, simulate_churn

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

customers = build_customer_base(n=6000, seed=5)
result = simulate_churn(customers, seed=17)
result.to_csv(OUT_DIR / "customers.csv", index=False)

print(f"customers: {len(result):,} rows")
print(f"overall churn rate: {(result['churned'] == 'Yes').mean():.1%}")
print(result.groupby("contract_type")["churned"].apply(lambda s: (s == "Yes").mean()).round(3))
