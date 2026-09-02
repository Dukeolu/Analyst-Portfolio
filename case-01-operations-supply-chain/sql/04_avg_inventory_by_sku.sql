-- Average on-hand inventory and days-of-inventory per SKU, under the
-- current reorder policy -- the input the Python step uses to size the
-- cash tied up in over-protected C-tier SKUs.

SELECT
    inv.sku,
    s.category,
    ROUND(AVG(inv.on_hand_qty), 1)                 AS avg_on_hand_units,
    ROUND(AVG(inv.on_hand_qty) * s.unit_cost, 2)    AS avg_on_hand_value,
    ROUND(AVG(inv.on_hand_qty) / NULLIF(s.base_weekly_demand, 0) * 7, 1) AS avg_days_of_inventory,
    s.reorder_point_current
FROM inventory_snapshots inv
JOIN skus s ON s.sku = inv.sku
GROUP BY inv.sku, s.category, s.unit_cost, s.base_weekly_demand, s.reorder_point_current
ORDER BY avg_on_hand_value DESC;
