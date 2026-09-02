"""
Case 02 -- Step 3: the actual "solution" step.

Three things happen here:
1. Cohort retention curves by contract type -- how much of the "MTM churns
   way more" story is really just a tenure-stage effect vs. a structural one.
2. A logistic regression trained to separate churners from non-churners,
   used the way analysts actually use it -- not to worship the AUC, but to
   rank which features move the needle, holding the others constant.
3. Score every *currently active* customer, target the riskiest 20%, and
   cost out a retention campaign against a plausible save rate -- so the
   recommendation is a number a VP of Sales can approve or reject, not
   just "these people might leave."
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

df = pd.read_csv(RAW / "customers.csv")

# ---------------------------------------------------------------- 1. cohort retention curves
HORIZONS = [1, 3, 6, 12, 18, 24]
rows = []
for contract in df["contract_type"].unique():
    sub = df[df["contract_type"] == contract]
    for h in HORIZONS:
        eligible = sub[sub["months_observable"] >= h]
        if len(eligible) < 30:
            continue
        retained = (eligible["tenure_months"] >= h).sum()
        rows.append({
            "contract_type": contract, "horizon_months": h,
            "eligible_customers": len(eligible), "retained_customers": int(retained),
            "retention_rate": round(retained / len(eligible), 4),
        })
retention_curve = pd.DataFrame(rows).sort_values(["contract_type", "horizon_months"])
retention_curve.to_csv(PROCESSED / "retention_curve.csv", index=False)

# ---------------------------------------------------------------- 2. logistic regression driver ranking
model_df = df.copy()
model_df["churned_flag"] = (model_df["churned"] == "Yes").astype(int)
model_df["autopay_flag"] = (model_df["autopay"] == "Yes").astype(int)

numeric_features = ["addon_count", "monthly_charge", "avg_engagement_score", "support_tickets_90d", "autopay_flag"]
cat_features = ["contract_type", "signup_channel", "region"]

X = pd.get_dummies(model_df[numeric_features + cat_features], columns=cat_features, drop_first=True)
y = model_df["churned_flag"]
feature_names = X.columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_s, y_train)

auc = roc_auc_score(y_test, clf.predict_proba(X_test_s)[:, 1])
acc = accuracy_score(y_test, clf.predict(X_test_s))

driver_ranking = pd.DataFrame({
    "feature": feature_names,
    "standardized_coefficient": clf.coef_[0],
}).assign(
    direction=lambda d: np.where(d["standardized_coefficient"] > 0, "raises churn risk", "lowers churn risk"),
    abs_effect=lambda d: d["standardized_coefficient"].abs(),
).sort_values("abs_effect", ascending=False).drop(columns="abs_effect")
driver_ranking.to_csv(PROCESSED / "driver_ranking.csv", index=False)

model_meta = pd.DataFrame([{"test_auc": round(auc, 3), "test_accuracy": round(acc, 3), "n_train": len(X_train), "n_test": len(X_test)}])
model_meta.to_csv(PROCESSED / "model_metadata.csv", index=False)

# ---------------------------------------------------------------- 3. score active customers, size the retention offer
X_all_s = scaler.transform(X)
model_df["churn_probability"] = clf.predict_proba(X_all_s)[:, 1]

active = model_df[model_df["churned"] == "No"].copy()
threshold = active["churn_probability"].quantile(0.80)  # target the riskiest 20%
high_risk = active[active["churn_probability"] >= threshold].copy()

CONTACT_COST = 12.0          # per customer contacted (agent time)
SAVE_RATE = 0.28             # share of true would-be churners a proactive campaign retains (industry benchmark range 20-35%)
DISCOUNT_MONTHS_EQUIV = 0.6  # avg discount cost per saved customer, in months of their own charge

avg_monthly_charge_hr = high_risk["monthly_charge"].mean()
avg_prob_hr = high_risk["churn_probability"].mean()

expected_saves = len(high_risk) * avg_prob_hr * SAVE_RATE
revenue_protected_annual = expected_saves * avg_monthly_charge_hr * 12
campaign_cost = len(high_risk) * CONTACT_COST + expected_saves * (avg_monthly_charge_hr * DISCOUNT_MONTHS_EQUIV)
net_benefit = revenue_protected_annual - campaign_cost

roi = pd.DataFrame([{
    "active_customers": len(active),
    "high_risk_customers_targeted": len(high_risk),
    "avg_predicted_churn_prob_high_risk": round(avg_prob_hr, 3),
    "monthly_revenue_at_risk": round(high_risk["monthly_charge"].sum(), 2),
    "annual_revenue_at_risk": round(high_risk["monthly_charge"].sum() * 12, 2),
    "expected_customers_saved": round(expected_saves, 1),
    "expected_annual_revenue_protected": round(revenue_protected_annual, 2),
    "campaign_cost": round(campaign_cost, 2),
    "net_annual_benefit": round(net_benefit, 2),
}])
roi.to_csv(PROCESSED / "retention_offer_roi.csv", index=False)

high_risk_by_segment = high_risk.groupby(["contract_type", "signup_channel"]).agg(
    customers=("customer_id", "count"),
    avg_churn_probability=("churn_probability", "mean"),
    monthly_revenue_at_risk=("monthly_charge", "sum"),
).reset_index().sort_values("monthly_revenue_at_risk", ascending=False)
high_risk_by_segment.to_csv(PROCESSED / "high_risk_by_segment.csv", index=False)

print(f"Model: test AUC={auc:.3f}, accuracy={acc:.3f}  (n_train={len(X_train)}, n_test={len(X_test)})")
print("\nTop churn drivers (standardized logistic regression coefficients):")
print(driver_ranking.head(8).to_string(index=False))
print("\nRetention curve (Month-to-month):")
print(retention_curve[retention_curve.contract_type == "Month-to-month"].to_string(index=False))
print("\nRetention offer ROI:")
print(roi.T)
