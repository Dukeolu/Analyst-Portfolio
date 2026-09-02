-- Accounts-receivable aging as of the snapshot date: every invoice that's
-- past due and still carries an outstanding balance, bucketed by how many
-- days overdue it is. This is the standard AR aging report a controller
-- would pull at month-end.

WITH outstanding AS (
    SELECT
        s.invoice_id,
        c.segment,
        c.risk_tier,
        s.outstanding_balance,
        CAST(julianday('2025-12-31') - julianday(s.due_date) AS INTEGER) AS days_overdue
    FROM invoice_payment_status s
    JOIN customers c ON c.customer_id = s.customer_id
    WHERE s.outstanding_balance > 0.01
      AND s.due_date <= '2025-12-31'
),
bucketed AS (
    SELECT
        *,
        CASE
            WHEN days_overdue <= 30  THEN '0-30 days'
            WHEN days_overdue <= 60  THEN '31-60 days'
            WHEN days_overdue <= 90  THEN '61-90 days'
            ELSE '90+ days'
        END AS aging_bucket
    FROM outstanding
)
SELECT
    aging_bucket,
    segment,
    risk_tier,
    COUNT(*)                            AS invoice_count,
    ROUND(SUM(outstanding_balance), 2)  AS outstanding_total,
    ROUND(100.0 * SUM(outstanding_balance) / SUM(SUM(outstanding_balance)) OVER (), 1) AS pct_of_total_outstanding
FROM bucketed
GROUP BY aging_bucket, segment, risk_tier
ORDER BY
    CASE aging_bucket WHEN '0-30 days' THEN 1 WHEN '31-60 days' THEN 2 WHEN '61-90 days' THEN 3 ELSE 4 END,
    outstanding_total DESC;
