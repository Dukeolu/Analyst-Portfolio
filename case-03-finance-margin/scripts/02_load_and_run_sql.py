"""Case 03 -- Step 2: load budget_vs_actual.csv into SQLite and run the SQL analysis."""
import sqlite3
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SQL = BASE / "sql"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
DB_PATH = OUT / "case03.db"

DB_PATH.unlink(missing_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.executescript((SQL / "01_schema.sql").read_text())

pd.read_csv(RAW / "budget_vs_actual.csv").to_sql("budget_actuals", conn, if_exists="append", index=False)
conn.commit()

queries = {
    "variance_ranked": "02_variance_ranked.sql",
    "monthly_trend_worst_combos": "03_monthly_trend_worst_combos.sql",
}
for out_name, sql_file in queries.items():
    d = pd.read_sql(SQL.joinpath(sql_file).read_text(), conn)
    d.to_csv(OUT / f"{out_name}.csv", index=False)
    print(f"{sql_file:32s} -> {out_name}.csv  ({len(d):,} rows)")

print("\nvariance_ranked (worst 6):")
print(pd.read_csv(OUT / "variance_ranked.csv").head(6).to_string(index=False))
conn.close()
print(f"\nSQLite DB written to {DB_PATH.relative_to(BASE)}")
