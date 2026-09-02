-- Monthly variance trend for the four worst combos -- shows whether the
-- leak is a one-off blip or a trend that's still getting worse (it's the
-- latter, which is exactly why it needs a decision now, not next quarter).

WITH worst_combos AS (
    SELECT category, region
    FROM (
        SELECT category, region, SUM(profit_variance) AS total_variance
        FROM budget_actuals
        GROUP BY category, region
        ORDER BY total_variance ASC
        LIMIT 4
    )
)
SELECT
    ba.month,
    ba.category,
    ba.region,
    ROUND(ba.profit_variance, 0) AS profit_variance,
    ROUND(ba.actual_discount_pct - ba.budget_discount_pct, 4) AS discount_variance_pts,
    ROUND(ba.actual_cogs_pct - ba.budget_cogs_pct, 4)         AS cogs_variance_pts
FROM budget_actuals ba
JOIN worst_combos wc ON wc.category = ba.category AND wc.region = ba.region
ORDER BY ba.category, ba.region, ba.month;
