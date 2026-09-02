-- Intersectional risk pockets: contract type x support-ticket load. A
-- single-dimension breakdown hides this -- it's the *combination* that
-- matters, not either factor alone.

WITH bucketed AS (
    SELECT
        *,
        CASE
            WHEN support_tickets_90d = 0 THEN '0 tickets'
            WHEN support_tickets_90d <= 2 THEN '1-2 tickets'
            ELSE '3+ tickets'
        END AS ticket_bucket
    FROM customers
)
SELECT
    contract_type,
    ticket_bucket,
    COUNT(*)                                                        AS customers,
    ROUND(100.0 * SUM(CASE WHEN churned = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(avg_engagement_score), 1)                             AS avg_engagement_score,
    ROUND(SUM(CASE WHEN churned = 'No' THEN monthly_charge ELSE 0 END), 2) AS active_mrr
FROM bucketed
GROUP BY contract_type, ticket_bucket
HAVING COUNT(*) >= 20
ORDER BY churn_rate_pct DESC;
