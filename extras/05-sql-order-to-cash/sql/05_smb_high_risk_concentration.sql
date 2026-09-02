-- How much of total outstanding AR is concentrated specifically in the
-- SMB x High-risk intersection -- the slice a segment-only or risk-only
-- breakdown each individually hide.

WITH outstanding AS (
    SELECT
        s.outstanding_balance,
        c.segment,
        c.risk_tier
    FROM invoice_payment_status s
    JOIN customers c ON c.customer_id = s.customer_id
    WHERE s.outstanding_balance > 0.01
      AND s.due_date <= '2025-12-31'
)
SELECT
    CASE WHEN segment = 'SMB' AND risk_tier = 'High' THEN 'SMB x High-risk' ELSE 'everyone else' END AS slice,
    COUNT(*)                           AS invoice_count,
    ROUND(SUM(outstanding_balance), 2) AS outstanding_total,
    ROUND(100.0 * SUM(outstanding_balance) / SUM(SUM(outstanding_balance)) OVER (), 1) AS pct_of_total_outstanding
FROM outstanding
GROUP BY slice
ORDER BY outstanding_total DESC;
