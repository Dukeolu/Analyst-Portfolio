"""Quantifies the before/after hardening results: CIS-style control compliance
by category, and attack-surface reduction across 6 concrete metrics."""
import csv
from collections import defaultdict

with open("data/raw/cis_hardening_checklist.csv") as f:
    controls = list(csv.DictReader(f))

with open("data/raw/attack_surface_metrics.csv") as f:
    surface = list(csv.DictReader(f))

total = len(controls)
baseline_pass = sum(1 for c in controls if c["baseline_pass"] == "True")
remediated_pass = sum(1 for c in controls if c["remediated_pass"] == "True")

by_category = defaultdict(lambda: [0, 0, 0])  # total, baseline_pass, remediated_pass
for c in controls:
    cat = c["category"]
    by_category[cat][0] += 1
    by_category[cat][1] += 1 if c["baseline_pass"] == "True" else 0
    by_category[cat][2] += 1 if c["remediated_pass"] == "True" else 0

print("=" * 90)
print(f"CIS-STYLE HARDENING BENCHMARK — {total} controls, ERP/WMS Integration Server")
print("=" * 90)
print(f"Baseline compliance:    {baseline_pass}/{total} ({100*baseline_pass/total:.1f}%)")
print(f"Post-remediation:       {remediated_pass}/{total} ({100*remediated_pass/total:.1f}%)")
print()
print(f"{'Category':<22}{'Baseline':<14}{'Remediated':<14}")
print("-" * 50)
for cat, (tot, base, rem) in by_category.items():
    print(f"{cat:<22}{f'{base}/{tot}':<14}{f'{rem}/{tot}':<14}")

exceptions = [c for c in controls if c["remediated_pass"] == "False"]
print(f"\nRisk-accepted exceptions after remediation: {len(exceptions)}")
for c in exceptions:
    print(f"  {c['control_id']} — {c['description']}")
    print(f"    {c['remediation_action']}")

print()
print("=" * 90)
print("ATTACK SURFACE REDUCTION")
print("=" * 90)
total_reduction_pct = []
for row in surface:
    metric = row["metric"]
    before = int(row["baseline_count"])
    after = int(row["remediated_count"])
    pct = 100 * (1 - after / before) if before > 0 else 0
    total_reduction_pct.append(pct)
    print(f"  {metric:<42}{before:>4} -> {after:<4} ({pct:.0f}% reduction)")

avg_reduction = sum(total_reduction_pct) / len(total_reduction_pct)
print(f"\nAverage reduction across all 6 attack-surface metrics: {avg_reduction:.1f}%")

with open("data/raw/hardening_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["metric", "value"])
    writer.writerow(["total_controls", total])
    writer.writerow(["baseline_pass", baseline_pass])
    writer.writerow(["baseline_pass_pct", round(100 * baseline_pass / total, 1)])
    writer.writerow(["remediated_pass", remediated_pass])
    writer.writerow(["remediated_pass_pct", round(100 * remediated_pass / total, 1)])
    writer.writerow(["risk_accepted_exceptions", len(exceptions)])
    writer.writerow(["avg_attack_surface_reduction_pct", round(avg_reduction, 1)])

print("\nWrote data/raw/hardening_summary.csv")
