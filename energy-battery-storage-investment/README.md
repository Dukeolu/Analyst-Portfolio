# Where Would Battery Storage Pay Off? — Meridian Renewables (simulated)

**Skills:** SQL &middot; Python &middot; forecasting &middot; energy market analytics &middot; investment economics (NPV/IRR)

## The business problem

Meridian Renewables (simulated) operates five renewable sites — three solar,
two onshore wind — and has budget for one behind-the-meter battery storage
investment this year, with more to follow if the first one earns its keep.
Every site "could" host a battery. The decision the business actually needs to
make is *which site first, and does the investment case survive scrutiny* —
not a general observation that batteries are a good idea.

The specific commercial question: **when and where would co-located battery
storage provide the greatest commercial value alongside our renewable
generation, and does the economics of the best candidate actually clear an
investment hurdle?**

## The data

Simulated hourly data, 2024-01-01 to 2025-12-31 (2 full years, 17,544 hours):
site metadata, per-site generation (MWh), and national demand + day-ahead
wholesale price (£/MWh). This sandbox can't reach real energy-market data
sources (Elexon/BMRS, NESO, Kaggle), so the series were built to reproduce the
real, well-documented dynamics of a renewables-heavy market — including
genuine negative-price events — rather than downloaded. Full schema, model,
and limitations: [`data/README.md`](data/README.md).

## Data preparation

Generation and price series were built directly at hourly grain with no
missing values or duplicates by construction (a simulation, not a scraped
export), so the preparation work here is calibration rather than cleaning:
solar and wind output were each independently tuned against real-world UK-like
capacity-factor ranges (solar ~9-12%, onshore wind ~27-31%) until the
generator's output matched, and the price model's renewable-suppression
coefficients were tuned until the capture-rate gap between technologies
(below) matched the order of magnitude reported in real capture-price
literature for high-solar-penetration markets, rather than picking whatever
number happened to fall out first. All three raw files were then loaded
as-is into a SQLite database (`sql/build_db.py`) for the SQL analysis.

## Analysis

1. **SQL** (`sql/queries.sql`, run via `sql/run_queries.py`) — capacity
   factor by site, the capture-rate calculation, a year-on-year capture-rate
   check, monthly price volatility, and a query that isolates the
   cannibalisation mechanism directly (price by national-solar-output
   quintile).
2. **Python / notebook** (`notebooks/battery_value_analysis.ipynb`) —
   reproduces and extends the SQL findings; simulates a 10 MW / 20 MWh
   behind-the-meter battery per site (`src/battery_model.py`) picking each
   day's cheapest hours to charge from the site's own generation and priciest
   hours to discharge; fits a seasonal-naive forecast of the monthly price
   spread and validates it against year 2; and builds 15-year NPV/IRR/payback
   investment economics for the two candidate sites at opposite ends of the
   ranking.

## Key findings

1. **Solar is structurally under-paid by the market, and it's not a small
   effect.** All three solar sites capture only **76.3%** of the simple
   average market price for their output, while the two wind sites capture
   **106-107%** — a ~31 percentage-point gap driven entirely by *when* each
   technology generates, not by how much. Isolating the mechanism directly:
   average price falls from £35.2/MWh in the lowest quintile of national
   solar output to £16.0/MWh in the highest quintile — solar cannibalises its
   own price by generating exactly when every other solar site does too.
2. **That gap is stable, not narrowing on its own.** Solar's capture rate
   held at 76.0% in 2024 and 76.7% in 2025 — essentially flat. The business
   can't assume this fixes itself as the portfolio matures; it needs a
   deliberate intervention.
3. **The sites earning the least per MWh gain the most from a battery.** A
   co-located battery earns by time-shifting a site's own generation from its
   cheapest hours to its priciest hours each day. Solar's concentrated,
   deeply-discounted output gives a battery far more spread to exploit:
   estimated annual arbitrage uplift ranges from **£216,474/year at Solent
   Solar Park** (the top-ranked site) down to **£146,451/year at Cambria Wind
   Farm** (the lowest-ranked) — a site-capacity-agnostic ranking that tracks
   capture-rate disadvantage, not nameplate MW or total generation volume.
4. **The underlying price-spread opportunity is seasonal but predictable.** A
   simple seasonal-naive forecast (using each month's 2024 spread as the 2025
   forecast) had a mean absolute error of just £1.37/MWh against a £40.20/MWh
   average spread (3.4% error) — stable enough to underwrite a multi-year
   asset against, not a one-off artefact of a single year.
5. **Pure arbitrage alone doesn't clear a normal investment hurdle — but
   stacked with capacity-market revenue, both candidate sites do, and the
   ranking still matters.** At Solent Solar Park (10 MW/20 MWh, £1.8M capex,
   £180k/MW): **NPV £2.72M, IRR 28.5%, payback 3.4 years**. At Cambria Wind
   Farm under identical assumptions: **NPV £2.18M, IRR 24.7%, payback 3.9
   years**. Both clear the hurdle; Solent clears it faster and by a wider
   margin, entirely because of the arbitrage layer quantified in Finding 3.

## Recommendations

1. **Fund the first battery at Solent Solar Park**, not at the largest site
   (Pennine Wind Farm, 60 MW) or by any other capacity-led rule of thumb —
   the arbitrage-value ranking, not nameplate size, should decide the order.
2. **If capital allows a second and third tranche this year, follow the same
   ranking**: Fenland Solar Array and Dee Solar Farm next, ahead of the two
   wind sites — all three solar sites are structurally the most under-paid
   and therefore the most improvable.
3. **Underwrite the investment case on capacity-market plus arbitrage
   revenue, not arbitrage alone** — a pure-arbitrage-only case would show a
   negative NPV at every site under these capex assumptions (see the notebook
   for that comparison) and would wrongly kill a genuinely good investment.
4. **Re-run the capture-rate analysis annually** rather than assuming the
   26-31 point solar/wind gap is temporary — Finding 2 shows no sign of it
   closing on its own.

## Expected impact

Prioritising Solent Solar Park over a capacity-led default (e.g. Pennine
Wind Farm) is worth an estimated **£500,000 more NPV and 0.5 years faster
payback** on the first battery investment alone (Finding 5). Rolling the same
battery spec out across all three solar sites, once capital allows, represents
an estimated **£615,983/year in combined arbitrage uplift** (Solent + Fenland
+ Dee, Finding 3) on top of whatever capacity-market revenue those assets
would earn regardless of siting decision.

## Limitations / next analysis

- **Perfect day-ahead price foresight.** The battery simulation assumes the
  operator knows the day's prices in advance when choosing charge/discharge
  hours. Real operations run on forecast prices with forecast error; a
  production model should re-run this with a realistic day-ahead forecast
  error distribution layered on top, which would lower the achievable uplift
  somewhat versus the perfect-foresight ceiling estimated here.
- **Single cycle per day.** Some real batteries can cycle more than once
  daily when price volatility allows; this would likely widen the gap in
  Meridian's favour, not narrow it, since higher-volatility days would be
  exploited more fully — but it's not modelled here, so the estimates in this
  report should be read as a reasonable single-cycle floor, not a ceiling.
- **No curtailment or grid-constraint modelling.** Sites are never physically
  constrained off; if the real network has export limits at any of the five
  connection points, the battery's *additional* value from avoiding curtailed
  (and otherwise entirely lost) energy could be materially higher than
  estimated here, especially at the largest sites.
- **Capex, capacity-market rate, and O&M are stated assumptions**, not a live
  tender quote — see `data/README.md` for the specific figures and reasoning.
  The next step before committing capital would be an actual OEM/EPC quote
  for the Solent Solar Park connection specifically, and a check against the
  current live capacity-market clearing price rather than an illustrative one.
- **Two years of data**, not enough to confirm whether the solar/wind capture
  gap widens as more solar capacity is added to the grid nationally over the
  next decade — a well-documented real-world trend this simulation doesn't
  attempt to model. If it does widen, as it has in comparable real markets,
  every finding here understates the case for prioritising solar sites.

## Repo structure

```
energy-battery-storage-investment/
├── README.md                          this file
├── requirements.txt
├── data/
│   ├── README.md                      data model, sources, limitations
│   └── raw/
│       ├── sites.csv
│       ├── generation.csv
│       └── market.csv
├── src/
│   ├── generate_data.py               builds the simulated dataset
│   └── battery_model.py               the battery arbitrage simulation
├── sql/
│   ├── build_db.py                    loads the CSVs into SQLite
│   ├── queries.sql                    the 5 labelled analysis queries
│   └── run_queries.py                 runs and prints all 5
├── notebooks/
│   ├── build_notebook.py              builds the notebook programmatically
│   └── battery_value_analysis.ipynb   the executed analysis notebook
└── visuals/
    ├── capture_rate_by_site.png
    ├── cannibalisation_mechanism.png
    ├── battery_uplift_ranking.png
    ├── seasonal_price_spread.png
    └── battery-value-exhibit.html     self-contained visual summary (site link)
```
