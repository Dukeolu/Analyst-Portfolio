"""Builds visuals/battery-value-exhibit.html — a self-contained inline-SVG dashboard
matching the site's existing dashboard design system (same CSS tokens/classes as the
4 existing DA case dashboards), built from the real analysis numbers."""

CAPTURE = [
    ("Solent Solar Park", "Solar", 76.3),
    ("Fenland Solar Array", "Solar", 76.3),
    ("Dee Solar Farm", "Solar", 76.3),
    ("Pennine Wind Farm", "Wind", 106.1),
    ("Cambria Wind Farm", "Wind", 107.3),
]
UPLIFT = [
    ("Solent Solar Park", "Solar", 216474),
    ("Fenland Solar Array", "Solar", 214343),
    ("Dee Solar Farm", "Solar", 185166),
    ("Pennine Wind Farm", "Wind", 151286),
    ("Cambria Wind Farm", "Wind", 146451),
]
MECHANISM = [(1, 637, 35.17), (2, 1735, 32.54), (3, 2645, 25.68), (4, 3323, 19.72), (5, 3914, 16.02)]

SOLAR_COLOR = "#c0742a"
WIND_COLOR = "#2a6f6f"


def hbar_chart(rows, value_fmt, max_val, width=640, left=170, right=624, row_h=34, top=10):
    """rows: list of (label, color, value). Horizontal bars from x=left."""
    n = len(rows)
    height = top + n * row_h + 10
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    for i, (label, color, val) in enumerate(rows):
        y = top + i * row_h
        bar_w = (val / max_val) * (right - left - 40)
        svg.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="20" rx="4" fill="{color}">'
                    f'<title>{label}: {value_fmt(val)}</title></rect>')
        svg.append(f'<text x="{left-10}" y="{y+14}" class="axis-label sku-label" text-anchor="end">{label}</text>')
        svg.append(f'<text x="{left+bar_w+8:.1f}" y="{y+14}" class="bar-label-h" text-anchor="start">{value_fmt(val)}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def line_chart(points, width=640, height=260, left=54, right=624, top=16, bottom=228):
    xs = [p[0] for p in points]
    ys = [p[2] for p in points]
    ymin, ymax = min(ys) - 3, max(ys) + 3
    def xf(x):
        return left + (x - min(xs)) / (max(xs) - min(xs)) * (right - left)
    def yf(y):
        return bottom - (y - ymin) / (ymax - ymin) * (bottom - top)

    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    # gridlines at 4 y-ticks
    for frac in [0, 0.33, 0.66, 1.0]:
        yval = ymin + frac * (ymax - ymin)
        y = yf(yval)
        svg.append(f'<line x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>')
        svg.append(f'<text x="{left-8}" y="{y+4:.1f}" class="axis-label" text-anchor="end">£{yval:.0f}</text>')
    pts = " ".join(f"{xf(x):.1f},{yf(y):.1f}" for x, _, y in points)
    svg.append(f'<polyline points="{pts}" class="trend-line"/>')
    for x, nmw, y in points:
        svg.append(f'<circle cx="{xf(x):.1f}" cy="{yf(y):.1f}" r="4" class="trend-dot">'
                    f'<title>Quintile {x} (avg {nmw:,} MW national solar): £{y:.2f}/MWh avg price</title></circle>')
        svg.append(f'<text x="{xf(x):.1f}" y="{bottom+20}" class="axis-label" text-anchor="middle">Q{x}</text>')
    svg.append(f'<line x1="{left}" x2="{right}" y1="{bottom}" y2="{bottom}" class="baseline"/>')
    svg.append("</svg>")
    return "\n".join(svg)


capture_rows = [(n, SOLAR_COLOR if t == "Solar" else WIND_COLOR, v) for n, t, v in CAPTURE]
capture_svg = hbar_chart(capture_rows, lambda v: f"{v:.1f}%", max_val=115)

uplift_rows = [(n, SOLAR_COLOR if t == "Solar" else WIND_COLOR, v) for n, t, v in UPLIFT]
uplift_svg = hbar_chart(uplift_rows, lambda v: f"£{v:,.0f}", max_val=230000)

mechanism_svg = line_chart(MECHANISM)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Renewables &middot; Battery Storage Value Exhibit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F5F4; --paper-raised:#FBFCFB; --ink:#0b0b0b; --ink-soft:#52514e; --ink-faint:#898781;
  --line:#D6DCDA; --line-strong:#B9C2C0; --accent:#B4802E; --accent-ink:#7A5620; --accent-wash:#F3E7D2;
  --good:#0ca30c;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#12161C; --paper-raised:#181D25; --ink:#ffffff; --ink-soft:#c3c2b7; --ink-faint:#6E7885;
    --line:#2A3038; --line-strong:#3A414B; --accent:#D9A85C; --accent-ink:#EFCE96; --accent-wash:#2C2417;
    --good:#0ca30c;
  }}
}}
:root[data-theme="dark"]{{
  --paper:#12161C; --paper-raised:#181D25; --ink:#ffffff; --ink-soft:#c3c2b7; --ink-faint:#6E7885;
  --line:#2A3038; --line-strong:#3A414B; --accent:#D9A85C; --accent-ink:#EFCE96; --accent-wash:#2C2417;
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

.chart-svg .grid{{stroke:var(--line); stroke-width:1;}}
.chart-svg .baseline{{stroke:var(--line-strong); stroke-width:1;}}
.chart-svg .axis-label{{fill:var(--ink-faint); font-size:11px; font-family:"IBM Plex Mono",monospace;}}
.chart-svg .sku-label{{fill:var(--ink-soft); font-family:"IBM Plex Sans",sans-serif;}}
.chart-svg .bar-label-h{{fill:var(--ink); font-size:12px; font-family:"IBM Plex Mono",monospace; font-weight:500;}}
.chart-svg .trend-line{{fill:none; stroke:#2a78d6; stroke-width:2;}}
.chart-svg .trend-dot{{fill:#2a78d6; stroke:var(--paper-raised); stroke-width:1.5;}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]) .chart-svg .trend-line{{stroke:#3987e5;}}
  :root:not([data-theme="light"]) .chart-svg .trend-dot{{stroke:var(--paper-raised);}}
}}
:root[data-theme="dark"] .chart-svg .trend-line{{stroke:#3987e5;}}

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
    <div class="eyebrow">Energy &amp; Investment Analytics &middot; Meridian Renewables (simulated)</div>
    <h1>Where would battery storage pay off?</h1>
    <p>Five renewable sites, one battery investment budget this year. Solar's own output is concentrated exactly when the wholesale market is most oversupplied &mdash; so solar sites are structurally paid less per MWh than wind, and that is precisely the gap a co-located battery is best positioned to close.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Solar capture rate</div>
      <div class="v">76.3%</div>
      <div class="delta">of the simple average market price</div>
    </div>
    <div class="kpi">
      <div class="k">Wind capture rate</div>
      <div class="v">106-107%</div>
      <div class="delta good">outperforms the market average</div>
    </div>
    <div class="kpi">
      <div class="k">Top site battery uplift</div>
      <div class="v">£216,474/yr</div>
      <div class="delta">Solent Solar Park</div>
    </div>
    <div class="kpi">
      <div class="k">Recommended first investment</div>
      <div class="v">3.4-yr payback</div>
      <div class="delta good">NPV £2.72M &middot; IRR 28.5%</div>
    </div>
  </div>

  <section>
    <h2>Capture rate by site</h2>
    <div class="sub">Volume-weighted price received &divide; simple average market price. Solar under-earns the market; wind over-earns it.</div>
    <div class="panel">
      <div class="legend">
        <span><span class="swatch" style="background:{SOLAR_COLOR}"></span>Solar</span>
        <span><span class="swatch" style="background:{WIND_COLOR}"></span>Wind</span>
      </div>
      {capture_svg}
    </div>
  </section>

  <section>
    <h2>The mechanism: price falls as national solar output rises</h2>
    <div class="sub">Midday hours bucketed by national solar output (quintile 5 = highest). Every solar site generates at once &mdash; that simultaneity is what suppresses the price.</div>
    <div class="panel">{mechanism_svg}</div>
  </section>

  <section>
    <h2>Estimated annual battery arbitrage uplift, by site</h2>
    <div class="sub">A 10&nbsp;MW / 20&nbsp;MWh behind-the-meter battery, time-shifting each site's own generation from its cheapest to priciest hours daily. The worst-paid sites gain the most.</div>
    <div class="panel">
      <div class="legend">
        <span><span class="swatch" style="background:{SOLAR_COLOR}"></span>Solar</span>
        <span><span class="swatch" style="background:{WIND_COLOR}"></span>Wind</span>
      </div>
      {uplift_svg}
    </div>
  </section>

  <section>
    <h2>Investment case: best-ranked vs. worst-ranked site</h2>
    <div class="sub">10&nbsp;MW/20&nbsp;MWh, £1.8M capex, arbitrage + capacity-market revenue, 15-year NPV @ 8% discount rate.</div>
    <div class="roi-grid">
      <div class="roi-card net">
        <div class="k">Solent Solar Park &mdash; recommended first</div>
        <div class="v">NPV £2,720,122</div>
        <div class="sub2">IRR 28.5% &middot; payback 3.4 years</div>
      </div>
      <div class="roi-card">
        <div class="k">Cambria Wind Farm &mdash; lowest-ranked</div>
        <div class="v">NPV £2,182,925</div>
        <div class="sub2">IRR 24.7% &middot; payback 3.9 years</div>
      </div>
      <div class="roi-card">
        <div class="k">Gap driven entirely by arbitrage</div>
        <div class="v">+£537,197 NPV</div>
        <div class="sub2">from prioritising Solent over Cambria</div>
      </div>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; built from <span class="mono">notebooks/battery_value_analysis.ipynb</span> &middot; Energy &amp; Investment Analytics case, Data Analyst track
  </footer>
</div>
</body>
</html>
"""

with open("battery-value-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/battery-value-exhibit.html")
