# Patching the CVE Isn't the Same as Hardening the Server — Meridian Manufacturing (simulated)

**Skills:** Server hardening &middot; CIS-style benchmarking &middot; Linux security configuration &middot; attack-surface reduction

## The business problem

The vulnerability assessment case found and prioritized Log4Shell on Meridian's ERP/WMS integration server. Patching that one CVE closes the specific finding a scanner flagged — it does nothing about the two dozen other hardening gaps sitting on the same host: SSH accepting password logins with no idle timeout, no host-based firewall, no audit logging, world-writable files, accounts with empty passwords. A vulnerability scan finds known CVEs; it doesn't tell you whether the underlying server is actually configured defensibly. This case runs a CIS-style hardening benchmark against that same server to answer the second question.

## Environment / data

A 25-control hardening checklist across 6 categories (Filesystem, Services, Network, Logging & Auditing, Access & SSH, System Maintenance), scored against the server's as-found baseline and again after remediation, plus 6 concrete attack-surface metrics (listening services, world-writable files, weak SSH ciphers, etc.) measured the same way. No real server or scanning tool is available in this sandbox. Full methodology: [`data/README.md`](data/README.md).

## Method / tools

1. **Baseline capture** (`configs/baseline/`) — the as-found `sshd_config` and `sysctl.conf`, representative of a server that's never had a deliberate hardening pass applied.
2. **CIS-style benchmark** (`src/generate_data.py`, `data/raw/cis_hardening_checklist.csv`) — 25 controls across 6 categories, each checked before and after remediation.
3. **Remediation** (`configs/hardened/`) — the actual hardened `sshd_config`, a new `sysctl.d` hardening file, and host-based firewall (`ufw`) rules, each change tied back to the specific control it satisfies.
4. **Analysis** (`src/hardening_analysis.py`) — compliance by category, the list of any remaining exceptions, and the attack-surface reduction across all 6 concrete metrics.

## Analysis

The hardening pass was organized by category rather than tackled as one flat list, because that's what surfaced a pattern worth reporting: every single category started under 30% compliant, meaning this wasn't a server with one weak area and five strong ones — it was a server that had never been hardened at all, uniformly. Access & SSH was the most extreme case (0 of 6 controls passing at baseline) and also the highest-leverage fix, since SSH is the primary administrative access path to the host. One control — legacy TLS on the integration API — was deliberately not forced to pass, because doing so would have broken a live EDI trading-partner integration; that's reported as a disclosed, time-boxed risk acceptance rather than smoothed over to claim a clean 100%.

## Key findings

1. **Baseline compliance was 20.0% (5 of 25 controls)** — not a server with isolated gaps, but one that had never been through a deliberate hardening process at all.
2. **Every one of the 6 control categories started below 30% compliant**, and 5 of 6 reached full compliance after remediation (Filesystem, Services, Network, Logging & Auditing, and Access & SSH all hit 100%).
3. **Access & SSH went from 0 of 6 controls passing to 6 of 6** — the highest-leverage category, since SSH is the primary administrative access path to this server.
4. **Attack surface dropped by an average of 89.5% across 6 concrete metrics**, including a 100% reduction in world-writable files (8→0), empty-password accounts (2→0), weak/legacy SSH ciphers accepted (9→0), and pending security updates (23→0).
5. **One control was deliberately not forced to pass**: legacy TLS 1.0/1.1 stays enabled on the integration API because one EDI trading partner's client can't yet negotiate TLS 1.2+ — tracked as a disclosed, time-boxed exception with a scheduled partner migration, not silently ignored to claim 100% compliance.

| Metric | Value |
|---|---|
| Baseline compliance | 20.0% (5 of 25 controls) |
| Post-remediation compliance | 96.0% (24 of 25 controls) |
| Average attack-surface reduction | 89.5% across 6 metrics |
| Risk-accepted exceptions | 1 (legacy TLS, disclosed &amp; time-boxed) |

## Recommendation

1. **Apply this same 25-control benchmark to every server in the estate**, prioritized by the vulnerability assessment's asset-criticality ratings — this case demonstrates the method on one host; the value compounds across all 40.
2. **Track the TLS exception on a real deadline**, not an open-ended one — the partner migration should have an owner and a date, or "time-boxed" quietly becomes permanent.
3. **Bake the hardened configs into the server build process** (a golden image or configuration-management baseline) rather than applying them as a one-time remediation — a server rebuilt from an unhardened base image regresses to 20% compliance immediately.
4. **Re-scan quarterly**, not just after an incident — hardening drift (a well-meaning admin re-enabling password SSH auth to debug something, and forgetting to revert it) is normal and needs a routine check to catch.

## Expected impact

This hardening pass reduces the ERP/WMS integration server's attack surface by an average of 89.5% across 6 concrete, independently verifiable metrics — not an abstract compliance percentage, but real counts: 8 world-writable files down to 0, 2 empty-password accounts down to 0, 23 pending security updates down to 0. Combined with the vulnerability assessment's Log4Shell finding, patching the one CVE and hardening the surrounding configuration together mean this server no longer has either a known critical vulnerability or the permissive baseline configuration that would make the next vulnerability easier to exploit.

> **The pitch in one line:** a vulnerability scan finds the vulnerabilities someone already named — a hardening pass fixes the hundred small permissive defaults nobody named yet, and 24 of them were sitting on the same server as the one CVE the scan actually caught.

## Limitations / next analysis

- The 25-control checklist is a representative subset built for this portfolio, covering standard, widely-documented hardening concepts — not the complete CIS Benchmark (200+ controls for a typical distribution), and not copied from any specific published, copyrighted benchmark document.
- This case hardens one server (the ERP/WMS integration server); a real program would run the same benchmark across the full 40-host estate from the vulnerability assessment case, and the categories most likely to vary host-to-host (Services, in particular, since different server roles need different services running) would need role-specific baselines rather than one universal checklist.
- The TLS risk-acceptance exception is disclosed and time-boxed in this write-up, but a real deployment would need this tracked in an actual risk register with an owner and review date — see the companion Risk Register / GRC case for how that tracking would work.
- Baseline and remediated states are simulated based on realistic defaults, not captured from an actual compliance-scanning tool (e.g., Lynis, OpenSCAP) run against a real host.

## Repo structure

```
cybersecurity-security-hardening/
├── README.md                          this file
├── requirements.txt
├── data/
│   ├── README.md                      data model, generation methodology, limitations
│   └── raw/
│       ├── cis_hardening_checklist.csv
│       ├── attack_surface_metrics.csv
│       └── hardening_summary.csv
├── src/
│   ├── generate_data.py               builds the simulated benchmark results
│   └── hardening_analysis.py          compliance by category + attack-surface reduction
├── configs/
│   ├── baseline/
│   │   ├── sshd_config.baseline
│   │   └── sysctl.baseline.conf
│   └── hardened/
│       ├── sshd_config.hardened
│       ├── sysctl-hardening.conf
│       └── ufw-rules.txt
└── visuals/
    ├── build_exhibit.py                builds the HTML exhibit
    └── hardening-exhibit.html          self-contained visual summary (site link)
```
