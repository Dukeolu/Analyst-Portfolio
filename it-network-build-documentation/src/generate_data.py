"""
Generates the simulated device inventory for Meridian Manufacturing's new
Riverside regional distribution branch (~65 devices, opening greenfield —
no existing network to migrate, so this is a build, not a redesign).

Deliberately seeded findings:
  - The naive "one flat network" plan a site-opening checklist defaults to
    would put all 65 devices, across 4 very different trust levels, in one
    broadcast domain / one routable subnet.
  - A handful of warehouse floor devices are older, rarely-patched barcode
    scanners and label printers (embedded OS, no host firewall, vendor
    support ended) — the single highest-risk asset class on the network,
    and exactly the kind of device a flat network fails to isolate.
  - Guest wifi for visiting drivers/vendors is a hard requirement (the
    branch has a loading-dock visitor flow) and must never share a
    broadcast domain with anything else.
"""
import csv
import random

random.seed(42)

DEVICE_TYPES = {
    "Office": [
        ("Workstation", 22, False),
        ("Office printer/MFP", 3, False),
        ("Wireless AP (corp SSID)", 2, False),
        ("File/print server", 1, False),
    ],
    "Warehouse": [
        ("Barcode scanner (handheld, legacy OS)", 10, True),
        ("Label printer (legacy firmware)", 4, True),
        ("Floor terminal / WMS kiosk", 3, False),
        ("Dock door controller", 1, False),
    ],
    "VoIP": [
        ("Desk phone", 12, False),
        ("Conference room phone", 2, False),
    ],
    "Guest": [
        ("Guest wifi client (visiting driver/vendor laptop or phone)", 12, False),
    ],
    "Management": [
        ("Core switch", 1, False),
        ("Access switch", 3, False),
        ("Firewall (mgmt interface)", 1, False),
        ("Wireless controller", 1, False),
    ],
}

VLAN_MAP = {
    "Office": (10, "10.10.10.0/24"),
    "Warehouse": (20, "10.10.20.0/24"),
    "VoIP": (30, "10.10.30.0/24"),
    "Guest": (40, "10.10.40.0/24"),
    "Management": (99, "10.10.99.0/28"),
}

rows = []
device_id = 1
for segment, devices in DEVICE_TYPES.items():
    vlan_id, subnet = VLAN_MAP[segment]
    for device_type, count, legacy_risk in devices:
        for _ in range(count):
            rows.append({
                "device_id": f"MFG-RVS-{device_id:04d}",
                "segment": segment,
                "device_type": device_type,
                "assigned_vlan": vlan_id,
                "assigned_subnet": subnet,
                "legacy_unpatched_risk": "Y" if legacy_risk else "N",
                "patch_status": "Vendor support ended / rarely patched" if legacy_risk else "Managed / current",
            })
            device_id += 1

with open("data/raw/device_inventory.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} devices across {len(DEVICE_TYPES)} segments.")
for segment in DEVICE_TYPES:
    n = sum(1 for r in rows if r["segment"] == segment)
    legacy = sum(1 for r in rows if r["segment"] == segment and r["legacy_unpatched_risk"] == "Y")
    print(f"  {segment}: {n} devices ({legacy} legacy/unpatched-risk)")
