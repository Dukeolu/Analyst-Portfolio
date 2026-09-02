-- Case 03: schema reference for the budget_actuals table loaded into SQLite.

CREATE TABLE IF NOT EXISTS budget_actuals (
    month                   TEXT NOT NULL,
    region                  TEXT NOT NULL,
    category                TEXT NOT NULL,
    budget_revenue          REAL NOT NULL,
    budget_discount_pct     REAL NOT NULL,
    budget_cogs_pct         REAL NOT NULL,
    actual_revenue          REAL NOT NULL,
    actual_discount_pct     REAL NOT NULL,
    actual_cogs_pct         REAL NOT NULL,
    budget_net_revenue      REAL NOT NULL,
    budget_cogs             REAL NOT NULL,
    budget_profit           REAL NOT NULL,
    actual_net_revenue      REAL NOT NULL,
    actual_cogs             REAL NOT NULL,
    actual_profit           REAL NOT NULL,
    profit_variance         REAL NOT NULL,
    PRIMARY KEY (month, region, category)
);

CREATE INDEX IF NOT EXISTS idx_ba_region_cat ON budget_actuals(region, category);
CREATE INDEX IF NOT EXISTS idx_ba_month ON budget_actuals(month);
