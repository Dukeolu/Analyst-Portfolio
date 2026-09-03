"""
Battery arbitrage model for the Meridian Renewables case study.

Models a battery co-located with (behind the meter of) a single renewable site:
it can only charge from that site's own metered generation, never from the
grid, and it discharges back to the grid connection at a later hour the same
day. This is the commercially realistic case for a co-located storage asset
paired with an existing generation connection.

Simplifying assumptions (stated explicitly as limitations in the README):
  - Perfect day-ahead price foresight (the simulation picks the objectively
    cheapest hours to charge and priciest hours to discharge each day).
  - A single charge/discharge cycle per calendar day.
  - Round-trip efficiency applied on the discharge side.
  - No degradation modelled in year 1 economics; a capacity-fade schedule is
    applied separately in the NPV model for later years.
"""

import numpy as np
import pandas as pd


def simulate_battery_for_site(gen_price_df: pd.DataFrame, power_mw: float = 10.0,
                               energy_mwh: float = 20.0, efficiency: float = 0.88) -> pd.DataFrame:
    """
    gen_price_df: hourly DataFrame for ONE site with columns
      ['timestamp', 'generation_mwh', 'price_gbp_per_mwh']
    Returns a per-day summary DataFrame with charge/discharge MWh and £ uplift.
    """
    df = gen_price_df.copy()
    df["date"] = df["timestamp"].dt.date
    max_hours_per_cycle = int(np.ceil(energy_mwh / power_mw))  # e.g. 20/10 = 2 hours

    records = []
    for date, day in df.groupby("date"):
        day_by_price_asc = day.sort_values("price_gbp_per_mwh")

        # --- Charging: cheapest hours first, limited by generation available,
        #     battery power rating, and remaining energy headroom ---
        remaining_energy = energy_mwh
        charge_rows = []          # (index, price, amount)
        charged_idx = set()
        for idx, row in day_by_price_asc.iterrows():
            if remaining_energy <= 0 or len(charge_rows) >= max_hours_per_cycle:
                break
            charge_amt = min(power_mw, row["generation_mwh"], remaining_energy)
            if charge_amt <= 0:
                continue
            charge_rows.append((idx, row["price_gbp_per_mwh"], charge_amt))
            charged_idx.add(idx)
            remaining_energy -= charge_amt

        total_charged = sum(a for _, _, a in charge_rows)
        if total_charged <= 0:
            records.append({"date": date, "charged_mwh": 0.0, "discharged_mwh": 0.0,
                             "charge_cost_gbp": 0.0, "discharge_revenue_gbp": 0.0, "uplift_gbp": 0.0})
            continue
        charge_cost = sum(p * a for _, p, a in charge_rows)

        # --- Discharging: priciest hours first (excluding hours already used
        #     to charge), limited by power rating and energy available after
        #     round-trip efficiency losses ---
        available_to_discharge = total_charged * efficiency
        day_by_price_desc = day.sort_values("price_gbp_per_mwh", ascending=False)
        discharge_rows = []
        remaining_discharge = available_to_discharge
        for idx, row in day_by_price_desc.iterrows():
            if remaining_discharge <= 0 or len(discharge_rows) >= max_hours_per_cycle:
                break
            if idx in charged_idx:
                continue
            dis_amt = min(power_mw, remaining_discharge)
            discharge_rows.append((row["price_gbp_per_mwh"], dis_amt))
            remaining_discharge -= dis_amt

        total_discharged = sum(a for _, a in discharge_rows)
        discharge_revenue = sum(p * a for p, a in discharge_rows)
        uplift = discharge_revenue - charge_cost

        records.append({
            "date": date, "charged_mwh": total_charged, "discharged_mwh": total_discharged,
            "charge_cost_gbp": charge_cost, "discharge_revenue_gbp": discharge_revenue,
            "uplift_gbp": uplift,
        })

    return pd.DataFrame(records)
