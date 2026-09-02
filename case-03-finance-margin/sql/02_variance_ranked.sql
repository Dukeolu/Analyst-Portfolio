-- Rank every region x category combo by total profit variance over the
-- trailing 24 months, with a running share of total negative variance --
-- the number that answers "how much of the leak do the top N combos
-- account for."

WITH combo_variance AS (
    SELECT
        category,
        region,
        SUM(budget_profit)  AS budget_profit,
        SUM(actual_profit)  AS actual_profit,
        SUM(profit_variance) AS variance
    FROM budget_actuals
    GROUP BY category, region
),
ranked AS (
    SELECT
        *,
        RANK() OVER (ORDER BY variance ASC) AS variance_rank,
        SUM(CASE WHEN variance < 0 THEN variance ELSE 0 END) OVER () AS total_negative_variance,
        SUM(CASE WHEN variance < 0 THEN variance ELSE 0 END) OVER (
            ORDER BY variance ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_negative_variance
    FROM combo_variance
)
SELECT
    variance_rank,
    category,
    region,
    ROUND(budget_profit, 0) AS budget_profit,
    ROUND(actual_profit, 0) AS actual_profit,
    ROUND(variance, 0)      AS variance,
    ROUND(100.0 * variance / NULLIF(budget_profit, 0), 2) AS variance_pct,
    ROUND(100.0 * running_negative_variance / NULLIF(total_negative_variance, 0), 1) AS cumulative_pct_of_total_leak
FROM ranked
ORDER BY variance_rank;
