# Building a Branch Network That's Segmented From Day One — Meridian Manufacturing (simulated)

**Skills:** Network design &middot; VLAN segmentation &middot; firewall policy &middot; DHCP scoping &middot; technical documentation

## The business problem

Meridian Manufacturing (simulated) is opening a new regional distribution branch — Riverside — with roughly 65 employees split across an office, a warehouse floor, and a steady flow of visiting drivers and vendors who need guest wifi at the loading dock. Left to a standard site-opening checklist, the default is one flat network: every device — workstations, warehouse scanners, guest laptops, the switches themselves — on one broadcast domain, because it's the fastest way to get the branch online. The problem with that default isn't hypothetical: it means a single compromised guest laptop, or one of the branch's own legacy warehouse scanners, can reach every other device on the network with nothing in the way. The task was to design and document the network so that trade-off is never made in the first place.

## Environment / data

A simulated 78-device inventory for the branch at go-live: 28 office devices, 18 warehouse devices (14 of them a legacy, rarely-patched device class — handheld scanners and label printers with embedded OS and no host firewall), 14 VoIP phones, 12 guest wifi clients, and 6 network-management devices. No real infrastructure exists behind this — it's a greenfield build, not an export from a live network. Full inventory and methodology: [`data/README.md`](data/README.md).

## Method / tools

1. **Segmentation design** — 5 VLANs (Office, Warehouse, VoIP, Guest, Management), each on its own subnet, mapped to the device inventory by trust level and function rather than by physical location alone.
2. **Switch configuration** (`configs/switch-vlan-config.txt`) — a Cisco IOS-style core + two access switches, 802.1Q trunks scoped to only the VLANs each switch actually needs, port security on every access port, BPDU guard on edge ports, and an intentionally unused native VLAN as a VLAN-hopping mitigation.
3. **DHCP scoping** (`configs/dhcp-config.conf`) — one scope per VLAN, each tuned to what that segment actually needs: a 1-hour lease on Guest (visitor turnover, keeps the pool from exhausting on a busy dock day), a 7-day lease on VoIP (phones rarely move), and no DHCP scope at all on Management (every management IP is static, so a rogue device can't just plug in and get an address on the network that controls the network).
4. **Firewall policy** (`configs/firewall-rules.conf`) — default-deny between every VLAN, with each necessary exception written as a narrow, named pinhole (a specific host and port) rather than a blanket VLAN-to-VLAN allow.
5. **Quantified analysis** (`src/network_analysis.py`) — a blast-radius calculation: how many devices would be reachable from one compromised device, before (flat network) and after (this design), per segment.

## Analysis

The core design decision was where to draw segment boundaries, and the driver was risk concentration, not device count. The 14 legacy/unpatched warehouse scanners and printers are the single highest-risk device class on the network — they can't run modern endpoint protection and their vendor stopped shipping patches — so Warehouse got the strictest firewall treatment of any internal segment: one pinhole to a single integration server, nothing else in or out except a proxied path for firmware updates. Guest got the strictest treatment overall, since it's the only segment with devices Meridian doesn't own or control at all: zero paths to any internal subnet, full client isolation even within the segment, and DNS pointed at a public resolver instead of the internal one. Management got the narrowest allow-list of all — one designated jump host, two ports — since anyone who can reach a switch's management interface can potentially reshape the whole network.

## Key findings

1. **A flat network gives every device the same blast radius: all 77 others.** That's the actual baseline this design replaces — not a hypothetical worst case, but what a default site-opening checklist produces.
2. **Segmentation cuts that blast radius by 65–94% depending on segment**, even under a "worst case" reading that assumes an attacker who reaches one VLAN can eventually reach everything in it: Office (the largest VLAN) drops to 27 reachable devices (a 64.9% reduction), while Management (the smallest, most sensitive) drops to 5 (a 93.5% reduction).
3. **The 14 legacy/unpatched warehouse devices — the network's biggest single risk concentration — are now isolated to an 18-device VLAN**, reachable from none of the other 60 devices on the network, instead of being flatly exposed to all of them.
4. **Every inter-VLAN exception in the firewall policy is a named pinhole, not a blanket allow.** Warehouse's only path to Office is one host, one port (the WMS integration server's API). Management is reachable from exactly one source IP (the IT jump host) on exactly two ports (SSH, HTTPS) — not from "the office network" broadly.
5. **Guest wifi has zero paths to any internal VLAN.** Its only allowed destination is the internet, on web/DNS ports — the single most important rule in the whole policy, since it's what stops a compromised visitor laptop from ever becoming a foothold into the corporate network.

| Metric | Value |
|---|---|
| Devices at branch go-live | 78 across 5 segments |
| Legacy/unpatched devices isolated to their own VLAN | 14 |
| Worst-case blast radius reduction (Office VLAN) | 77 → 27 devices (64.9%) |
| Best-case blast radius reduction (Management VLAN) | 77 → 5 devices (93.5%) |
| Guest → internal-network paths allowed | 0 |

## Recommendation

1. **Deploy the 5-VLAN design as specified** — Office, Warehouse, VoIP, Guest, Management — rather than the single flat network a faster rollout would default to; the incremental cost is switch/firewall configuration time, not additional hardware.
2. **Treat the Warehouse pinhole (WMS server, single port) as the one exception worth monitoring closely** — it's the only path in or out of the branch's highest-risk device class, so any change to that rule should go through change control, not a quick edit.
3. **Keep Management on static addressing permanently**, even as the branch grows — the moment a DHCP scope gets added "temporarily" for a network device is the moment the jump-host-only access control gets easier to bypass by accident.
4. **Re-run the blast-radius analysis whenever the device mix changes materially** (e.g., a warehouse automation project adds 20 more scanners) — the segmentation boundaries were drawn against today's device counts and risk concentration, and a large enough shift could justify a 6th VLAN rather than growing an existing one past its intent.

## Expected impact

Segmenting the network at build time, rather than retrofitting segmentation onto a flat network later, avoids the two costs a retrofit usually carries: the migration risk of moving live production devices between subnets, and the window of exposure between "flat network goes live" and "someone gets around to fixing it." Quantified directly: the design reduces the number of devices reachable from any single compromised device by 65–94% depending on segment, and isolates the branch's single largest risk concentration (14 legacy, unpatched warehouse devices) from the other 60 devices on the network entirely. This is a zero-incremental-hardware change — the cost is switch, DHCP, and firewall configuration effort during a build that was happening anyway, not a new purchase.

> **The pitch in one line:** the safest time to segment a network is before it has any devices on it — this build gets a 65–94% blast-radius reduction for the cost of writing the VLAN and firewall config instead of skipping it.

## Limitations / next analysis

- This is a greenfield build, so there's no real "before" network to compare against — the flat-network baseline used throughout is the counterfactual a standard site-opening checklist would produce, not a network that ever actually ran.
- The blast-radius metric is a simplified proxy (devices reachable per segment) — it doesn't weight for device value, exploit difficulty, or defense-in-depth controls beyond network segmentation (host firewalls, EDR, MFA), which a full risk assessment would layer on top of this design.
- Device counts are a go-live planning estimate, not a trued-up hardware order — a real rollout would confirm exact counts before finalizing DHCP pool sizes, especially the Guest pool, which is sized for an assumed peak concurrent-visitor count rather than measured dock traffic.
- The firewall ruleset is written in a generic, pfSense-style syntax for portability across this portfolio's audience — a real deployment would translate it to the specific platform in use (a physical next-gen firewall, a cloud-hosted virtual appliance, etc.) and validate every rule against the vendor's actual rule-evaluation semantics.
- This design covers the network layer only — it doesn't include endpoint hardening, wireless security (WPA2-Enterprise vs. PSK, RADIUS setup), or physical security controls, all of which a complete branch security posture would need alongside it.

## Repo structure

```
it-network-build-documentation/
├── README.md                      this file
├── requirements.txt
├── data/
│   ├── README.md                  data model, generation methodology, limitations
│   └── raw/
│       ├── device_inventory.csv
│       └── blast_radius_summary.csv
├── src/
│   ├── generate_data.py           builds the simulated device inventory
│   └── network_analysis.py        blast-radius before/after calculation
├── configs/
│   ├── switch-vlan-config.txt     Cisco IOS-style core + access switch config
│   ├── dhcp-config.conf           ISC dhcpd-style scope per VLAN
│   └── firewall-rules.conf        pfSense-style default-deny inter-VLAN policy
└── visuals/
    ├── build_diagram.py           builds the topology diagram (Graphviz)
    ├── network-diagram.png
    ├── build_exhibit.py           builds the HTML exhibit
    └── network-build-exhibit.html   self-contained visual summary (site link)
```
