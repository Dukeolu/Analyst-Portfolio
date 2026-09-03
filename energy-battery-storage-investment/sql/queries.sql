-- ============================================================================
-- Meridian Renewables — Battery Storage Investment Case
-- SQL analysis (SQLite). Run via sql/run_queries.py to reproduce the printed
-- results below (also embedded, with commentary, in notebooks/battery_value_
-- analysis.ipynb).
-- ============================================================================

-- --------------------------------------------------------------------------
-- Q1. Realised capacity factor by site (2024-2025 combined)
-- --------------------------------------------------------------------------
SELECT
  s.site_name,
  s.technology,
  s.region,
  s.capacity_mw,
  ROUND(AVG(g.generation_mwh) / s.capacity_mw, 3) AS realised_capacity_factor,
  ROUND(SUM(g.generation_mwh) / 1000.0, 1) AS total_generation_gwh
FROM generation g
JOIN sites s ON s.site_id = g.site_id
GROUP BY s.site_id
ORDER BY s.technology, realised_capacity_factor DESC;

-- --------------------------------------------------------------------------
-- Q2. Capture rate by site: volume-weighted price received vs the simple
--     average market price. This is the core commercial metric of the case —
--     a capture rate below 100% means the site is structurally paid less per
--     MWh than an average generator would be, because its output is
--     concentrated in hours when the market is oversupplied.
-- --------------------------------------------------------------------------
WITH avg_price AS (
  SELECT AVG(price_gbp_per_mwh) AS simple_avg_price FROM market
),
site_capture AS (
  SELECT
    s.site_id,
    s.site_name,
    s.technology,
    SUM(g.generation_mwh * m.price_gbp_per_mwh) / SUM(g.generation_mwh) AS capture_price,
    SUM(g.generation_mwh) AS total_mwh
  FROM generation g
  JOIN market m ON m.timestamp = g.timestamp
  JOIN sites s ON s.site_id = g.site_id
  GROUP BY s.site_id
)
SELECT
  sc.site_name,
  sc.technology,
  ROUND(sc.capture_price, 2) AS capture_price_gbp_mwh,
  ROUND(ap.simple_avg_price, 2) AS market_avg_price_gbp_mwh,
  ROUND(100.0 * sc.capture_price / ap.simple_avg_price, 1) AS capture_rate_pct,
  ROUND(sc.total_mwh / 1000.0, 1) AS total_generation_gwh,
  -- Revenue "lost" (or gained) versus what the site would have earned selling
  -- its same output at the flat average price
  ROUND((sc.capture_price - ap.simple_avg_price) * sc.total_mwh / 1000.0, 1) AS vs_flat_price_gbp_000s
FROM site_capture sc, avg_price ap
ORDER BY capture_rate_pct ASC;

-- --------------------------------------------------------------------------
-- Q3. Capture-rate trend by technology, 2024 vs 2025 — is cannibalisation
--     getting worse year over year? (feeds the forecasting step)
-- --------------------------------------------------------------------------
WITH avg_price_by_year AS (
  SELECT CAST(strftime('%Y', timestamp) AS INT) AS yr, AVG(price_gbp_per_mwh) AS avg_price
  FROM market GROUP BY yr
),
tech_capture_by_year AS (
  SELECT
    s.technology,
    CAST(strftime('%Y', g.timestamp) AS INT) AS yr,
    SUM(g.generation_mwh * m.price_gbp_per_mwh) / SUM(g.generation_mwh) AS capture_price
  FROM generation g
  JOIN market m ON m.timestamp = g.timestamp
  JOIN sites s ON s.site_id = g.site_id
  GROUP BY s.technology, yr
)
SELECT
  t.technology,
  t.yr,
  ROUND(t.capture_price, 2) AS capture_price,
  ROUND(a.avg_price, 2) AS market_avg_price,
  ROUND(100.0 * t.capture_price / a.avg_price, 1) AS capture_rate_pct
FROM tech_capture_by_year t
JOIN avg_price_by_year a ON a.yr = t.yr
ORDER BY t.technology, t.yr;

-- --------------------------------------------------------------------------
-- Q4. Price volatility & negative-price hours by month — where/when is the
--     arbitrage opportunity concentrated?
-- --------------------------------------------------------------------------
SELECT
  strftime('%Y-%m', timestamp) AS month,
  ROUND(AVG(price_gbp_per_mwh), 2) AS avg_price,
  ROUND(MAX(price_gbp_per_mwh) - MIN(price_gbp_per_mwh), 1) AS price_range,
  ROUND(
    (SELECT AVG(p2) FROM (
        SELECT price_gbp_per_mwh AS p2 FROM market m2
        WHERE strftime('%Y-%m', m2.timestamp) = strftime('%Y-%m', market.timestamp)
        ORDER BY p2 DESC LIMIT 20
     )), 1
  ) AS avg_top20_hourly_price,
  SUM(CASE WHEN price_gbp_per_mwh < 0 THEN 1 ELSE 0 END) AS negative_price_hours
FROM market
GROUP BY month
ORDER BY month;

-- --------------------------------------------------------------------------
-- Q5. The cannibalisation mechanism, made explicit: bucket daylight hours by
--     how high aggregate national SOLAR output is at that moment (our sample
--     sites, scaled to the national fleet), and show the average market
--     price in each bucket. If cannibalisation is real, price should fall
--     as national solar output rises.
-- --------------------------------------------------------------------------
WITH solar_by_ts AS (
  SELECT g.timestamp, SUM(g.generation_mwh) / 0.010 AS national_solar_mw
  FROM generation g
  JOIN sites s ON s.site_id = g.site_id AND s.technology = 'Solar'
  GROUP BY g.timestamp
  HAVING national_solar_mw > 50   -- daylight hours with meaningful solar output only
),
ranked AS (
  SELECT
    sb.timestamp,
    sb.national_solar_mw,
    m.price_gbp_per_mwh,
    NTILE(5) OVER (ORDER BY sb.national_solar_mw) AS solar_output_quintile
  FROM solar_by_ts sb
  JOIN market m ON m.timestamp = sb.timestamp
)
SELECT
  solar_output_quintile,
  COUNT(*) AS n_hours,
  ROUND(AVG(national_solar_mw), 0) AS avg_national_solar_mw,
  ROUND(AVG(price_gbp_per_mwh), 2) AS avg_price_gbp_mwh
FROM ranked
GROUP BY solar_output_quintile
ORDER BY solar_output_quintile;
