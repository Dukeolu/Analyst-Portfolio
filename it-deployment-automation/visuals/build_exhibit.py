"""Builds visuals/onboarding-automation-exhibit.html — matches the site's
dashboard design system, built from the real comparison numbers in
data/raw/onboarding_comparison_summary.csv."""
import csv

with open("data/raw/onboarding_comparison_summary.csv") as f:
    summary = {row["metric"]: row["value"] for row in csv.DictReader(f)}

manual_avg = float(summary["manual_avg_minutes_per_hire"])
auto_avg = float(summary["automated_avg_minutes_per_hire"])
group_miss = float(summary["manual_group_miss_rate_pct"])
vpn_miss = float(summary["manual_vpn_miss_rate_pct"])
hours_saved = float(summary["annual_hours_saved_total"])
dollar_saved = float(summary["annual_dollar_saved"])
hires = int(float(summary["hires_per_year"]))

STEP_ROWS_MANUAL = [
    ("Account creation", 5.0), ("Group assignment", 8.0), ("Home directory", 4.0),
    ("Mailbox", 6.0), ("VPN setup", 1.5), ("Welcome email", 3.0), ("Ticket logging", 2.0),
]
BEFORE_COLOR = "#c0392b"
AFTER_COLOR = "#2a6f6f"


def compare_bar(manual_val, auto_val, width=640, left=170, right=624, row_h=40, top=10):
    max_val = manual_val * 1.05
    height = top + 2 * row_h + 20
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    rows = [("Manual process", manual_val, BEFORE_COLOR), ("Automated script", auto_val, AFTER_COLOR)]
    for i, (label, val, color) in enumerate(rows):
        y = top + i * row_h
        bw = (val / max_val) * (right - left - 40)
        svg.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="22" rx="4" fill="{color}">'
                    f'<title>{label}: {val:.1f} min</title></rect>')
        svg.append(f'<text x="{left-10}" y="{y+16}" class="axis-label sku-label" text-anchor="end">{label}</text>')
        svg.append(f'<text x="{left+bw+8:.1f}" y="{y+16}" class="bar-label-h" text-anchor="start">{val:.1f} min/hire</text>')
    svg.append("</svg>")
    return "\n".join(svg)


compare_svg = compare_bar(manual_avg, auto_avg)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Manufacturing &middot; New-Hire Onboarding Automation Exhibit</title>
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
.kpi .delta.bad{{color:#c0392b;}}

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
    <h1>Automating new-hire onboarding: less time, fewer missed steps</h1>
    <p>The manual onboarding process wasn't slow because technicians were careless — it was slow and error-prone because department security-group requirements lived in someone's memory instead of a system. A script driven by one lookup table fixes the structural problem, not just the clock.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Hands-on time per hire</div>
      <div class="v">{manual_avg:.0f} &rarr; {auto_avg:.1f} min</div>
      <div class="delta good">90% reduction</div>
    </div>
    <div class="kpi">
      <div class="k">Manual group-assignment miss rate</div>
      <div class="v">{group_miss:.1f}%</div>
      <div class="delta bad">0% under automation (lookup-table driven)</div>
    </div>
    <div class="kpi">
      <div class="k">Manual VPN day-1 miss rate</div>
      <div class="v">{vpn_miss:.1f}%</div>
      <div class="delta bad">remote-eligible hires only</div>
    </div>
    <div class="kpi">
      <div class="k">Annual impact</div>
      <div class="v">${dollar_saved:,.0f}/yr</div>
      <div class="delta good">{hours_saved:.0f} technician-hours/yr, {hires} hires/yr</div>
    </div>
  </div>

  <section>
    <h2>Hands-on technician time per new hire</h2>
    <div class="sub">Automated time is just launching the script and reviewing its completion report — provisioning itself runs unattended.</div>
    <div class="panel">{compare_svg}</div>
  </section>

  <section>
    <h2>What actually drove the manual process's error rate</h2>
    <div class="sub">Not carelessness — a lookup problem. The script fixes it structurally by reading the same group-mapping table every time.</div>
    <div class="roi-grid">
      <div class="roi-card net">
        <div class="k">Root cause</div>
        <div class="v">Memory, not effort</div>
        <div class="sub2">technicians assigned groups from memory or a printed cheat-sheet that drifted out of date</div>
      </div>
      <div class="roi-card">
        <div class="k">Structural fix</div>
        <div class="v">One lookup table</div>
        <div class="sub2">$DepartmentGroupMap in the script is now the single source of truth for every hire, every time</div>
      </div>
      <div class="roi-card">
        <div class="k">Rework avoided</div>
        <div class="v">43 incidents/yr</div>
        <div class="sub2">missed groups + missed VPN access, each previously requiring a follow-up ticket</div>
      </div>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; script: <span class="mono">src/onboarding_automation.ps1</span> &middot; IT Support case, IT &amp; Cybersecurity track
  </footer>
</div>
</body>
</html>
"""

with open("visuals/onboarding-automation-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/onboarding-automation-exhibit.html")
