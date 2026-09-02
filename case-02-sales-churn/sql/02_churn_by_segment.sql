-- Churn rate, customer count, and monthly recurring revenue at risk, by
-- the three segment cuts a retention team would ask for first: how the
-- customer signed up, what contract they're on, and where they are.

SELECT
    'contract_type' AS segment_dimension,
    contract_type   AS segment_value,
    COUNT(*)                                                      AS customers,
    SUM(CASE WHEN churned = 'Yes' THEN 1 ELSE 0 END)               AS churned_customers,
    ROUND(100.0 * SUM(CASE WHEN churned = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN churned = 'No' THEN monthly_charge ELSE 0 END), 2) AS active_mrr
FROM customers GROUP BY contract_type

UNION ALL

SELECT
    'signup_channel', signup_channel,
    COUNT(*),
    SUM(CASE WHEN churned = 'Yes' THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN churned = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2),
    ROUND(SUM(CASE WHEN churned = 'No' THEN monthly_charge ELSE 0 END), 2)
FROM customers GROUP BY signup_channel

UNION ALL

SELECT
    'region', region,
    COUNT(*),
    SUM(CASE WHEN churned = 'Yes' THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN churned = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2),
    ROUND(SUM(CASE WHEN churned = 'No' THEN monthly_charge ELSE 0 END), 2)
FROM customers GROUP BY region

ORDER BY segment_dimension, churn_rate_pct DESC;
