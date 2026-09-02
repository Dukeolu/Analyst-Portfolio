"""
Case 04 -- Step 2: derive monthly hires/terminations by department from
the employee-level data, for the headcount roll-forward (Excel and SQL
both consume this).
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

emp = pd.read_csv(RAW / "employees.csv")
emp["hire_period"] = pd.PeriodIndex(emp["hire_month"], freq="M")
emp["term_period"] = emp.apply(
    lambda r: r["hire_period"] + int(r["tenure_months"]) if r["terminated_voluntary"] == "Yes" else pd.NaT, axis=1
)

months = pd.period_range("2024-01", periods=24, freq="M")
departments = sorted(emp["department"].unique())

rows = []
for dept in departments:
    e = emp[emp.department == dept]
    for m in months:
        hires = (e["hire_period"] == m).sum()
        terms = (e["term_period"] == m).sum()
        rows.append({"month": str(m), "department": dept, "hires": int(hires), "terminations": int(terms)})

df = pd.DataFrame(rows)
df.to_csv(OUT / "monthly_headcount_by_dept.csv", index=False)
print(f"monthly_headcount_by_dept: {len(df):,} rows")
print(df.groupby("department")[["hires", "terminations"]].sum())
