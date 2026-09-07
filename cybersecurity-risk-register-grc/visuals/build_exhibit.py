"""Builds visuals/risk-register-exhibit.html — matches the site's dashboard
design system, built from the real risk register and GRC rollup numbers."""
import csv
from collections import defaultdict

with open("data/raw/risk_register.csv") as f:
    risks = list(csv.DictReader(f))

with open("data/raw/grc_summary.csv") as f:
    summary = {row["metric"]: row["value"] for row in csv.DictReader(f)}

with open("data/raw/csf_coverage.csv") as f:
    csf = list(csv.DictReader(f))

STATUS_COLOR = {
    "Closed": "#2a6f6f",
    "Open": "#c0392b",
    "In Progress": "#b5652f",
    "Risk Accepted": "#7a5fa0",
    "Monitoring": "#3d7ab5",
}
ACCENT = "#8b2f2f"


def heat_map(width=560, cell=88, pad_left=70, pad_top=20):
    """5x5 likelihood (x) x impact (y) grid, residual position, one dot per risk."""
    height = pad_top + cell * 5 + 40
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    # background cells, colored low(green)->high(red) by L*I
    for li in range(1, 6):
        for im in range(1, 6):
            score = li * im
            # color scale: green -> amber -> red
            if score <= 6:
                fill = "#8fbf8f"
            elif score <= 12:
                fill = "#e0c468"
            elif score <= 19:
                fill = "#d98f5f"
            else:
                fill = "#c0392b"
            x = pad_left + (li - 1) * cell
            y = pad_top + (5 - im) * cell
            svg.append(f'<rect x="{x}" y="{y}" width="{cell-2}" height="{cell-2}" fill="{fill}" opacity="0.28" rx="4"/>')
    # axis labels
    for li in range(1, 6):
        x = pad_left + (li - 1) * cell + cell / 2
        svg.append(f'<text x="{x:.1f}" y="{pad_top+5*cell+18}" text-anchor="middle" class="axis-label">{li}</text>')
    for im in range(1, 6):
        y = pad_top + (5 - im) * cell + cell / 2 + 4
        svg.append(f'<text x="{pad_left-14}" y="{y:.1f}" text-anchor="end" class="axis-label">{im}</text>')
    svg.append(f'<text x="{pad_left+2.5*cell:.1f}" y="{pad_top+5*cell+36}" text-anchor="middle" class="sku-label">Residual likelihood &rarr;</text>')
    svg.append(f'<text x="14" y="{pad_top+2.5*cell:.1f}" text-anchor="middle" class="sku-label" transform="rotate(-90,14,{pad_top+2.5*cell:.1f})">Residual impact &rarr;</text>')

    # jitter dots that share a cell so they don't fully overlap
    cell_occupants = defaultdict(list)
    for r in risks:
        key = (int(r["residual_likelihood"]), int(r["residual_impact"]))
        cell_occupants[key].append(r)

    for (li, im), items in cell_occupants.items():
        n = len(items)
        for idx, r in enumerate(items):
            cx = pad_left + (li - 1) * cell + cell / 2
            cy = pad_top + (5 - im) * cell + cell / 2
            if n > 1:
                offset = (idx - (n - 1) / 2) * 16
                cx += offset
            color = STATUS_COLOR.get(r["status"], "#888")
            svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="{color}" stroke="var(--paper)" stroke-width="2">'
                        f'<title>{r["risk_id"]}: {r["title"]} ({r["status"]})</title></circle>')
            svg.append(f'<text x="{cx:.1f}" y="{cy+3.5:.1f}" text-anchor="middle" font-size="8.5" fill="white" font-family="IBM Plex Mono, monospace">{r["risk_id"][1:]}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def csf_chart(width=640, left=140, right=624, row_h=38, top=10):
    n = len(csf)
    height = top + n * row_h + 10
    max_val = max(float(r["residual_score_sum"]) for r in csf)
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    for i, r in enumerate(csf):
        y = top + i * row_h
        val = float(r["residual_score_sum"])
        bw = (val / max_val) * (right - left - 60) if max_val else 0
        svg.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="18" rx="3" fill="{ACCENT}">'
                    f'<title>{r["csf_function"]}: {val:.0f} residual points across {r["risk_count"]} risks</title></rect>')
        svg.append(f'<text x="{left+bw+8:.1f}" y="{y+13}" class="bar-label-h" text-anchor="start">{val:.0f} pts &middot; {r["risk_count"]} risks</text>')
        svg.append(f'<text x="{left-10}" y="{y+13}" class="axis-label sku-label" text-anchor="end">{r["csf_function"]}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


heat_svg = heat_map()
csf_svg = csf_chart()

total_risks = int(summary["total_risks"])
inherent = float(summary["total_inherent_score"])
residual = float(summary["total_residual_score"])
reduction = float(summary["overall_reduction_pct"])
open_count = int(summary["open_count"])
closed_count = int(summary["closed_count"])
open_residual = float(summary["open_risk_residual_sum"])

legend_html = "".join(
    f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:16px;font-size:12px;color:var(--ink-soft);">'
    f'<span style="width:10px;height:10px;border-radius:50%;background:{color};display:inline-block;"></span>{status}</span>'
    for status, color in STATUS_COLOR.items()
)

top_open = sorted([r for r in risks if r["status"] in ("Open", "In Progress")],
                   key=lambda r: -float(r["residual_score"]))[:5]
top_open_rows = "".join(
    f'<tr><td class="mono">{r["risk_id"]}</td><td>{r["title"]}</td><td class="mono">{int(float(r["residual_score"]))}</td>'
    f'<td>{r["csf_function"]}</td><td>{r["owner"]}</td><td class="mono">{r["target_date"]}</td></tr>'
    for r in top_open
)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Manufacturing &middot; Risk Register &amp; GRC Exhibit</title>
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
    <h1>One risk register, rolled up from every case in the track</h1>
    <p>{total_risks} risks, each citing the specific case it came from &mdash; Log4Shell and the VPN gateway RCE from the vulnerability assessment, the hardening exceptions, the four gaps the incident response tabletop surfaced. This is where those findings get tracked to closure instead of staying one-off write-ups.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Total risks tracked</div>
      <div class="v">{total_risks}</div>
      <div class="delta">across 6 NIST CSF 2.0 functions</div>
    </div>
    <div class="kpi">
      <div class="k">Overall risk reduction</div>
      <div class="v">{reduction:.1f}%</div>
      <div class="delta good">{inherent:.0f} &rarr; {residual:.0f} points, inherent to residual</div>
    </div>
    <div class="kpi">
      <div class="k">Closed</div>
      <div class="v">{closed_count} of {total_risks}</div>
      <div class="delta good">remediated with a verifiable case behind each one</div>
    </div>
    <div class="kpi">
      <div class="k">Open, still tracked</div>
      <div class="v">{open_count}</div>
      <div class="delta bad">{open_residual:.0f} residual points remaining</div>
    </div>
  </div>

  <section>
    <h2>Residual risk heat map</h2>
    <div class="sub">Every risk plotted by residual likelihood &times; impact, colored by status. Two risks (R06, R14) still sit in the top-right cell.</div>
    <div class="panel">
      {heat_svg}
      <div style="padding:4px 0 14px;">{legend_html}</div>
    </div>
  </section>

  <section>
    <h2>Residual risk by NIST CSF 2.0 function</h2>
    <div class="sub">Protect carries the most tracked risk points &mdash; expected, since patching and hardening produce the most individually-scored findings; Detect and Govern are smaller in count but carry real weight per risk.</div>
    <div class="panel">{csf_svg}</div>
  </section>

  <section>
    <h2>Top open risks, by residual score</h2>
    <div class="sub">What the register says to fix next, ranked &mdash; not a flat unordered backlog.</div>
    <div class="panel">
      <table>
        <thead><tr><th>ID</th><th>Risk</th><th>Residual</th><th>CSF</th><th>Owner</th><th>Target</th></tr></thead>
        <tbody>{top_open_rows}</tbody>
      </table>
    </div>
  </section>

  <footer>
    Data and workbook are simulated (see README for methodology) &middot; built from <span class="mono">src/grc_analysis.py</span> &middot; full working register: <span class="mono">reports/risk-register.xlsx</span> &middot; Cybersecurity case, IT &amp; Cybersecurity track
  </footer>
</div>
</body>
</html>
"""

with open("visuals/risk-register-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/risk-register-exhibit.html")
