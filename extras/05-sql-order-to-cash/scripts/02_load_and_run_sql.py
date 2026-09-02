"""Extra 05 -- Step 2: load into SQLite, run every analysis query, save results."""
import sqlite3
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SQL = BASE / "sql"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
DB_PATH = OUT / "o2c.db"

DB_PATH.unlink(missing_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.executescript((SQL / "01_schema.sql").read_text())

for tbl in ["customers", "orders", "invoices", "payments"]:
    pd.read_csv(RAW / f"{tbl}.csv").to_sql(tbl, conn, if_exists="append", index=False)
conn.commit()

queries = {
    "dso_by_segment_trend": "02_dso_by_segment_trend.sql",
    "ar_aging_snapshot": "03_ar_aging_snapshot.sql",
    "smb_high_risk_concentration": "05_smb_high_risk_concentration.sql",
    "cumulative_collections_vs_target": "06_cumulative_collections_vs_target.sql",
}
for out_name, sql_file in queries.items():
    d = pd.read_sql(SQL.joinpath(sql_file).read_text(), conn)
    d.to_csv(OUT / f"{out_name}.csv", index=False)
    print(f"{sql_file:38s} -> {out_name}.csv  ({len(d):,} rows)")

# 04 has two statements (a comment + the ranked query); run just the query
late_drivers_sql = "\n".join(
    l for l in (SQL / "04_late_payment_drivers.sql").read_text().splitlines()
    if not l.strip().startswith("--")
)
late = pd.read_sql(late_drivers_sql, conn)
late.to_csv(OUT / "late_payment_drivers.csv", index=False)
print(f"{'04_late_payment_drivers.sql':38s} -> late_payment_drivers.csv  ({len(late):,} rows)")

print("\n--- late payment drivers: segment vs risk tier ---")
print(late.to_string(index=False))

print("\n--- SMB x High-risk concentration ---")
print(pd.read_csv(OUT / "smb_high_risk_concentration.csv").to_string(index=False))

conn.close()
print(f"\nSQLite DB written to {DB_PATH.relative_to(BASE)}")
