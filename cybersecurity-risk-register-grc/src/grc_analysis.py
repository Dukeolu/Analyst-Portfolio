"""
Rolls the risk register up into portfolio-level GRC metrics: overall risk
reduction, CSF function coverage, status breakdown, and a prioritized list
of the highest-residual-risk items still open.
"""
import csv
from collections import defaultdict

with open("data/raw/risk_register.csv") as f:
    risks = list(csv.DictReader(f))

for r in risks:
    for k in ("inherent_score", "residual_score", "risk_reduction_pct"):
        r[k] = float(r[k])

total_inherent = sum(r["inherent_score"] for r in risks)
total_residual = sum(r["residual_score"] for r in risks)
overall_reduction_pct = round((total_inherent - total_residual) / total_inherent * 100, 1)

status_counts = defaultdict(int)
for r in risks:
    status_counts[r["status"]] += 1

csf_counts = defaultdict(lambda: [0, 0.0])  # [count, residual_score_sum]
for r in risks:
    csf_counts[r["csf_function"]][0] += 1
    csf_counts[r["csf_function"]][1] += r["residual_score"]

open_risks = [r for r in risks if r["status"] in ("Open", "In Progress")]
open_risks_ranked = sorted(open_risks, key=lambda r: -r["residual_score"])

closed_risks = [r for r in risks if r["status"] == "Closed"]
closed_reduction = sum(r["inherent_score"] - r["residual_score"] for r in closed_risks)

print("=" * 78)
print("PORTFOLIO RISK ROLLUP — MERIDIAN MANUFACTURING (SIMULATED)")
print("=" * 78)
print(f"Total risks tracked: {len(risks)}")
print(f"Total inherent risk score: {total_inherent:.0f}")
print(f"Total residual risk score: {total_residual:.0f}")
print(f"Overall risk reduction: {overall_reduction_pct:.1f}%")
print(f"\nRisk points closed by remediated (Closed-status) findings: {closed_reduction:.0f}")

print("\nStatus breakdown:")
for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
    print(f"  {status:<15} {count}")

print("\nResidual risk by NIST CSF 2.0 function:")
for func, (count, score_sum) in sorted(csf_counts.items(), key=lambda x: -x[1][1]):
    print(f"  {func:<10} {count} risks, {score_sum:.0f} residual points")

print(f"\nTop open/in-progress risks by residual score ({len(open_risks_ranked)} total open):")
for r in open_risks_ranked[:6]:
    print(f"  {r['risk_id']}  residual={r['residual_score']:.0f}  {r['title']}")

with open("data/raw/grc_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["metric", "value"])
    writer.writerow(["total_risks", len(risks)])
    writer.writerow(["total_inherent_score", total_inherent])
    writer.writerow(["total_residual_score", total_residual])
    writer.writerow(["overall_reduction_pct", overall_reduction_pct])
    writer.writerow(["closed_count", status_counts["Closed"]])
    writer.writerow(["open_count", status_counts["Open"]])
    writer.writerow(["in_progress_count", status_counts["In Progress"]])
    writer.writerow(["risk_accepted_count", status_counts["Risk Accepted"]])
    writer.writerow(["monitoring_count", status_counts["Monitoring"]])
    writer.writerow(["open_risk_residual_sum", sum(r["residual_score"] for r in open_risks)])

with open("data/raw/csf_coverage.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["csf_function", "risk_count", "residual_score_sum"])
    for func, (count, score_sum) in sorted(csf_counts.items(), key=lambda x: -x[1][1]):
        writer.writerow([func, count, score_sum])

print("\nWrote data/raw/grc_summary.csv and data/raw/csf_coverage.csv")
