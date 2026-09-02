-- Case 02: schema reference for the customers table loaded into SQLite
-- (loaded by scripts/02_load_and_run_sql.py).

CREATE TABLE IF NOT EXISTS customers (
    customer_id             TEXT PRIMARY KEY,
    signup_month            TEXT NOT NULL,
    contract_type           TEXT NOT NULL,
    plan_tier               TEXT NOT NULL,
    addon_count             INTEGER NOT NULL,
    monthly_charge          REAL NOT NULL,
    autopay                 TEXT NOT NULL,   -- 'Yes' / 'No'
    signup_channel          TEXT NOT NULL,
    region                  TEXT NOT NULL,
    tenure_months           INTEGER NOT NULL,
    months_observable       INTEGER NOT NULL,
    avg_engagement_score    REAL NOT NULL,
    support_tickets_90d     INTEGER NOT NULL,
    churned                 TEXT NOT NULL    -- 'Yes' / 'No'
);

CREATE INDEX IF NOT EXISTS idx_customers_contract ON customers(contract_type);
CREATE INDEX IF NOT EXISTS idx_customers_churned ON customers(churned);
