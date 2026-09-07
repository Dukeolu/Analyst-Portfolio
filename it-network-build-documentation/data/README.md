# Data — Riverside Branch Network Build

Simulated for this portfolio. Meridian Manufacturing and its Riverside branch are fictional — this is a greenfield network build (no existing infrastructure to migrate), so "data" here is a device inventory constructed to be representative of a real small-branch build, not exported from a live network.

## Files

### `raw/device_inventory.csv` (78 rows)

One row per device planned for the branch at go-live.

| Column | Description |
|---|---|
| `device_id` | Simulated asset tag |
| `segment` | Office / Warehouse / VoIP / Guest / Management |
| `device_type` | What the device is |
| `assigned_vlan` | VLAN ID it's placed on |
| `assigned_subnet` | The VLAN's subnet |
| `legacy_unpatched_risk` | Y/N — flags device classes with embedded OS, no host firewall, and ended vendor support (the warehouse scanners/printers) |
| `patch_status` | Free-text patch posture |

### `raw/blast_radius_summary.csv` (6 rows)

Output of `src/network_analysis.py` — device count, legacy-risk count, and post-segmentation blast radius per segment, plus the flat-network baseline row.

## How the inventory was built (`src/generate_data.py`)

Device counts and types were chosen to be representative of a ~65-employee branch with a small warehouse floor: 28 office devices (workstations, an MFP, corp wifi APs, a file/print server), 18 warehouse devices (barcode scanners, label printers, floor terminals, a dock door controller — 14 of these are the legacy/unpatched device class, since handheld scanners and label printers in the field are notoriously slow to patch and often end-of-vendor-support years before anyone notices), 14 VoIP desk/conference phones, 12 guest wifi clients (a fixed planning assumption for concurrent visiting drivers/vendors), and 6 management-plane devices (switches, firewall, wireless controller).

## Limitations

- This is a greenfield build, not a migration — there's no "before" network to audit, so the "before" comparison in the README and exhibit (flat network) is the counterfactual a site-opening checklist would produce by default, not a network that ever actually existed.
- Device counts are a planning estimate for branch go-live, not a live headcount — a real rollout would true these up against the actual hardware order and HR headcount before finalizing DHCP pool sizes.
- The blast-radius metric (devices reachable per segment) is a simplified proxy for lateral-movement risk — it doesn't model exploit difficulty, device value, or defense-in-depth controls beyond VLAN/firewall segmentation (host firewalls, EDR, etc.), which a real risk assessment would layer on top.
