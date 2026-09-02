"""
Shared simulation library for Case 04 (HR & People Operations).

Two linked mechanisms, both simulated rather than assigned directly:
1. A recruiting funnel (applied -> screened -> interviewed -> offered ->
   hired) by department x channel x month, with stage conversion rates
   that vary by channel and one deliberately bottlenecked department x
   channel combo.
2. Employee-level voluntary attrition, simulated month-by-month, where
   hires from the weakest channel carry elevated early-tenure risk --
   linking funnel quality to retention outcomes, not just headcount.

No demographic attributes (age, gender, etc.) are modeled -- attrition
risk here is driven entirely by structural/business factors: department,
compensation-to-market ratio, overtime load, manager span, engagement,
performance, and hiring channel.
"""
import numpy as np
import pandas as pd

ANALYSIS_DATE = pd.Timestamp("2025-12-31")
DEPARTMENTS = ["Sales", "Customer Support", "Warehouse & Ops", "Engineering", "Finance & Accounting", "Marketing"]
CHANNELS = ["Job Board", "Employee Referral", "Agency", "Campus", "Internal Transfer"]
LEVELS = ["Entry", "Mid", "Senior", "Manager"]

# Funnel stage conversion rates by channel (applied->screened->interviewed->offered->hired)
CHANNEL_FUNNEL = {
    "Job Board":          dict(screen=0.38, interview=0.55, offer=0.60, accept=0.78),
    "Employee Referral":  dict(screen=0.72, interview=0.75, offer=0.72, accept=0.90),
    "Agency":             dict(screen=0.65, interview=0.60, offer=0.68, accept=0.82),
    "Campus":             dict(screen=0.55, interview=0.58, offer=0.55, accept=0.75),
    "Internal Transfer":  dict(screen=0.90, interview=0.85, offer=0.80, accept=0.88),
}
# the seeded bottleneck: Warehouse & Ops screening backlog cuts Job Board's
# screen->interview conversion hard, on top of Job Board's already-weak baseline
SCREENING_BOTTLENECK = {("Warehouse & Ops", "Job Board"): 0.55}  # multiplier on 'interview' rate

APPLIED_VOLUME = {  # baseline monthly applications by channel
    "Job Board": 140, "Employee Referral": 35, "Agency": 45, "Campus": 25, "Internal Transfer": 15,
}
CHANNEL_MIX_BY_DEPT = {  # relative applied-volume weight by department (mostly even, Warehouse skews Job Board)
    "Warehouse & Ops": {"Job Board": 1.8, "Employee Referral": 0.6, "Agency": 0.8, "Campus": 0.5, "Internal Transfer": 0.4},
}

MONTHS = pd.period_range("2024-01", periods=24, freq="M")

# early-tenure attrition multiplier by channel -- the fit/expectations-setting effect
CHANNEL_EARLY_RISK = {"Job Board": 1.9, "Agency": 1.3, "Campus": 1.2, "Employee Referral": 0.7, "Internal Transfer": 0.6}


def build_recruiting_funnel(seed: int = 41) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for dept in DEPARTMENTS:
        mix = CHANNEL_MIX_BY_DEPT.get(dept, {c: 1.0 for c in CHANNELS})
        for channel in CHANNELS:
            rates = CHANNEL_FUNNEL[channel]
            weight = mix.get(channel, 1.0)
            for m in MONTHS:
                applied = max(0, int(rng.poisson(APPLIED_VOLUME[channel] / len(DEPARTMENTS) * weight)))
                screen_rate = np.clip(rng.normal(rates["screen"], 0.04), 0.05, 0.98)
                interview_rate = np.clip(rng.normal(rates["interview"], 0.04), 0.05, 0.98)
                if (dept, channel) in SCREENING_BOTTLENECK:
                    interview_rate *= SCREENING_BOTTLENECK[(dept, channel)]
                offer_rate = np.clip(rng.normal(rates["offer"], 0.04), 0.05, 0.98)
                accept_rate = np.clip(rng.normal(rates["accept"], 0.04), 0.05, 0.98)

                screened = int(round(applied * screen_rate))
                interviewed = int(round(screened * interview_rate))
                offered = int(round(interviewed * offer_rate))
                hired = int(round(offered * accept_rate))

                rows.append({
                    "month": str(m), "department": dept, "channel": channel,
                    "applied": applied, "screened": screened, "interviewed": interviewed,
                    "offered": offered, "hired": hired,
                })
    return pd.DataFrame(rows)


def build_employee_base(funnel: pd.DataFrame, seed: int = 43) -> pd.DataFrame:
    """One row per hire drawn from the funnel's monthly hired counts, with
    department/channel/level/comp/overtime/engagement attributes."""
    rng = np.random.default_rng(seed)
    rows = []
    emp_n = 1
    for r in funnel.itertuples(index=False):
        for _ in range(r.hired):
            level = rng.choice(LEVELS, p=[0.45, 0.32, 0.16, 0.07])
            comp_ratio = np.clip(rng.normal(1.0 if level != "Entry" else 0.96, 0.09), 0.75, 1.35)
            manager_span = max(3, int(rng.normal(9 if r.department == "Warehouse & Ops" else 7, 2.5)))
            overtime_hours = max(0, rng.normal(14 if r.department == "Warehouse & Ops" else 5, 6))
            base_engagement = np.clip(rng.normal(66, 16), 5, 100)
            rows.append({
                "employee_id": f"EMP-{emp_n:05d}",
                "hire_month": r.month, "department": r.department, "channel": r.channel, "level": level,
                "comp_ratio": round(comp_ratio, 3), "manager_span": manager_span,
                "overtime_hours_monthly": round(overtime_hours, 1), "base_engagement": base_engagement,
            })
            emp_n += 1
    return pd.DataFrame(rows)


def simulate_attrition(employees: pd.DataFrame, seed: int = 47) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for e in employees.itertuples(index=False):
        months_available = (ANALYSIS_DATE.to_period("M") - pd.Period(e.hire_month)).n
        engagement_hist = []
        terminated, tenure = False, 0
        for t in range(1, max(1, months_available) + 1):
            month_engagement = float(np.clip(rng.normal(e.base_engagement, 7), 0, 100))
            engagement_hist.append(month_engagement)

            base_hazard = 0.014
            tenure_factor = (2.4 if t <= 3 else (1.3 if t <= 6 else (0.9 if t <= 18 else 0.75)))
            channel_early_factor = CHANNEL_EARLY_RISK[e.channel] if t <= 3 else (1 + (CHANNEL_EARLY_RISK[e.channel] - 1) * 0.3)
            comp_factor = 1 + max(0.0, (0.95 - e.comp_ratio)) * 3.5
            overtime_factor = 1 + max(0.0, (e.overtime_hours_monthly - 8)) / 30
            span_factor = 1 + max(0.0, (e.manager_span - 8)) / 25
            engagement_factor = 1 + max(0.0, (55 - month_engagement)) / 45

            hazard = min(0.30, base_hazard * tenure_factor * channel_early_factor * comp_factor * overtime_factor * span_factor * engagement_factor)
            tenure = t
            if rng.random() < hazard:
                terminated = True
                break

        avg_engagement = float(np.mean(engagement_hist)) if engagement_hist else e.base_engagement
        rows.append({
            "employee_id": e.employee_id, "hire_month": e.hire_month, "department": e.department,
            "channel": e.channel, "level": e.level, "comp_ratio": e.comp_ratio,
            "manager_span": e.manager_span, "overtime_hours_monthly": e.overtime_hours_monthly,
            "avg_engagement_score": round(avg_engagement, 1),
            "tenure_months": tenure, "months_observable": max(1, months_available),
            "terminated_voluntary": "Yes" if terminated else "No",
        })
    return pd.DataFrame(rows)
