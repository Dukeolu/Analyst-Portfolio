"""
Extra 08 -- Step 2: forecast the holdout period three ways and compare.

Two naive baselines a planner might actually use without any modeling
effort, against Holt-Winters exponential smoothing (additive trend +
additive seasonality) -- the simplest method that can actually use the
seasonal pattern.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

TEST_WEEKS = 52
SEASONAL_PERIOD = 52

df = pd.read_csv(RAW / "weekly_demand.csv", parse_dates=["week_start"])
series = df.set_index("week_start")["units_sold"]

train = series.iloc[:-TEST_WEEKS]
test = series.iloc[-TEST_WEEKS:]

# ---------------------------------------------------------------- baseline 1: naive
# "next N weeks = last observed value, flat" -- the zero-effort forecast
naive_forecast = pd.Series(train.iloc[-1], index=test.index)

# ---------------------------------------------------------------- baseline 2: seasonal naive
# "this week = the same week last year" -- free seasonality, no trend, no fitting
seasonal_naive_forecast = series.shift(SEASONAL_PERIOD).loc[test.index]

# ---------------------------------------------------------------- Holt-Winters
hw_model = ExponentialSmoothing(
    train, trend="add", seasonal="add", seasonal_periods=SEASONAL_PERIOD,
    initialization_method="estimated",
).fit()
hw_forecast = hw_model.forecast(TEST_WEEKS)
hw_forecast.index = test.index


def score(actual, forecast, name):
    err = actual - forecast
    mae = err.abs().mean()
    rmse = np.sqrt((err ** 2).mean())
    mape = (err.abs() / actual).mean()
    return {"method": name, "mae": round(mae, 1), "rmse": round(rmse, 1), "mape": round(mape, 4)}


results = pd.DataFrame([
    score(test, naive_forecast, "Naive (flat)"),
    score(test, seasonal_naive_forecast, "Seasonal naive (same week last year)"),
    score(test, hw_forecast, "Holt-Winters (trend + seasonal)"),
])
results["mape_pct"] = (results["mape"] * 100).round(1)
results.to_csv(PROCESSED / "forecast_accuracy.csv", index=False)

forecasts_out = pd.DataFrame({
    "week_start": test.index,
    "actual": test.values,
    "naive": naive_forecast.values,
    "seasonal_naive": seasonal_naive_forecast.values,
    "holt_winters": hw_forecast.values.round(1),
})
forecasts_out.to_csv(PROCESSED / "forecast_vs_actual.csv", index=False)

best_baseline_mape = results.loc[results["method"] != "Holt-Winters (trend + seasonal)", "mape"].min()
hw_mape = results.loc[results["method"] == "Holt-Winters (trend + seasonal)", "mape"].iloc[0]
improvement = (best_baseline_mape - hw_mape) / best_baseline_mape

print(f"Train weeks: {len(train)}  |  Test (holdout) weeks: {len(test)}")
print("\nForecast accuracy on the 52-week holdout:")
print(results.to_string(index=False))
print(f"\nHolt-Winters improves MAPE by {improvement:.1%} vs. the best naive baseline "
      f"({best_baseline_mape:.1%} -> {hw_mape:.1%})")
