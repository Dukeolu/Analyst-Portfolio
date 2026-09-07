# Data — Security Hardening Project

Simulated for this portfolio. Meridian Manufacturing's real server configuration isn't available here — the target host is the same ERP/WMS integration server that carried the Log4Shell finding in the vulnerability-assessment case, continuing that case's narrative rather than introducing a new unrelated system.

## Files

### `raw/cis_hardening_checklist.csv` (25 rows)

25 hardening controls across 6 categories (Filesystem, Services, Network, Logging & Auditing, Access & SSH, System Maintenance), modeled on standard, widely-known Linux server hardening practices — original descriptions of these concepts, not verbatim text from any specific published benchmark (CIS Benchmarks are copyrighted documents). Each row records baseline pass/fail, post-remediation pass/fail, and the specific remediation action taken.

### `raw/attack_surface_metrics.csv` (6 rows)

Concrete before/after counts for 6 attack-surface indicators (listening services, world-writable files, empty-password accounts, etc.) — a second, more concrete way of measuring the same hardening effort beyond the pass/fail checklist.

### `raw/hardening_summary.csv`

Output of `src/hardening_analysis.py` — the headline compliance and attack-surface-reduction numbers.

## How it was generated (`src/generate_data.py`)

The baseline compliance state (5 of 25 controls passing, 20.0%) was constructed to be representative of a server that has never been through a deliberate hardening pass — the default state of most services, SSH, and logging on a freshly built Linux server, not a strawman worst case. One control (legacy TLS 1.0/1.1 on the integration API) was deliberately left failing after remediation, with a disclosed, realistic business reason: an EDI trading partner's legacy client can't yet negotiate TLS 1.2+, so forcing it immediately would break a live integration. That's presented as a tracked, time-boxed risk-acceptance exception rather than a silently ignored gap — the honest answer to "did you fix everything" is usually "no, and here's the one thing and why."

## Limitations

- The 25-control checklist is a representative subset built for this portfolio, not the complete CIS Benchmark (which runs to 200+ controls for a typical Linux distribution) — the categories and underlying concepts are standard and widely documented, but the specific control set and numbering here are original to this project, not copied from CIS's published, copyrighted benchmark documents.
- Baseline and remediated pass/fail states are simulated based on realistic defaults and standard hardening practice, not from an actual compliance-scanning tool run against a real host.
- Attack-surface metric counts (listening services, world-writable files, etc.) are illustrative, consistent with the checklist's pass/fail results, not derived from an actual `nmap`/`lynis`-style scan output.
