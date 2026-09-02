"""Case 04 -- Step 3: load employees.csv and recruiting_funnel.csv into SQLite, run the SQL analysis."""
import sqlite3
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SQL = BASE / "sql"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
DB_PATH = OUT / "case04.db"

DB_PATH.unlink(missing_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.executescript((SQL / "01_schema.sql").read_text())

pd.read_csv(RAW / "employees.csv").to_sql("employees", conn, if_exists="append", index=False)
pd.read_csv(RAW / "recruiting_funnel.csv").to_sql("recruiting_funnel", conn, if_exists="append", index=False)
conn.commit()

queries = {
    "attrition_by_tenure_band": "02_attrition_by_tenure_band.sql",
    "department_risk_ranking": "03_department_risk_ranking.sql",
}
for out_name, sql_file in queries.items():
    d = pd.read_sql(SQL.joinpath(sql_file).read_text(), conn)
    d.to_csv(OUT / f"{out_name}.csv", index=False)
    print(f"{sql_file:32s} -> {out_name}.csv  ({len(d):,} rows)")

print("\ndepartment_risk_ranking:")
print(pd.read_csv(OUT / "department_risk_ranking.csv").to_string(index=False))
conn.close()
print(f"\nSQLite DB written to {DB_PATH.relative_to(BASE)}")
