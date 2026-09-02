-- Running cumulative cash collected by month against a flat monthly target
-- (total 2024-2025 invoiced revenue / 24 months) -- the kind of tracker
-- a treasury/cash-management function would watch to catch a collections
-- slowdown early, rather than waiting for the month-end AR aging report.

WITH monthly_collected AS (
    SELECT
        strftime('%Y-%m', payment_date) AS month,
        SUM(payment_amount)             AS collected
    FROM payments
    GROUP BY month
),
target AS (
    SELECT ROUND(SUM(invoice_amount) / 24.0, 2) AS monthly_target
    FROM invoices
)
SELECT
    m.month,
    m.collected,
    t.monthly_target,
    ROUND(SUM(m.collected) OVER (ORDER BY m.month), 2)                              AS cumulative_collected,
    ROUND(t.monthly_target * ROW_NUMBER() OVER (ORDER BY m.month), 2)               AS cumulative_target,
    ROUND(SUM(m.collected) OVER (ORDER BY m.month)
          - t.monthly_target * ROW_NUMBER() OVER (ORDER BY m.month), 2)             AS cumulative_variance
FROM monthly_collected m
CROSS JOIN target t
ORDER BY m.month;
