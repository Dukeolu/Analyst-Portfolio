"""Builds visuals/ticket-triage-exhibit.html — a self-contained inline-SVG
dashboard matching the site's existing dashboard design system, built from
the real analysis numbers (see notebooks/ticket_triage_analysis.ipynb)."""

SLA_BY_CATEGORY = [
    ("Network & VPN", 64.8),
    ("Software Install", 83.6),
    ("Hardware", 93.9),
    ("Email & Calendar", 98.6),
    ("Account Access", 99.2),
    ("Password Reset", 100.0),
]

RESOLUTION_BY_MATCH = [
    ("Network & VPN", 7.93, 17.44),
    ("Software Install", 6.33, 12.76),
    ("Hardware", 3.92, 7.95),
    ("Email & Calendar", 2.02, 3.83),
    ("Account Access", 1.27, 2.84),
    ("Password Reset", 0.40, 0.86),
]

WASTED_HOURS = [
    ("Network & VPN", 762.5),
    ("Software Install", 471.4),
    ("Hardware", 461.8),
    ("Email & Calendar", 194.2),
    ("Account Access", 158.4),
    ("Password Reset", 80.3),
]

MATCH_COLOR = "#5C7A52"
MISMATCH_COLOR = "#c0392b"
WASTE_COLOR = "#eb6834"


def hbar_chart(rows, value_fmt, max_val, color_fn, width=640, left=170, right=624, row_h=34, top=10):
    n = len(rows)
    height = top + n * row_h + 10
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    for i, (label, val) in enumerate(rows):
        y = top + i * row_h
        bar_w = (val / max_val) * (right - left - 40)
        color = color_fn(val)
        svg.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="20" rx="4" fill="{color}">'
                    f'<title>{label}: {value_fmt(val)}</title></rect>')
        svg.append(f'<text x="{left-10}" y="{y+14}" class="axis-label sku-label" text-anchor="end">{label}</text>')
        svg.append(f'<text x="{left+bar_w+8:.1f}" y="{y+14}" class="bar-label-h" text-anchor="start">{value_fmt(val)}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def grouped_hbar_chart(rows, value_fmt, max_val, width=640, left=170, right=624, row_h=48, top=10):
    """rows: list of (label, matched_val, mismatched_val)."""
    n = len(rows)
    height = top + n * row_h + 10
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    for i, (label, matched_v, mismatch_v) in enumerate(rows):
        y = top + i * row_h
        bw_matched = (matched_v / max_val) * (right - left - 40)
        bw_mismatch = (mismatch_v / max_val) * (right - left - 40)
        svg.append(f'<rect x="{left}" y="{y}" width="{bw_matched:.1f}" height="16" rx="3" fill="{MATCH_COLOR}">'
                    f'<title>{label} (specialist match): {value_fmt(matched_v)}</title></rect>')
        svg.append(f'<text x="{left+bw_matched+8:.1f}" y="{y+13}" class="bar-label-h" text-anchor="start">{value_fmt(matched_v)}</text>')
        y2 = y + 20
        svg.append(f'<rect x="{left}" y="{y2}" width="{bw_mismatch:.1f}" height="16" rx="3" fill="{MISMATCH_COLOR}">'
                    f'<title>{label} (off-specialty): {value_fmt(mismatch_v)}</title></rect>')
        svg.append(f'<text x="{left+bw_mismatch+8:.1f}" y="{y2+13}" class="bar-label-h" text-anchor="start">{value_fmt(mismatch_v)}</text>')
        svg.append(f'<text x="{left-10}" y="{y+18}" class="axis-label sku-label" text-anchor="end">{label}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


sla_rows = SLA_BY_CATEGORY
sla_svg = hbar_chart(sla_rows, lambda v: f"{v:.1f}%", max_val=105,
                      color_fn=lambda v: MISMATCH_COLOR if v < 90 else MATCH_COLOR)

resolution_svg = grouped_hbar_chart(RESOLUTION_BY_MATCH, lambda v: f"{v:.1f}h", max_val=20)

wasted_rows = WASTED_HOURS
wasted_svg = hbar_chart(wasted_rows, lambda v: f"{v:.0f}h", max_val=800, color_fn=lambda v: WASTE_COLOR)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Manufacturing &middot; Help Desk Triage Exhibit</title>
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

.legend{{display:flex; gap:18px; font-size:12.5px; color:var(--ink-soft); margin-bottom:10px;}}
.legend span{{display:inline-flex; align-items:center; gap:6px;}}
.swatch{{width:10px; height:10px; border-radius:3px; display:inline-block;}}

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
    <h1>Why does the help desk's own SLA number not match user complaints?</h1>
    <p>92.4% overall SLA compliance looks fine in monthly reporting. It's hiding a specific, fixable problem: tickets are assigned "next available technician," ignoring specialty, and that mismatch &mdash; not category complexity alone &mdash; is what's driving the complaints.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Overall SLA compliance</div>
      <div class="v">92.4%</div>
      <div class="delta">the number leadership already sees</div>
    </div>
    <div class="kpi">
      <div class="k">Network &amp; VPN SLA compliance</div>
      <div class="v">64.8%</div>
      <div class="delta bad">worst of any category</div>
    </div>
    <div class="kpi">
      <div class="k">Off-specialty assignment rate</div>
      <div class="v">73.8%</div>
      <div class="delta">routing ignores specialty today</div>
    </div>
    <div class="kpi">
      <div class="k">Recommended fix</div>
      <div class="v">$91,754/yr</div>
      <div class="delta good">no new hires required</div>
    </div>
  </div>

  <section>
    <h2>SLA compliance by category</h2>
    <div class="sub">The 92.4% overall figure averages away a real, concentrated problem in two categories.</div>
    <div class="panel">{sla_svg}</div>
  </section>

  <section>
    <h2>The mechanism: resolution time, specialist match vs. off-specialty</h2>
    <div class="sub">Off-specialty assignment roughly doubles (or worse) resolution time in every category &mdash; worst in absolute hours for the three most complex ones.</div>
    <div class="panel">
      <div class="legend">
        <span><span class="swatch" style="background:{MATCH_COLOR}"></span>Specialist match</span>
        <span><span class="swatch" style="background:{MISMATCH_COLOR}"></span>Off-specialty</span>
      </div>
      {resolution_svg}
    </div>
  </section>

  <section>
    <h2>Wasted technician-hours by category (26 weeks observed)</h2>
    <div class="sub">Off-specialty resolution time minus that category's own median specialist-handled time. Ranks where a routing fix matters most.</div>
    <div class="panel">{wasted_svg}</div>
  </section>

  <section>
    <h2>What a realistic routing fix actually recovers</h2>
    <div class="sub">Capacity-constrained simulation: specialist-first routing, overflow to round-robin only when specialists are busy (6 hrs/week/specialist assumed for reactive ticket work).</div>
    <div class="roi-grid">
      <div class="roi-card net">
        <div class="k">Recovered by routing alone</div>
        <div class="v">$91,754/yr</div>
        <div class="sub2">SLA compliance 92.4% &rarr; 93.8% &middot; zero capex</div>
      </div>
      <div class="roi-card">
        <div class="k">Fully solved by routing</div>
        <div class="v">3 of 6 categories</div>
        <div class="sub2">Account Access, Email &amp; Calendar, Password Reset</div>
      </div>
      <div class="roi-card">
        <div class="k">Still capacity-constrained</div>
        <div class="v">Network &amp; VPN worst</div>
        <div class="sub2">only 18.8% of its mismatched tickets convert &mdash; needs added specialist capacity, not just routing</div>
      </div>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; built from <span class="mono">notebooks/ticket_triage_analysis.ipynb</span> &middot; IT Support case, IT &amp; Cybersecurity track
  </footer>
</div>
</body>
</html>
"""

with open("ticket-triage-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/ticket-triage-exhibit.html")
