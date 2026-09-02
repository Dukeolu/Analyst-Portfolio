-- Service-level KPIs by ABC tier, category and region: the diagnostic that
-- shows the current reorder policy isn't just "a bit off" on average -- it's
-- systematically failing the SKUs that matter most (A-tier) while over-
-- protecting the ones that matter least (C-tier).

WITH abc AS (
    -- inline copy of 02_abc_classification.sql's tiering logic, kept
    -- self-contained so this query can be run on its own
    WITH sku_revenue AS (
        SELECT sku, SUM(revenue) AS trailing_revenue
        FROM orders GROUP BY sku
    ),
    ranked AS (
        SELECT
            sku, trailing_revenue,
            SUM(trailing_revenue) OVER (ORDER BY trailing_revenue DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_revenue,
            SUM(trailing_revenue) OVER () AS total_revenue
        FROM sku_revenue
    )
    SELECT
        sku,
        CASE
            WHEN running_revenue / total_revenue <= 0.80 THEN 'A'
            WHEN running_revenue / total_revenue <= 0.95 THEN 'B'
            ELSE 'C'
        END AS abc_tier
    FROM ranked
)
SELECT
    abc.abc_tier,
    COUNT(DISTINCT o.sku)                              AS sku_count,
    ROUND(SUM(o.qty_fulfilled), 0)                      AS units_fulfilled,
    ROUND(SUM(o.qty_ordered), 0)                        AS units_ordered,
    ROUND(100.0 * SUM(o.qty_fulfilled) / SUM(o.qty_ordered), 2) AS fill_rate_pct,
    ROUND(100.0 * (1 - SUM(o.qty_fulfilled) / SUM(o.qty_ordered)), 2) AS stockout_rate_pct,
    ROUND(SUM(o.revenue), 2)                            AS revenue
FROM orders o
JOIN abc ON abc.sku = o.sku
GROUP BY abc.abc_tier
ORDER BY abc.abc_tier;
