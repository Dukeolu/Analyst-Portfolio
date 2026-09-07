"""
Simulates a "specialist-first, capacity-constrained" routing policy against
the observed 26-week ticket history, as a counterfactual for what skill-based
routing could realistically recover -- not an idealized 100%-match ceiling.

Method: each category's specialist technicians are assumed to have a stated,
disclosed weekly capacity for ticket work (default 30 hours/week/tech, after
meetings and project time -- a reasonable assumption for a help-desk tech,
not derived from this data). Currently-matched tickets consume that capacity
first (since they're already being handled by a specialist). Any capacity
left over is used to convert some currently-*mismatched* tickets in that
category to a specialist-quality outcome, drawing their resolution hours
from the empirical distribution of that category's actual matched tickets
(so the simulated outcome reflects real observed specialist performance, not
a formula). Once a category's specialist capacity is exhausted, the
remaining mismatched tickets in that category are left as observed --
this is what "overflow to round robin when specialists are busy" means in
practice, and it is why this counterfactual recovers less than the full
mismatch-penalty ceiling reported in the SQL/notebook analysis.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(11)


def simulate_specialist_first_routing(tickets: pd.DataFrame, technicians: pd.DataFrame,
                                       capacity_hours_per_week: float = 30.0,
                                       n_weeks: float = 26.0) -> pd.DataFrame:
    spec_map = {r.tech_id: set(r.specialty_categories.split(";")) for r in technicians.itertuples()}
    tickets = tickets.copy()
    tickets["matched"] = tickets.apply(lambda r: r.category in spec_map[r.assigned_tech_id], axis=1)
    tickets["sim_resolution_hours"] = tickets["resolution_hours"]
    tickets["sim_converted"] = False

    n_specialists_by_cat = {}
    for cat in tickets["category"].unique():
        n_specialists_by_cat[cat] = sum(cat in specs for specs in spec_map.values())

    summary_rows = []
    for cat, group in tickets.groupby("category"):
        n_spec = n_specialists_by_cat[cat]
        total_capacity_hours = capacity_hours_per_week * n_spec * n_weeks

        matched_mask = group["matched"]
        matched_hours_used = group.loc[matched_mask, "resolution_hours"].sum()
        matched_pool = group.loc[matched_mask, "resolution_hours"].values
        if len(matched_pool) == 0:
            matched_pool = np.array([group["resolution_hours"].median()])

        remaining_capacity = max(total_capacity_hours - matched_hours_used, 0.0)

        mismatched_idx = group.index[~matched_mask].tolist()
        RNG.shuffle(mismatched_idx)

        converted = []
        used = 0.0
        for idx in mismatched_idx:
            draw = RNG.choice(matched_pool)
            if used + draw <= remaining_capacity:
                tickets.loc[idx, "sim_resolution_hours"] = draw
                tickets.loc[idx, "sim_converted"] = True
                converted.append(idx)
                used += draw
            # else: stays mismatched (overflow), unchanged

        summary_rows.append({
            "category": cat,
            "n_specialists": n_spec,
            "total_capacity_hours_26wk": round(total_capacity_hours, 1),
            "matched_hours_used": round(matched_hours_used, 1),
            "n_mismatched_tickets": len(mismatched_idx),
            "n_converted_to_specialist": len(converted),
            "pct_of_mismatched_converted": round(100 * len(converted) / max(len(mismatched_idx), 1), 1),
        })

    tickets["sim_resolved_at"] = pd.to_datetime(tickets["created_at"]) + pd.to_timedelta(
        tickets["sim_resolution_hours"], unit="h")
    tickets["sim_sla_breached"] = tickets["sim_resolution_hours"] > tickets["sla_target_hours"]

    capacity_summary = pd.DataFrame(summary_rows)
    return tickets, capacity_summary


if __name__ == "__main__":
    tickets = pd.read_csv("data/raw/tickets.csv")
    technicians = pd.read_csv("data/raw/technicians.csv")
    sim, cap_summary = simulate_specialist_first_routing(tickets, technicians)

    print(cap_summary.to_string(index=False))
    print()
    actual_hours = tickets["resolution_hours"].sum()
    sim_hours = sim["sim_resolution_hours"].sum()
    hours_saved_26wk = actual_hours - sim_hours
    print(f"Actual total hours (26wk): {actual_hours:.1f}")
    print(f"Simulated total hours under specialist-first routing (26wk): {sim_hours:.1f}")
    print(f"Hours saved (26wk): {hours_saved_26wk:.1f}")
    print(f"Hours saved (annualized, x2): {hours_saved_26wk * 2:.1f}")
    print(f"Cost avoided annualized @ $45/hr: ${hours_saved_26wk * 2 * 45:,.0f}")
    print()
    print(f"Actual SLA compliance: {(1 - tickets['sla_breached'].mean()) * 100:.1f}%")
    print(f"Simulated SLA compliance: {(1 - sim['sim_sla_breached'].mean()) * 100:.1f}%")
