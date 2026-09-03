"""Run each labelled query block in queries.sql against data/energy.db and print results."""
import re
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/energy.db")
sql_text = open("sql/queries.sql").read()

# Split on the "-- Q<N>." markers
blocks = re.split(r"(?=-- Q\d+\.)", sql_text)
for block in blocks:
    m = re.match(r"-- (Q\d+)\.\s*(.+?)\n", block)
    if not m:
        continue
    label, title = m.group(1), m.group(2).strip()
    # Strip comment lines, keep the actual statement
    stmt = "\n".join(l for l in block.splitlines() if not l.strip().startswith("--")).strip()
    if not stmt:
        continue
    print(f"\n{'='*90}\n{label}: {title}\n{'='*90}")
    df = pd.read_sql(stmt, conn)
    print(df.to_string(index=False))

conn.close()
