-- Case 01: schema reference for the three tables loaded into SQLite
-- (loaded by scripts/02_load_and_run_sql.py; kept here so the schema is
-- reviewable without opening the loader script).

CREATE TABLE IF NOT EXISTS skus (
    sku                     TEXT PRIMARY KEY,
    category                TEXT NOT NULL,
    unit_cost               REAL NOT NULL,
    unit_price              REAL NOT NULL,
    base_weekly_demand      REAL NOT NULL,
    demand_cv               REAL NOT NULL,
    lead_time_days_mean     REAL NOT NULL,
    lead_time_days_std      REAL NOT NULL,
    reorder_point_current   REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        INTEGER PRIMARY KEY,
    order_date      TEXT NOT NULL,   -- week-ending date, ISO 8601
    sku             TEXT NOT NULL REFERENCES skus(sku),
    category        TEXT NOT NULL,
    region          TEXT NOT NULL,
    qty_ordered     REAL NOT NULL,
    qty_fulfilled   REAL NOT NULL,
    unit_cost       REAL NOT NULL,
    unit_price      REAL NOT NULL,
    revenue         REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory_snapshots (
    week_ending             TEXT NOT NULL,
    sku                     TEXT NOT NULL REFERENCES skus(sku),
    on_hand_qty             REAL NOT NULL,
    reorder_point_current   REAL NOT NULL,
    PRIMARY KEY (week_ending, sku)
);

CREATE INDEX IF NOT EXISTS idx_orders_sku ON orders(sku);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_inv_sku ON inventory_snapshots(sku);
