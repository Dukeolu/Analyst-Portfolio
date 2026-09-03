"""
Generate simulated hourly data for the Meridian Renewables battery-storage case study.

Produces three hourly time series over 2024-01-01 through 2025-12-31 (2 full years,
17,544 hours):

  - data/raw/sites.csv        static site metadata (5 sites: 3 solar, 2 onshore wind)
  - data/raw/generation.csv   hourly generation (MWh) per site
  - data/raw/market.csv       hourly national demand (MW) and day-ahead wholesale
                               price (GBP/MWh)

The data is entirely simulated but built to reproduce two well-documented, real-world
dynamics in renewable-heavy power markets:

  1. "Merit order" price formation: price rises with demand and falls as aggregate
     renewable output rises, including genuine negative-price events when renewable
     output is high and demand is low.
  2. "Cannibalisation" / capture-price erosion: because solar output is concentrated
     around midday, and midday is exactly when aggregate solar output (and therefore
     price suppression) is highest, solar generators structurally receive a lower
     volume-weighted price than the simple average market price. Wind, being spread
     more evenly across day and night and stronger in autumn/winter, is less exposed
     to this effect. This gap is the entire commercial premise of the case study.

Random seed is fixed for reproducibility.
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

START = pd.Timestamp("2024-01-01 00:00:00")
END = pd.Timestamp("2025-12-31 23:00:00")
TS = pd.date_range(START, END, freq="h")
N = len(TS)
print(f"Generating {N:,} hourly timestamps from {START.date()} to {END.date()}")

hour = TS.hour.values
doy = TS.dayofyear.values
year = TS.year.values
dow = TS.dayofweek.values  # 0=Mon
is_weekend = (dow >= 5).astype(float)

# Fraction of the year, used for smooth seasonal curves (peaks at summer solstice ~day 172)
season = np.sin(2 * np.pi * (doy - 80) / 365.25)          # +1 around late June, -1 around late Dec
season_wind = np.sin(2 * np.pi * (doy - 260) / 365.25)     # +1 around mid-Nov, -1 around mid-May (wind stronger in autumn/winter)

# ---------------------------------------------------------------------------
# 1. SITES
# ---------------------------------------------------------------------------
sites = pd.DataFrame([
    {"site_id": "SOLAR-01", "site_name": "Solent Solar Park",   "technology": "Solar", "region": "South Coast", "capacity_mw": 45, "base_capacity_factor": 0.115},
    {"site_id": "SOLAR-02", "site_name": "Fenland Solar Array", "technology": "Solar", "region": "East",        "capacity_mw": 38, "base_capacity_factor": 0.108},
    {"site_id": "SOLAR-03", "site_name": "Dee Solar Farm",      "technology": "Solar", "region": "West",        "capacity_mw": 30, "base_capacity_factor": 0.095},
    {"site_id": "WIND-01",  "site_name": "Pennine Wind Farm",   "technology": "Wind",  "region": "North",       "capacity_mw": 60, "base_capacity_factor": 0.305},
    {"site_id": "WIND-02",  "site_name": "Cambria Wind Farm",   "technology": "Wind",  "region": "Wales",       "capacity_mw": 52, "base_capacity_factor": 0.275},
])
sites.to_csv("data/raw/sites.csv", index=False)
print("Wrote data/raw/sites.csv")
print(sites.to_string(index=False))

# ---------------------------------------------------------------------------
# 2. DEMAND (national, GW-scale but expressed in MW for consistency)
# ---------------------------------------------------------------------------
# Daily shape: two peaks (morning ~08:00, evening ~18:00), trough overnight
daily_shape = (
    0.55
    + 0.30 * np.exp(-((hour - 8) ** 2) / (2 * 2.4 ** 2))
    + 0.38 * np.exp(-((hour - 18) ** 2) / (2 * 2.6 ** 2))
    - 0.18 * np.exp(-((hour - 4) ** 2) / (2 * 2.0 ** 2))
)
weekend_reduction = 1 - 0.13 * is_weekend
winter_heating_uplift = 1 + 0.22 * (-season)  # higher demand in winter (heating), lower in summer
demand_noise = RNG.normal(0, 0.015, N)

base_demand_mw = 32000  # roughly a mid-size national grid, illustrative only
demand_mw = (
    base_demand_mw
    * daily_shape
    * weekend_reduction
    * winter_heating_uplift
    * (1 + demand_noise)
)
demand_mw = np.clip(demand_mw, 14000, None)

# ---------------------------------------------------------------------------
# 3. GENERATION — solar
# ---------------------------------------------------------------------------
# Day length varies seasonally; sunrise/sunset approximated with a cosine model
day_length = 12 + 4.4 * season  # hours of daylight, ~7.6h midwinter to ~16.4h midsummer
sunrise = 12 - day_length / 2
sunset = 12 + day_length / 2
daylight = (hour >= sunrise) & (hour <= sunset)
sun_angle = np.where(
    daylight,
    np.sin(np.pi * (hour - sunrise) / np.maximum(day_length, 0.1)),
    0.0,
)
sun_angle = np.clip(sun_angle, 0, None)

# Autocorrelated daily "cloudiness" factor shared across all solar sites but with
# site-specific noise layered on top, so sites are correlated but not identical.
n_days = int(np.ceil(N / 24))
cloud_state = np.zeros(n_days)
c = 0.85
for d in range(1, n_days):
    cloud_state[d] = np.clip(cloud_state[d - 1] * 0.7 + RNG.normal(0, 0.35), -1.4, 1.0)
cloud_factor_hourly = np.repeat(1 - 0.32 * np.clip(cloud_state, -0.5, 1.0), 24)[:N]

def solar_generation(capacity_mw, base_cf):
    # Scale sun_angle so that, averaged over daylight hours across the year, output
    # matches the site's target annual base capacity factor.
    site_noise = 1 + RNG.normal(0, 0.05, N)
    raw = capacity_mw * sun_angle * cloud_factor_hourly * site_noise
    raw = np.clip(raw, 0, capacity_mw)
    # Calibrate to target capacity factor
    scale = (base_cf * capacity_mw) / max(raw.mean(), 1e-6)
    return np.clip(raw * scale, 0, capacity_mw)

# ---------------------------------------------------------------------------
# 4. GENERATION — wind (mean-reverting wind-speed process -> cubic-ish power curve)
# ---------------------------------------------------------------------------
def wind_generation(capacity_mw, base_cf, seed_offset):
    rng = np.random.default_rng(42 + seed_offset)
    speed = np.zeros(N)
    speed[0] = 8.0
    seasonal_mean = 8.0 + 2.6 * season_wind
    for t in range(1, N):
        theta = 0.06
        speed[t] = speed[t - 1] + theta * (seasonal_mean[t] - speed[t - 1]) + rng.normal(0, 0.9)
    speed = np.clip(speed, 0, 32)

    cut_in, rated, cut_out = 3.5, 13.0, 25.0
    power_frac = np.zeros(N)
    ramp = (speed >= cut_in) & (speed < rated)
    power_frac[ramp] = ((speed[ramp] - cut_in) / (rated - cut_in)) ** 3
    power_frac[(speed >= rated) & (speed < cut_out)] = 1.0
    power_frac[speed >= cut_out] = 0.0  # safety cut-out at very high wind speed

    raw = capacity_mw * power_frac
    scale = (base_cf * capacity_mw) / max(raw.mean(), 1e-6)
    return np.clip(raw * scale, 0, capacity_mw), speed

gen_frames = []
for _, s in sites.iterrows():
    if s["technology"] == "Solar":
        mwh = solar_generation(s["capacity_mw"], s["base_capacity_factor"])
    else:
        seed_off = {"WIND-01": 1, "WIND-02": 2}[s["site_id"]]
        mwh, _ = wind_generation(s["capacity_mw"], s["base_capacity_factor"], seed_off)
    gen_frames.append(pd.DataFrame({
        "timestamp": TS, "site_id": s["site_id"], "generation_mwh": np.round(mwh, 2),
    }))

generation = pd.concat(gen_frames, ignore_index=True)
generation.to_csv("data/raw/generation.csv", index=False)
print(f"Wrote data/raw/generation.csv ({len(generation):,} rows)")

cf_check = (
    generation.merge(sites, on="site_id")
    .groupby(["site_id", "site_name", "capacity_mw"])["generation_mwh"]
    .mean()
    .reset_index()
)
cf_check["realised_capacity_factor"] = (cf_check["generation_mwh"] / cf_check["capacity_mw"]).round(3)
print(cf_check[["site_name", "realised_capacity_factor"]].to_string(index=False))

# ---------------------------------------------------------------------------
# 5. PRICE — merit-order model: rises with demand, falls with aggregate renewable
#    output (fleet-wide, not just our 5 sample sites — scaled up to represent the
#    wider national renewable fleet these 5 sites are a sample of).
# ---------------------------------------------------------------------------
gen_wide = generation.merge(sites[["site_id", "technology"]], on="site_id")
solar_gen_by_ts = gen_wide[gen_wide["technology"] == "Solar"].groupby("timestamp")["generation_mwh"].sum().reindex(TS).fillna(0).values
wind_gen_by_ts = gen_wide[gen_wide["technology"] == "Wind"].groupby("timestamp")["generation_mwh"].sum().reindex(TS).fillna(0).values

# Our sample sites represent a small slice of the national solar and wind fleets.
# Solar's fleet-wide simultaneity (everyone generates at once, at midday) makes its
# price suppression effect sharper per MW than wind's, which is more spread out.
national_solar_mw = solar_gen_by_ts / 0.010
national_wind_mw = wind_gen_by_ts / 0.020
national_renewable_mw = national_solar_mw + national_wind_mw

demand_price_component = 34 + 0.0021 * (demand_mw - 20000)
renewable_suppression = 0.0044 * national_solar_mw + 0.0021 * national_wind_mw
gas_price_shock_days = RNG.choice(n_days, size=max(1, n_days // 45), replace=False)
gas_shock_hourly = np.isin(np.arange(n_days).repeat(24)[:N], gas_price_shock_days).astype(float)
gas_shock_component = gas_shock_hourly * RNG.uniform(18, 55, N)

price_noise = RNG.normal(0, 4.2, N)
price = demand_price_component - renewable_suppression + gas_shock_component + price_noise
price = np.clip(price, -60, 420)  # allow genuine negative pricing events

market = pd.DataFrame({
    "timestamp": TS,
    "demand_mw": np.round(demand_mw, 1),
    "price_gbp_per_mwh": np.round(price, 2),
    "national_renewable_output_mw": np.round(national_renewable_mw, 1),
})
market.to_csv("data/raw/market.csv", index=False)
print(f"Wrote data/raw/market.csv ({len(market):,} rows)")
print(f"Mean price: £{market['price_gbp_per_mwh'].mean():.2f}/MWh | "
      f"Negative-price hours: {(market['price_gbp_per_mwh'] < 0).sum():,} "
      f"({(market['price_gbp_per_mwh'] < 0).mean()*100:.2f}%)")

# Quick sanity check on the core hypothesis: solar capture rate vs wind capture rate
merged = generation.merge(market[["timestamp", "price_gbp_per_mwh"]], on="timestamp").merge(sites, on="site_id")
avg_price = market["price_gbp_per_mwh"].mean()
capture = (
    merged.groupby(["site_id", "site_name", "technology"])
    .apply(lambda g: pd.Series({
        "capture_price": (g["generation_mwh"] * g["price_gbp_per_mwh"]).sum() / g["generation_mwh"].sum(),
    }), include_groups=False)
    .reset_index()
)
capture["capture_rate_pct"] = (capture["capture_price"] / avg_price * 100).round(1)
print(f"\nSimple average market price: £{avg_price:.2f}/MWh")
print(capture[["site_name", "technology", "capture_price", "capture_rate_pct"]].to_string(index=False))
