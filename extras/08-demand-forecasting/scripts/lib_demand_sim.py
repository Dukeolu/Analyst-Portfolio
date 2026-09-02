"""Simulates 3.5 years of weekly demand for one product: a gentle upward
trend, strong yearly seasonality (holiday-driven -- peaks in Nov/Dec,
trough in summer), a few one-off promo spikes, and multiplicative noise."""
import numpy as np
import pandas as pd

RNG_SEED = 19
N_WEEKS = 182  # 3.5 years
START_DATE = pd.Timestamp("2023-01-02")  # a Monday

BASE_LEVEL = 4200
WEEKLY_TREND = 6.5  # units/week added to the level, on average
SEASONAL_AMPLITUDE = 0.42  # +/- 42% swing at peak/trough vs. the trend level
NOISE_SD_PCT = 0.07

PROMO_WEEKS = [18, 44, 96, 122, 148, 170]  # a handful of one-off promo spikes
PROMO_LIFT = 0.35


def build_demand(seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    weeks = pd.date_range(START_DATE, periods=N_WEEKS, freq="W-MON")
    t = np.arange(N_WEEKS)

    trend = BASE_LEVEL + WEEKLY_TREND * t
    # yearly seasonality: peak around week 47-48 (late Nov), trough around week 21-22 (late May)
    seasonal = SEASONAL_AMPLITUDE * np.cos(2 * np.pi * (t - 47) / 52)
    level = trend * (1 + seasonal)

    promo = np.zeros(N_WEEKS)
    for pw in PROMO_WEEKS:
        if pw < N_WEEKS:
            promo[pw] = PROMO_LIFT

    noise = rng.normal(0, NOISE_SD_PCT, size=N_WEEKS)
    demand = level * (1 + promo + noise)
    demand = np.round(np.clip(demand, 200, None)).astype(int)

    return pd.DataFrame({"week_start": weeks, "units_sold": demand})
