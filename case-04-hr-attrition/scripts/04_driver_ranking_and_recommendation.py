"""
Case 04 -- Step 4: the actual "solution" step.

1. Logistic regression ranks what actually predicts voluntary attrition,
   holding the other structural factors constant (same technique as
   Case 02, appropriate again here since it's the same underlying
   problem shape: binary outcome, mixed categorical/continuous drivers).
2. Reproduces the Excel workbook's two $ scenarios in Python so the
   dashboard and README have a single, cross-checked source of numbers:
   the early-attrition cost of Job Board vs. Employee Referral, and the
   Warehouse & Ops x Job Board screening-bottleneck's wasted recruiter effort.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

emp = pd.read_csv(RAW / "employees.csv")
funnel = pd.read_csv(RAW / "recruiting_funnel.csv")

# ---------------------------------------------------------------- 1. driver ranking
# Predicting whether an employee has voluntarily terminated at any point in their
# observed tenure. Tenure itself is deliberately excluded from the features: it's
# mechanically entangled with the outcome (a terminated employee's tenure *is* how
# long until they left), so including it would make the model tautological rather
# than predictive -- the point is to rank the *structural* factors HR can act on.
model_df = emp.copy()
model_df["terminated_flag"] = (model_df["terminated_voluntary"] == "Yes").astype(int)

numeric_features = ["comp_ratio", "manager_span", "overtime_hours_monthly", "avg_engagement_score"]
cat_features = ["department", "channel", "level"]

X = pd.get_dummies(model_df[numeric_features + cat_features], columns=cat_features, drop_first=True)
y = model_df["terminated_flag"]
feature_names = X.columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_s, y_train)
auc = roc_auc_score(y_test, clf.predict_proba(X_test_s)[:, 1])

driver_ranking = pd.DataFrame({
    "feature": feature_names,
    "standardized_coefficient": clf.coef_[0],
}).assign(
    direction=lambda d: np.where(d["standardized_coefficient"] > 0, "raises attrition risk", "lowers attrition risk"),
    abs_effect=lambda d: d["standardized_coefficient"].abs(),
).sort_values("abs_effect", ascending=False).drop(columns="abs_effect")
driver_ranking.to_csv(PROCESSED / "driver_ranking.csv", index=False)
pd.DataFrame([{"test_auc": round(auc, 3), "n_train": len(X_train), "n_test": len(X_test)}]).to_csv(PROCESSED / "model_metadata.csv", index=False)

# ---------------------------------------------------------------- 2a. early-attrition cost by channel
REPLACEMENT_COST = 9000
early = emp[emp["terminated_voluntary"] == "Yes"]
early_by_channel = pd.DataFrame({
    "hires": emp.groupby("channel").size(),
    "early_departures": early[early["tenure_months"] <= 3].groupby("channel").size(),
}).fillna(0)
early_by_channel["early_attrition_rate"] = early_by_channel["early_departures"] / early_by_channel["hires"]
early_by_channel["cost_of_early_attrition"] = early_by_channel["early_departures"] * REPLACEMENT_COST
early_by_channel = early_by_channel.reset_index().rename(columns={"index": "channel"})
early_by_channel.to_csv(PROCESSED / "early_attrition_by_channel.csv", index=False)

jb = early_by_channel.set_index("channel").loc["Job Board"]
ref_rate = early_by_channel.set_index("channel").loc["Employee Referral", "early_attrition_rate"]
implied_departures = jb["hires"] * ref_rate
departures_avoided = jb["early_departures"] - implied_departures
annual_savings_channel_mix = departures_avoided * REPLACEMENT_COST / 2  # 24mo -> annualized

# ---------------------------------------------------------------- 2b. screening-bottleneck cost
SCREEN_COST = 35  # recruiter/hiring-manager time per screened candidate reviewed for interview
wo_jb = funnel[(funnel.department == "Warehouse & Ops") & (funnel.channel == "Job Board")]
jb_all = funnel[funnel.channel == "Job Board"]
wo_jb_interview_rate = wo_jb["interviewed"].sum() / wo_jb["screened"].sum()
jb_overall_interview_rate = jb_all["interviewed"].sum() / jb_all["screened"].sum()
# candidates screened at Warehouse & Ops who, at the network's normal Job Board conversion,
# should have converted to an interview but didn't -- wasted screening effort with no output
missed_interviews = wo_jb["screened"].sum() * (jb_overall_interview_rate - wo_jb_interview_rate)
wasted_screening_cost_24mo = wo_jb["screened"].sum() * SCREEN_COST  # cost of running the pipeline at all
annual_missed_interviews = missed_interviews / 2

recommendation = pd.DataFrame([{
    "job_board_hires_24mo": int(jb["hires"]),
    "job_board_early_attrition_rate": round(jb["early_attrition_rate"], 4),
    "referral_early_attrition_rate": round(ref_rate, 4),
    "departures_avoided_24mo": round(departures_avoided, 1),
    "annual_savings_channel_mix": round(annual_savings_channel_mix, 0),
    "wo_jobboard_interview_rate": round(wo_jb_interview_rate, 4),
    "jobboard_overall_interview_rate": round(jb_overall_interview_rate, 4),
    "annual_missed_interviews_wo_bottleneck": round(annual_missed_interviews, 1),
}])
recommendation.to_csv(PROCESSED / "recommendation_summary.csv", index=False)

print(f"Model: test AUC={auc:.3f} (n_train={len(X_train)}, n_test={len(X_test)})")
print("\nTop attrition drivers:")
print(driver_ranking.head(8).to_string(index=False))
print("\nRecommendation summary:")
print(recommendation.T)
