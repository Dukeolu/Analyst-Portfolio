-- Case 04: schema reference for the two tables loaded into SQLite.

CREATE TABLE IF NOT EXISTS employees (
    employee_id             TEXT PRIMARY KEY,
    hire_month               TEXT NOT NULL,
    department               TEXT NOT NULL,
    channel                  TEXT NOT NULL,
    level                     TEXT NOT NULL,
    comp_ratio                REAL NOT NULL,
    manager_span              INTEGER NOT NULL,
    overtime_hours_monthly    REAL NOT NULL,
    avg_engagement_score      REAL NOT NULL,
    tenure_months             INTEGER NOT NULL,
    months_observable         INTEGER NOT NULL,
    terminated_voluntary      TEXT NOT NULL   -- 'Yes' / 'No'
);

CREATE TABLE IF NOT EXISTS recruiting_funnel (
    month        TEXT NOT NULL,
    department   TEXT NOT NULL,
    channel      TEXT NOT NULL,
    applied      INTEGER NOT NULL,
    screened     INTEGER NOT NULL,
    interviewed  INTEGER NOT NULL,
    offered      INTEGER NOT NULL,
    hired        INTEGER NOT NULL,
    PRIMARY KEY (month, department, channel)
);

CREATE INDEX IF NOT EXISTS idx_emp_dept ON employees(department);
CREATE INDEX IF NOT EXISTS idx_emp_channel ON employees(channel);
CREATE INDEX IF NOT EXISTS idx_funnel_dept_channel ON recruiting_funnel(department, channel);
