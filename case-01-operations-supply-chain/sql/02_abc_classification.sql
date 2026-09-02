-- ABC classification: rank SKUs by trailing revenue, then bucket them by
-- cumulative share of total revenue (the standard 80/15/5 split). This is
-- the segmentation everything downstream (fill-rate targets, safety stock)
-- is built on -- A-items get tighter service targets, C-items don't.

WITH sku_revenue AS (
    SELECT
        sku,
        category,
        SUM(revenue) AS trailing_revenue,
        SUM(qty_ordered) AS trailing_units_ordered
    FROM orders
    GROUP BY sku, category
),
ranked AS (
    SELECT
        sku,
        category,
        trailing_revenue,
        trailing_units_ordered,
        SUM(trailing_revenue) OVER (ORDER BY trailing_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_revenue,
        SUM(trailing_revenue) OVER () AS total_revenue,
        ROW_NUMBER() OVER (ORDER BY trailing_revenue DESC) AS revenue_rank
    FROM sku_revenue
)
SELECT
    sku,
    category,
    ROUND(trailing_revenue, 2)        AS trailing_revenue,
    trailing_units_ordered,
    revenue_rank,
    ROUND(100.0 * running_revenue / total_revenue, 2) AS cumulative_revenue_pct,
    CASE
        WHEN running_revenue / total_revenue <= 0.80 THEN 'A'
        WHEN running_revenue / total_revenue <= 0.95 THEN 'B'
        ELSE 'C'
    END AS abc_tier
FROM ranked
ORDER BY revenue_rank;
