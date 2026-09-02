"""
Case 04 -- Step 1: generate the raw datasets.

As in Cases 01-03, real recruiting-funnel and employee-level attrition
data is simulated rather than downloaded (commercially/personally
sensitive, and not available on this sandbox's network allowlist
anyway). Two deliberate mechanisms are seeded: a screening backlog that
specifically hits Warehouse & Ops' Job Board pipeline, and elevated
early-tenure attrition for Job Board hires network-wide (a fit/
expectations-setting effect). No demographic attributes are modeled --
see lib_hr_sim.py and the case README for exactly what drives risk here.

Outputs:
  data/raw/recruiting_funnel.csv   720 rows (6 dept x 5 channel x 24mo)
  data/raw/employees.csv           one row per hire, with attrition outcome
"""
from pathlib import Path
from lib_hr_sim import build_recruiting_funnel, build_employee_base, simulate_attrition

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

funnel = build_recruiting_funnel(seed=41)
funnel.to_csv(OUT_DIR / "recruiting_funnel.csv", index=False)

employees_base = build_employee_base(funnel, seed=43)
employees = simulate_attrition(employees_base, seed=47)
employees.to_csv(OUT_DIR / "employees.csv", index=False)

print(f"recruiting_funnel: {len(funnel):,} rows, {funnel['applied'].sum():,} total applications, {funnel['hired'].sum():,} total hires")
print(f"employees: {len(employees):,} rows")
print(f"overall voluntary attrition rate: {(employees['terminated_voluntary']=='Yes').mean():.1%}")
print("\nattrition by channel:")
print(employees.groupby("channel")["terminated_voluntary"].apply(lambda s: (s == "Yes").mean()).round(3).sort_values(ascending=False))
print("\nfunnel conversion, Warehouse & Ops x Job Board vs overall Job Board:")
wo = funnel[(funnel.department == "Warehouse & Ops") & (funnel.channel == "Job Board")]
jb = funnel[funnel.channel == "Job Board"]
print(f"  Warehouse & Ops x Job Board: screen->interview = {wo['interviewed'].sum()/wo['screened'].sum():.1%}")
print(f"  Job Board overall:          screen->interview = {jb['interviewed'].sum()/jb['screened'].sum():.1%}")
