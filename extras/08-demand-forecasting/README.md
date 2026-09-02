# Extra 08 — Demand forecasting: how much does modeling actually buy you?

**Tool:** Python (pandas, statsmodels) — one holdout comparison, one chart. No dashboard, no Excel, no SQL.

[Actual vs. forecast chart](charts/actual_vs_forecast.png) · [Accuracy comparison](data/processed/forecast_accuracy.csv)

## The question

Before reaching for a forecasting model, it's worth knowing exactly how much better than "no model at all" it actually is — otherwise the modeling effort might not be worth it. This project answers that directly: **3.5 years of simulated weekly demand** for one product (182 weeks — trend, strong yearly seasonality peaking around late November, a handful of one-off promo spikes, and realistic noise), with the final 52 weeks held out and never seen during fitting, forecast three different ways.

## Method

1. **Naive (flat)** — forecast every week of the holdout as simply the last observed value. The zero-effort baseline.
2. **Seasonal naive** — forecast each week as whatever actually happened the same week one year earlier. Free seasonality, no fitting, still no trend.
3. **Holt-Winters exponential smoothing** (`statsmodels`, additive trend + additive seasonality, 52-week period) — fit on the training 130 weeks only, forecast the 52-week holdout.

All three scored against the same held-out actuals on MAE, RMSE, and MAPE — nothing is fit or tuned on the test period.

## Findings

| Method | MAE | RMSE | MAPE |
|---|---|---|---|
| Naive (flat) | 2,028 | 2,585 | 32.2% |
| Seasonal naive (same week last year) | 536 | 703 | 10.2% |
| **Holt-Winters (trend + seasonal)** | **377** | **490** | **7.4%** |

The flat baseline is, unsurprisingly, bad — a single number can't represent a series that swings from ~2,700 to ~9,700 units across a year. Seasonal naive gets most of the way there for free: just repeating last year's pattern captures the seasonality and gets MAPE down to 10.2%. Holt-Winters — which additionally fits a trend on top of the seasonal pattern rather than assuming this year repeats last year exactly — improves on that by a further **27.6%** (10.2% → 7.4% MAPE). The chart makes the gap visible directly: the flat baseline is a straight line that ignores the entire holdout's shape, seasonal naive tracks the *shape* but misses that the whole series has grown since last year, and Holt-Winters tracks both.

## Repo structure

```
08-demand-forecasting/
├── data/
│   ├── raw/                  weekly_demand.csv
│   └── processed/            forecast_accuracy.csv, forecast_vs_actual.csv
├── scripts/                  01_generate_data → 02_forecast_and_evaluate → 03_build_chart
├── charts/actual_vs_forecast.png
└── README.md
```

To reproduce: `cd scripts && python3 01_generate_data.py && python3 02_forecast_and_evaluate.py && python3 03_build_chart.py`

**Limitations, stated plainly:** the series is simulated, so the exact accuracy numbers are illustrative — the method (always benchmark a model against the naive alternatives someone could compute in a spreadsheet before shipping it) is the transferable part. A single 52-week holdout is one test, not a robust cross-validated estimate — a production forecasting pipeline would want rolling-origin backtesting across multiple holdout windows before trusting a single improvement number this precisely.
