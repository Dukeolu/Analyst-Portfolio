"""Case 02 -- Step 2: load customers.csv into SQLite and run the SQL analysis."""
import sqlite3
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SQL = BASE / "sql"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
DB_PATH = OUT / "case02.db"

DB_PATH.unlink(missing_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.executescript((SQL / "01_schema.sql").read_text())

pd.read_csv(RAW / "customers.csv").to_sql("customers", conn, if_exists="append", index=False)
conn.commit()

queries = {
    "churn_by_segment": "02_churn_by_segment.sql",
    "high_risk_segments": "03_high_risk_segments.sql",
}
for out_name, sql_file in queries.items():
    df = pd.read_sql(SQL.joinpath(sql_file).read_text(), conn)
    df.to_csv(OUT / f"{out_name}.csv", index=False)
    print(f"{sql_file:30s} -> {out_name}.csv  ({len(df):,} rows)")

print("\nhigh_risk_segments:")
print(pd.read_csv(OUT / "high_risk_segments.csv").to_string(index=False))
conn.close()
print(f"\nSQLite DB written to {DB_PATH.relative_to(BASE)}")
