# Data

All three files in `raw/` are **simulated**, not downloaded from a real market or
generation dataset. This project's network sandbox can't reach public energy data
sources (Elexon/BMRS, NESO, Ofgem, Kaggle), so the data was built from scratch to
reproduce the structure and dynamics of a real renewable-heavy wholesale market —
see the generator at `../src/generate_data.py` for the exact model and every
assumption. If real settlement-period price and generation data is available, the
same pipeline can be re-pointed at it with no change to the SQL, notebook, or
battery model downstream.

## Files

**`sites.csv`** (5 rows) — static metadata for five fictional renewable sites
(3 solar, 2 onshore wind): `site_id`, `site_name`, `technology`, `region`,
`capacity_mw`, `base_capacity_factor`.

**`generation.csv`** (87,720 rows) — hourly generation in MWh per site, 2024-01-01
through 2025-12-31. Solar output follows a daylight/seasonal envelope with
autocorrelated day-to-day "cloudiness"; wind output follows a mean-reverting
simulated wind-speed process passed through a simplified cubic power curve with
cut-in (3.5 m/s), rated (13 m/s), and cut-out (25 m/s) thresholds.

**`market.csv`** (17,544 rows) — hourly national demand (MW), day-ahead wholesale
price (£/MWh), and an implied national renewable output figure (our five sites
scaled up to represent a national fleet). Price is generated from a simplified
merit-order model: it rises with demand and falls with aggregate national
renewable output (solar output suppressing price more sharply than wind, per MW,
because solar's fleet-wide simultaneity concentrates the effect), plus periodic
gas-price shock days and random noise. Genuine negative-price hours occur (21
hours, 0.12% of the period) when renewable output is high and demand is low —
a real, well-documented phenomenon in markets with high renewables penetration.

## Known limitations of the simulated data

- **Single national price signal.** Real markets have locational/zonal price
  differences; this model uses one national price series, so it can't capture
  transmission-constraint or curtailment effects specific to a site's grid
  connection point.
- **No modelled curtailment.** Sites are never physically constrained off during
  oversupply — the price signal captures the *economic* effect of oversupply,
  but not the operational reality that some renewable output is curtailed
  entirely during extreme events.
- **Simplified wind physics.** The power curve is a standard simplified cubic
  approximation, not turbine-specific manufacturer data.
- **Two years only.** Long enough to check year-on-year consistency (Section 5
  of the notebook) but too short to draw conclusions about multi-year trends
  such as renewables-penetration growth eroding capture rates further over time.
- **Illustrative capex/revenue assumptions.** Battery capex (£180k/MW), capacity
  market payment (£35k/MW/year), and O&M (£42k/year) are stated, defensible
  assumptions for a 2024/2025-vintage 2-hour system — not sourced from a specific
  live tender or contract. Treat the investment economics as directionally
  correct, not as a quote.

Random seed is fixed (`numpy.random.default_rng(42)`), so re-running
`src/generate_data.py` reproduces byte-identical output.
