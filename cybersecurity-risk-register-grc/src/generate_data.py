"""
Builds the simulated risk register for Meridian Manufacturing — the GRC
roll-up of findings from every other case in the IT & Cybersecurity track.
Each risk cites the specific case it was identified in, so this register
reads as a rollup rather than a fresh, disconnected list.

Scoring model: inherent risk (before any control) vs residual risk (given
current controls), each as likelihood (1-5) x impact (1-5) = score (1-25).
Risk reduction % = (inherent - residual) / inherent.
"""
import csv

# (risk_id, title, category, csf_function, source_case,
#  inherent_likelihood, inherent_impact,
#  residual_likelihood, residual_impact,
#  status, owner, target_date, notes)
RISKS = [
    ("R01", "Log4Shell RCE on the ERP/WMS integration server", "Vulnerability",
     "Protect", "Vulnerability Assessment (Cyber Case 02)",
     4, 5, 1, 5, "Closed",
     "Infrastructure", "2026-01-15",
     "Patched per refined remediation priority; server also hardened (Cyber Case 03)"),

    ("R02", "Citrix VPN gateway RCE (refined priority #1 finding)", "Vulnerability",
     "Protect", "Vulnerability Assessment (Cyber Case 02)",
     4, 5, 1, 5, "Closed",
     "Infrastructure", "2026-01-15",
     "Patched first under the composite-score refined ranking, ahead of naive CVSS-only order"),

    ("R03", "Legacy TLS 1.0/1.1 still enabled on the EDI integration API", "Configuration",
     "Protect", "Security Hardening (Cyber Case 03)",
     3, 3, 2, 3, "Risk Accepted",
     "Infrastructure", "2026-Q2",
     "One trading partner's client can't yet negotiate TLS 1.2+; migration scheduled, disclosed and time-boxed"),

    ("R04", "Vendor support account still active & privileged 8 months post-engagement", "Access Control",
     "Identify", "Incident Response Tabletop (Cyber Case 04)",
     3, 4, 3, 4, "Open",
     "IT Security", "2026-10-01",
     "Was the actual lateral-movement path used in the tabletop scenario; no compensating control yet"),

    ("R05", "No ransomware-specific incident response runbook", "Response Readiness",
     "Respond", "Incident Response Tabletop (Cyber Case 04)",
     3, 4, 3, 4, "Open",
     "IT Security", "2026-09-30",
     "Team improvised containment steps in the tabletop; adapt the VPN outage runbook format"),

    ("R06", "Phishing reports take ~2 days to reach security (26h detection gap)", "Detection Gap",
     "Detect", "Incident Response Tabletop (Cyber Case 04)",
     4, 4, 4, 4, "Open",
     "IT Security", "2026-10-15",
     "Single highest-priority recommendation from the tabletop after-action report"),

    ("R07", "Account-takeover detection rule not yet deployed", "Detection Gap",
     "Detect", "Log Analysis / Intrusion Detection (prior case)",
     3, 4, 3, 3, "In Progress",
     "SOC", "2026-11-01",
     "Would likely have caught the tabletop's user0147 compromise at hour 0-1 instead of hour 26"),

    ("R08", "No recurring access review for third-party / vendor accounts", "Governance",
     "Govern", "Incident Response Tabletop (Cyber Case 04)",
     3, 3, 3, 3, "Open",
     "IT Security", "2026-10-01",
     "Standing process gap, independent of any single incident"),

    ("R09", "SSH accepted password auth & legacy ciphers (pre-hardening baseline)", "Configuration",
     "Protect", "Security Hardening (Cyber Case 03)",
     3, 3, 1, 3, "Closed",
     "Infrastructure", "2026-01-20",
     "Access & SSH category went from 0/6 to 6/6 controls passing"),

    ("R10", "World-writable files & empty-password accounts (pre-hardening baseline)", "Configuration",
     "Protect", "Security Hardening (Cyber Case 03)",
     3, 3, 1, 2, "Closed",
     "Infrastructure", "2026-01-20",
     "Filesystem & Access categories both reached 100% post-remediation"),

    ("R11", "Backup recovery point objective is a 4-hour window, unvalidated beyond one incident", "Recovery",
     "Recover", "Incident Response Tabletop (Cyber Case 04)",
     2, 3, 2, 2, "Monitoring",
     "IT Infrastructure", "2026-Q1 review",
     "Restore worked cleanly in the tabletop; RPO tightening is a future efficiency question, not a current gap"),

    ("R12", "181 lower-severity scan findings outside the 8-hour remediation window", "Vulnerability",
     "Protect", "Vulnerability Assessment (Cyber Case 02)",
     3, 2, 3, 2, "Open",
     "Infrastructure", "2026-Q4 backlog",
     "Refined plan closed 29.0% of composite risk in the first 8 hours; the remainder is tracked backlog, not ignored"),

    ("R13", "No policy trigger tying account deprovisioning to HR/vendor contract end dates", "Governance",
     "Govern", "Synthesized across Cyber Case 04 findings",
     3, 3, 3, 3, "Open",
     "IT Security", "2026-10-01",
     "The policy-level root cause underneath both R04 and R08 — one fix closes both symptoms"),

    ("R14", "Warehouse & Ops VPN accounts use single-factor authentication", "Access Control",
     "Protect", "Synthesized across IT Case 01, IT Case 04, Cyber Case 02, Cyber Case 04",
     4, 4, 4, 4, "Open",
     "IT Security", "2026-11-15",
     "The VPN gateway recurs as an initial-access or availability theme in four separate cases; MFA is the common fix"),

    ("R15", "KB self-service articles still building toward target adoption", "Response Readiness",
     "Respond", "Knowledge Base & Runbook Set (IT Case 04)",
     2, 2, 2, 1, "Monitoring",
     "IT Support", "2026-Q2 review",
     "25% adoption assumption modeled in that case; higher adoption further reduces technician load"),
]

with open("data/raw/risk_register.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "risk_id", "title", "category", "csf_function", "source_case",
        "inherent_likelihood", "inherent_impact", "inherent_score",
        "residual_likelihood", "residual_impact", "residual_score",
        "risk_reduction_pct", "status", "owner", "target_date", "notes",
    ])
    for (rid, title, cat, csf, source, il, ii, rl, ri, status, owner, target, notes) in RISKS:
        inherent_score = il * ii
        residual_score = rl * ri
        reduction_pct = round((inherent_score - residual_score) / inherent_score * 100, 1)
        writer.writerow([
            rid, title, cat, csf, source,
            il, ii, inherent_score,
            rl, ri, residual_score,
            reduction_pct, status, owner, target, notes,
        ])

print(f"Wrote data/raw/risk_register.csv ({len(RISKS)} risks)")
