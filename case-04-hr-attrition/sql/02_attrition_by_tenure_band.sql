-- Attrition rate by tenure band and hiring channel -- the SQL version of
-- the "when do people actually leave" question, cut by channel to show
-- it isn't uniform.

WITH banded AS (
    SELECT
        *,
        CASE
            WHEN tenure_months <= 3 THEN '0-3 months'
            WHEN tenure_months <= 6 THEN '4-6 months'
            WHEN tenure_months <= 12 THEN '7-12 months'
            ELSE '13+ months'
        END AS tenure_band
    FROM employees
)
SELECT
    channel,
    tenure_band,
    COUNT(*) AS employees,
    SUM(CASE WHEN terminated_voluntary = 'Yes' THEN 1 ELSE 0 END) AS voluntary_terms,
    ROUND(100.0 * SUM(CASE WHEN terminated_voluntary = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS term_rate_pct
FROM banded
GROUP BY channel, tenure_band
HAVING COUNT(*) >= 15
ORDER BY channel,
    CASE tenure_band WHEN '0-3 months' THEN 1 WHEN '4-6 months' THEN 2 WHEN '7-12 months' THEN 3 ELSE 4 END;
