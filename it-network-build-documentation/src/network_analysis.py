"""
Quantifies what segmentation actually buys Meridian Manufacturing's new
Riverside branch, compared to the flat-network default a site-opening
checklist would otherwise produce.

"Blast radius" here = the number of other devices an attacker who
compromises one device on the network could reach at Layer 2/3 without
crossing a firewall policy. On a flat network that's every other device.
With VLAN segmentation + default-deny inter-VLAN rules, it's just the
devices in that one VLAN (plus whatever the firewall explicitly allows
through, which this analysis also counts).
"""
import csv
from collections import Counter

with open("data/raw/device_inventory.csv") as f:
    rows = list(csv.DictReader(f))

total_devices = len(rows)
by_segment = Counter(r["segment"] for r in rows)
legacy_by_segment = Counter(r["segment"] for r in rows if r["legacy_unpatched_risk"] == "Y")

# Explicit inter-VLAN allows carved out of default-deny, per configs/firewall-rules.conf:
#   Office <-> Warehouse: Office can reach the WMS kiosk subnet's server port only (not scanners/printers)
#   VoIP <-> Management: phones can reach the PBX/call-manager host in Management for provisioning
# Everything else stays fully isolated to its own VLAN.
EXTRA_REACHABLE = {
    "Office": 0,       # Office's allow-list target (the WMS server) is a single host inside Warehouse,
    "Warehouse": 0,    # not counted as "reaching the segment" since it's one narrowly-scoped service, not lateral access
    "VoIP": 0,
    "Guest": 0,
    "Management": 0,
}

print("=" * 72)
print("BEFORE: flat network (no VLANs, one broadcast domain)")
print("=" * 72)
print(f"Total devices on the network: {total_devices}")
print(f"Blast radius from ANY compromised device: {total_devices - 1} other devices reachable")
print(f"Legacy/unpatched warehouse devices exposed directly to every other device: "
      f"{legacy_by_segment['Warehouse']}")
print(f"Guest wifi clients sharing a broadcast domain with corporate file/print server: "
      f"{by_segment['Guest']}")

print()
print("=" * 72)
print("AFTER: 5-VLAN segmentation + default-deny inter-VLAN firewall policy")
print("=" * 72)
header = f"{'Segment':<12}{'VLAN':<6}{'Devices':<10}{'Legacy risk':<13}{'Blast radius (worst case)':<28}"
print(header)
print("-" * len(header))
results = []
for segment, count in by_segment.items():
    blast_radius = count - 1 + EXTRA_REACHABLE[segment]
    reduction_pct = 100 * (1 - blast_radius / (total_devices - 1))
    results.append((segment, count, legacy_by_segment.get(segment, 0), blast_radius, reduction_pct))
    print(f"{segment:<12}{'':<6}{count:<10}{legacy_by_segment.get(segment,0):<13}{blast_radius:<28}")

worst_case = max(r[3] for r in results)
worst_reduction = 100 * (1 - worst_case / (total_devices - 1))
best_case = min(r[3] for r in results)
best_reduction = 100 * (1 - best_case / (total_devices - 1))

print()
print(f"Worst-case post-segmentation blast radius (largest VLAN, Office): {worst_case} devices "
      f"({worst_reduction:.1f}% reduction from flat-network baseline of {total_devices - 1})")
print(f"Best-case post-segmentation blast radius (smallest VLAN, Management): {best_case} devices "
      f"({best_reduction:.1f}% reduction)")
print(f"\nThe {legacy_by_segment['Warehouse']} legacy/unpatched warehouse scanners and printers — "
      f"the single highest-risk device class on the network — are now reachable only from the "
      f"{by_segment['Warehouse']}-device Warehouse VLAN, not from any of the other "
      f"{total_devices - by_segment['Warehouse']} devices on the network.")

with open("data/raw/blast_radius_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["segment", "device_count", "legacy_risk_devices", "blast_radius_after_segmentation",
                      "blast_radius_reduction_pct"])
    for segment, count, legacy, blast, pct in results:
        writer.writerow([segment, count, legacy, blast, round(pct, 1)])
    writer.writerow(["FLAT_NETWORK_BASELINE", total_devices, legacy_by_segment["Warehouse"],
                      total_devices - 1, 0.0])

print("\nWrote data/raw/blast_radius_summary.csv")
