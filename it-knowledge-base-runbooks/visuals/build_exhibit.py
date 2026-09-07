"""Builds visuals/kb-runbook-exhibit.html — matches the site's dashboard
design system, built from the real deflection analysis numbers."""
import csv

with open("data/raw/deflection_summary.csv") as f:
    rows = list(csv.DictReader(f))
top5 = [r for r in rows if r["category"] != "TOTAL"]

with open("data/raw/deflection_impact.csv") as f:
    impact = {row["metric"]: row["value"] for row in csv.DictReader(f)}

adoption_rate = float(impact["self_service_adoption_rate_pct"])
annual_tickets = float(impact["annual_addressable_tickets"])
annual_hours = float(impact["annual_addressable_hours"])
deflected_tickets = float(impact["annual_deflected_tickets"])
deflected_hours = float(impact["annual_deflected_hours"])
dollar_impact = float(impact["annual_dollar_impact"])

BAR_COLOR = "#2a6f6f"

LABELS = {
    ("Network & VPN", "Can't connect to office VPN"): "VPN connection (KB-01)",
    ("Hardware", "Printer won't print / shows offline"): "Printer troubleshooting (KB-02)",
    ("Password Reset", "Forgot network password"): "Password reset (KB-03)",
    ("Email & Calendar", "Can't set up email on phone"): "Email on phone (KB-04)",
    ("Network & VPN", "Can't connect to office wifi"): "Wifi connection (KB-05)",
}


def hbar_chart(rows, width=640, left=200, right=624, row_h=38, top=10):
    n = len(rows)
    height = top + n * row_h + 10
    max_val = max(float(r["minutes_annual"]) for r in rows) * 1.05
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    for i, r in enumerate(rows):
        y = top + i * row_h
        key = (r["category"], r["issue"])
        label = LABELS.get(key, f"{r['category']} / {r['issue']}")
        minutes = float(r["minutes_annual"])
        hours = minutes / 60
        bw = (minutes / max_val) * (right - left - 40)
        svg.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="20" rx="4" fill="{BAR_COLOR}">'
                    f'<title>{label}: {hours:.0f} technician-hours/yr</title></rect>')
        svg.append(f'<text x="{left-10}" y="{y+14}" class="axis-label sku-label" text-anchor="end">{label}</text>')
        svg.append(f'<text x="{left+bw+8:.1f}" y="{y+14}" class="bar-label-h" text-anchor="start">{hours:.0f}h/yr</text>')
    svg.append("</svg>")
    return "\n".join(svg)


chart_svg = hbar_chart(top5)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Manufacturing &middot; KB &amp; Runbook Deflection Exhibit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F5F4; --paper-raised:#FBFCFB; --ink:#0b0b0b; --ink-soft:#52514e; --ink-faint:#898781;
  --line:#D6DCDA; --line-strong:#B9C2C0; --accent:#2a6f6f; --accent-ink:#1d4f4f; --accent-wash:#DCEAEA;
  --good:#0ca30c;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#12161C; --paper-raised:#181D25; --ink:#ffffff; --ink-soft:#c3c2b7; --ink-faint:#6E7885;
    --line:#2A3038; --line-strong:#3A414B; --accent:#5FB3B3; --accent-ink:#9FD6D6; --accent-wash:#173030;
    --good:#0ca30c;
  }}
}}
:root[data-theme="dark"]{{
  --paper:#12161C; --paper-raised:#181D25; --ink:#ffffff; --ink-soft:#c3c2b7; --ink-faint:#6E7885;
  --line:#2A3038; --line-strong:#3A414B; --accent:#5FB3B3; --accent-ink:#9FD6D6; --accent-wash:#173030;
  --good:#0ca30c;
}}
*{{box-sizing:border-box;}}
body{{margin:0; background:var(--paper); color:var(--ink); font-family:"IBM Plex Sans",sans-serif; -webkit-font-smoothing:antialiased;}}
h1,h2{{font-family:"Spectral",Georgia,serif; font-weight:600; margin:0; text-wrap:balance;}}
.mono{{font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums;}}
.shell{{max-width:1080px; margin:0 auto; padding:40px 28px 72px;}}
header{{padding-bottom:24px; border-bottom:1px solid var(--line); margin-bottom:28px;}}
.eyebrow{{font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.1em; text-transform:uppercase; color:var(--accent-ink); display:flex; align-items:center; gap:8px; margin-bottom:10px;}}
.eyebrow::before{{content:""; width:6px; height:6px; border-radius:50%; background:var(--accent);}}
header h1{{font-size:clamp(24px,3.4vw,32px);}}
header p{{color:var(--ink-soft); font-size:14.5px; max-width:68ch; margin-top:10px; line-height:1.6;}}

.kpis{{display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:32px;}}
@media (max-width:820px){{.kpis{{grid-template-columns:1fr 1fr;}}}}
.kpi{{background:var(--paper-raised); border:1px solid var(--line); border-radius:10px; padding:18px 18px 16px;}}
.kpi .k{{font-family:"IBM Plex Mono",monospace; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--ink-faint);}}
.kpi .v{{font-family:"IBM Plex Mono",monospace; font-size:25px; margin-top:8px;}}
.kpi .delta{{font-size:12.5px; color:var(--ink-soft); margin-top:4px;}}
.kpi .delta.good{{color:var(--good);}}

section{{margin-bottom:36px;}}
section h2{{font-size:17px; margin-bottom:4px;}}
section .sub{{color:var(--ink-faint); font-size:13px; margin-bottom:14px;}}
.panel{{background:var(--paper-raised); border:1px solid var(--line); border-radius:10px; padding:18px 18px 8px; overflow-x:auto;}}

.chart-svg .baseline{{stroke:var(--line-strong); stroke-width:1;}}
.chart-svg .axis-label{{fill:var(--ink-faint); font-size:11px; font-family:"IBM Plex Mono",monospace;}}
.chart-svg .sku-label{{fill:var(--ink-soft); font-family:"IBM Plex Sans",sans-serif;}}
.chart-svg .bar-label-h{{fill:var(--ink); font-size:12px; font-family:"IBM Plex Mono",monospace; font-weight:500;}}

.roi-grid{{display:grid; grid-template-columns:repeat(3,1fr); gap:16px;}}
@media (max-width:760px){{.roi-grid{{grid-template-columns:1fr;}}}}
.roi-card{{background:var(--paper-raised); border:1px solid var(--line); border-radius:10px; padding:18px;}}
.roi-card .k{{font-family:"IBM Plex Mono",monospace; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--ink-faint);}}
.roi-card .v{{font-family:"IBM Plex Mono",monospace; font-size:22px; margin:8px 0 10px;}}
.roi-card .sub2{{font-size:12.5px; color:var(--ink-soft);}}
.roi-card.net{{border-color:var(--accent); background:var(--accent-wash);}}

footer{{border-top:1px solid var(--line); padding-top:18px; font-size:12px; color:var(--ink-faint);}}
</style>
</head>
<body>
<div class="shell">
  <header>
    <div class="eyebrow">IT Support &middot; Meridian Manufacturing (simulated)</div>
    <h1>Which 5 KB articles are actually worth writing?</h1>
    <p>Not the 5 easiest topics to explain &mdash; the 5 self-service-eligible issues consuming the most technician time. Ranked from 6 months of ticket data, then written, plus one technician-facing runbook for the highest-severity version of the worst offender.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Addressable ticket volume</div>
      <div class="v">{annual_tickets:,.0f}/yr</div>
      <div class="delta">across the 5 KB topics chosen</div>
    </div>
    <div class="kpi">
      <div class="k">Technician time at stake</div>
      <div class="v">{annual_hours:,.0f} hrs/yr</div>
      <div class="delta">on these 5 issue types alone</div>
    </div>
    <div class="kpi">
      <div class="k">Stated adoption assumption</div>
      <div class="v">{adoption_rate:.0f}%</div>
      <div class="delta">deliberately conservative, disclosed</div>
    </div>
    <div class="kpi">
      <div class="k">Projected annual impact</div>
      <div class="v">${dollar_impact:,.0f}</div>
      <div class="delta good">{deflected_hours:.0f} technician-hours/yr, {deflected_tickets:.0f} tickets deflected</div>
    </div>
  </div>

  <section>
    <h2>Technician-hours at stake, by issue (annualized)</h2>
    <div class="sub">Ranked by total resolution time, not ticket count &mdash; a less frequent but slower issue can outweigh a more frequent, quick one.</div>
    <div class="panel">{chart_svg}</div>
  </section>

  <section>
    <h2>Two registers of technical writing, one problem</h2>
    <div class="sub">The 5 KB articles are written for end users troubleshooting alone. The runbook is written for a technician mid-incident &mdash; same underlying issue (VPN), different reader, different job.</div>
    <div class="roi-grid">
      <div class="roi-card net">
        <div class="k">End-user register</div>
        <div class="v">5 KB articles</div>
        <div class="sub2">plain language, "if this doesn't work" escape hatches, no jargon</div>
      </div>
      <div class="roi-card">
        <div class="k">Technician register</div>
        <div class="v">1 incident runbook</div>
        <div class="sub2">VPN gateway outage: checklist steps, target times, escalation contacts</div>
      </div>
      <div class="roi-card">
        <div class="k">Why VPN gets both</div>
        <div class="v">Worst SLA category</div>
        <div class="sub2">Network &amp; VPN was IT Case 01's worst-performing category at 64.8% compliance</div>
      </div>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; built from <span class="mono">src/deflection_analysis.py</span> &middot; IT Support case, IT &amp; Cybersecurity track
  </footer>
</div>
</body>
</html>
"""

with open("visuals/kb-runbook-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/kb-runbook-exhibit.html")
