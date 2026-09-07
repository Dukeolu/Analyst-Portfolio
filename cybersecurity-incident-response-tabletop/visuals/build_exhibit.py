"""Builds visuals/tabletop-exhibit.html — matches the site's dashboard
design system, built from the real timeline analysis numbers."""
import csv

with open("data/raw/timeline_metrics.csv") as f:
    metrics = {row["metric"]: float(row["hours"]) for row in csv.DictReader(f)}

with open("data/raw/tabletop_timeline.csv") as f:
    events = list(csv.DictReader(f))

ACCENT = "#8b2f2f"
DETECT_COLOR = "#c0392b"
CONTAIN_COLOR = "#b5652f"
ERADICATE_COLOR = "#9c7a2f"
RECOVER_COLOR = "#2a6f6f"

total = metrics["total_incident_duration"]

# Phase spans, derived from first-occurrence hours in the timeline
PHASES = [
    ("Undetected (Initial Access + Discovery/Lateral Movement)", 0.0, metrics["time_to_detect"], DETECT_COLOR),
    ("Detection", metrics["time_to_detect"], metrics["time_to_detect"] + metrics["time_to_contain"], CONTAIN_COLOR),
    ("Containment", metrics["time_to_detect"] + metrics["time_to_contain"],
     metrics["time_to_detect"] + metrics["time_to_contain"] + metrics["time_to_eradicate"], ERADICATE_COLOR),
    ("Eradication + Recovery", metrics["time_to_detect"] + metrics["time_to_contain"] + metrics["time_to_eradicate"],
     total, RECOVER_COLOR),
]


def timeline_chart(width=760, left=20, right=740, top=20, height=90):
    svg = [f'<svg viewBox="0 0 {width} {height+60}" width="100%" height="{height+60}" role="img" class="chart-svg">']
    track_w = right - left
    for label, start, end, color in PHASES:
        x = left + (start / total) * track_w
        w = ((end - start) / total) * track_w
        svg.append(f'<rect x="{x:.1f}" y="{top}" width="{w:.1f}" height="{height-40}" fill="{color}" opacity="0.85" rx="3">'
                    f'<title>{label}: {end-start:.1f}h</title></rect>')
        mid = x + w / 2
        svg.append(f'<text x="{mid:.1f}" y="{top+height-48}" text-anchor="middle" class="bar-label-h" fill="white" font-size="11">{end-start:.1f}h</text>')
    # hour ticks every 8 hours
    for h in range(0, int(total) + 1, 8):
        x = left + (h / total) * track_w
        svg.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top+height-40}" y2="{top+height-30}" class="baseline"/>')
        svg.append(f'<text x="{x:.1f}" y="{top+height-14}" text-anchor="middle" class="axis-label">{h}h</text>')
    # phase legend below
    ly = top + height + 8
    lx = left
    for label, start, end, color in PHASES:
        svg.append(f'<rect x="{lx}" y="{ly}" width="10" height="10" rx="2" fill="{color}"/>')
        svg.append(f'<text x="{lx+16}" y="{ly+9}" class="sku-label" font-size="11.5">{label}</text>')
        lx += 16 + len(label) * 6.2 + 24
    svg.append("</svg>")
    return "\n".join(svg)


def event_list_html():
    rows = []
    for e in events:
        rows.append(
            f'<tr><td class="mono">{float(e["elapsed_hours"]):.1f}h</td>'
            f'<td>{e["phase"]}</td><td>{e["actor"]}</td><td>{e["event"]}</td></tr>'
        )
    return "\n".join(rows)


timeline_svg = timeline_chart()
event_rows = event_list_html()

time_to_detect = metrics["time_to_detect"]
time_to_contain = metrics["time_to_contain"]
time_to_eradicate = metrics["time_to_eradicate"]
time_to_recover = metrics["time_to_recover"]
active_encryption_window = metrics["active_encryption_window"]
data_loss_window = metrics["data_loss_window"]
volumes_affected = int(metrics["volumes_affected"])
volumes_total = int(metrics["volumes_total"])

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Manufacturing &middot; Incident Response Tabletop Exhibit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F1EF; --paper-raised:#FBF9F8; --ink:#0b0b0b; --ink-soft:#524d4a; --ink-faint:#8c8681;
  --line:#DCD5D0; --line-strong:#C2B8B2; --accent:#8b2f2f; --accent-ink:#6b2020; --accent-wash:#F2DEDE;
  --good:#0ca30c;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#1C1416; --paper-raised:#241A1D; --ink:#ffffff; --ink-soft:#c7bdb9; --ink-faint:#85787a;
    --line:#382A2C; --line-strong:#4A3838; --accent:#D98080; --accent-ink:#E8B0B0; --accent-wash:#2E1A1B;
    --good:#3fcf5f;
  }}
}}
:root[data-theme="dark"]{{
  --paper:#1C1416; --paper-raised:#241A1D; --ink:#ffffff; --ink-soft:#c7bdb9; --ink-faint:#85787a;
  --line:#382A2C; --line-strong:#4A3838; --accent:#D98080; --accent-ink:#E8B0B0; --accent-wash:#2E1A1B;
  --good:#3fcf5f;
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

table{{width:100%; border-collapse:collapse; font-size:13px;}}
th,td{{text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top;}}
th{{font-family:"IBM Plex Mono",monospace; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--ink-faint); font-weight:500;}}
td.mono{{white-space:nowrap;}}

footer{{border-top:1px solid var(--line); padding-top:18px; font-size:12px; color:var(--ink-faint);}}
</style>
</head>
<body>
<div class="shell">
  <header>
    <div class="eyebrow">Cybersecurity &middot; Meridian Manufacturing (simulated)</div>
    <h1>A ransomware tabletop, run before the real thing happens</h1>
    <p>A phished VPN account (user0147 &mdash; the same account flagged in the Log Analysis / Intrusion Detection case) leads to lateral movement, a stale vendor admin credential, and ransomware staged on a shared file server. This exercise plays the incident out end to end and times every phase.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Time to detect</div>
      <div class="v">{time_to_detect:.1f}h</div>
      <div class="delta bad">the dominant share of the 48h incident</div>
    </div>
    <div class="kpi">
      <div class="k">Time to contain</div>
      <div class="v">{time_to_contain:.1f}h</div>
      <div class="delta good">once detected, fast &amp; decisive</div>
    </div>
    <div class="kpi">
      <div class="k">Active encryption window</div>
      <div class="v">{active_encryption_window:.1f}h</div>
      <div class="delta">staging began before detection did</div>
    </div>
    <div class="kpi">
      <div class="k">Data loss</div>
      <div class="v">{volumes_affected} of {volumes_total} vols</div>
      <div class="delta">{data_loss_window:.0f}h since last backup</div>
    </div>
  </div>

  <section>
    <h2>Incident timeline, by phase</h2>
    <div class="sub">48 hours end to end &mdash; and 26 of them elapsed before anyone knew an incident was underway.</div>
    <div class="panel">{timeline_svg}</div>
  </section>

  <section>
    <h2>What the gap analysis found</h2>
    <div class="sub">Three concrete, fixable gaps &mdash; not "be more careful."</div>
    <div class="roi-grid">
      <div class="roi-card net">
        <div class="k">Biggest gap</div>
        <div class="v">Reporting path, not tech</div>
        <div class="sub2">the phishing click happened at hour 0; the employee's own report didn't reach IT for two days</div>
      </div>
      <div class="roi-card">
        <div class="k">Preventable entry point</div>
        <div class="v">Stale vendor account</div>
        <div class="sub2">a support account was still active and privileged 8 months after the engagement ended</div>
      </div>
      <div class="roi-card">
        <div class="k">Improvised response</div>
        <div class="v">No ransomware runbook</div>
        <div class="sub2">containment steps were worked out in real time &mdash; exactly what a tabletop should catch first</div>
      </div>
    </div>
  </section>

  <section>
    <h2>Full event log</h2>
    <div class="sub">Every inject, as played &mdash; see the After-Action Report for discussion and recommendations.</div>
    <div class="panel">
      <table>
        <thead><tr><th>Elapsed</th><th>Phase</th><th>Actor</th><th>Event</th></tr></thead>
        <tbody>{event_rows}</tbody>
      </table>
    </div>
  </section>

  <footer>
    Scenario and timeline are simulated (see README for methodology) &middot; built from <span class="mono">src/timeline_analysis.py</span> &middot; Cybersecurity case, IT &amp; Cybersecurity track
  </footer>
</div>
</body>
</html>
"""

with open("visuals/tabletop-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/tabletop-exhibit.html")
