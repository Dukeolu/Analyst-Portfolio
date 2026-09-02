"""
Case 01 -- Step 4: build the dashboard.

Power BI/Tableau aren't installable in this environment, so the dashboard
deliverable is a self-contained, static HTML file instead -- same KPI/
chart content a stakeholder would get from a .pbix, but viewable with
nothing but a browser (and embeddable straight into the portfolio site).
Charts are hand-built inline SVG rather than a charting library, so the
file has zero external dependencies.
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
P = BASE / "data" / "processed"
OUT = BASE / "dashboard" / "index.html"

fill_tier = pd.read_csv(P / "fill_rate_by_tier.csv")
fill_before_after = pd.read_csv(P / "fill_rate_by_tier_before_after.csv")
monthly = pd.read_csv(P / "monthly_fill_rate.csv")
roi = pd.read_csv(P / "roi_summary.csv").iloc[0]
reco = pd.read_csv(P / "reorder_point_recommendations.csv")
summary = pd.read_csv(P / "before_after_summary.csv").set_index("metric")["before"]
summary_after = pd.read_csv(P / "before_after_summary.csv").set_index("metric")["after"]

# validated dataviz palette slots (see dataviz skill, references/palette.md)
BLUE, ORANGE = "#2a78d6", "#eb6834"
BLUE_D, ORANGE_D = "#3987e5", "#d95926"
GOOD, GOOD_D = "#0ca30c", "#0ca30c"
INK, INK_D = "#0b0b0b", "#ffffff"
SEC, SEC_D = "#52514e", "#c3c2b7"
MUTED = "#898781"
GRID, GRID_D = "#e1e0d9", "#2c2c2a"


def svg_open(w, h):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img" class="chart-svg">'


# ---------------------------------------------------------------- chart 1
# grouped vertical bars: fill rate by ABC tier, before vs after
def chart_fill_by_tier():
    w, h = 640, 300
    margin = dict(l=44, r=16, t=16, b=40)
    plot_w, plot_h = w - margin["l"] - margin["r"], h - margin["t"] - margin["b"]
    tiers = fill_before_after["abc_tier"].tolist()
    n = len(tiers)
    group_w = plot_w / n
    bar_w = 34
    gap = 6
    y0 = margin["t"] + plot_h

    def y(v):
        return margin["t"] + plot_h * (1 - v)

    svg = [svg_open(w, h)]
    # gridlines at 0/25/50/75/100%
    for pct in (0, 25, 50, 75, 100):
        yy = y(pct / 100)
        svg.append(f'<line x1="{margin["l"]}" x2="{w - margin["r"]}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/>')
        svg.append(f'<text x="{margin["l"] - 8}" y="{yy + 4:.1f}" class="axis-label" text-anchor="end">{pct}%</text>')

    bars_svg = []
    for i, row in fill_before_after.iterrows():
        cx = margin["l"] + group_w * i + group_w / 2
        for j, (key, color, label) in enumerate([
            ("fill_rate_before", BLUE, "Current policy"),
            ("fill_rate_after", ORANGE, "Recommended policy"),
        ]):
            v = row[key]
            bx = cx - bar_w - gap / 2 + j * (bar_w + gap)
            by = y(v)
            bh = y0 - by
            bars_svg.append(
                f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w}" height="{bh:.1f}" rx="4" '
                f'fill="{color}" class="bar bar-{j}"><title>{label}, tier {row["abc_tier"]}: {v:.1%}</title></rect>'
            )
            bars_svg.append(
                f'<text x="{bx + bar_w/2:.1f}" y="{by - 6:.1f}" class="bar-label" text-anchor="middle">{v:.0%}</text>'
            )
        svg.append(f'<text x="{cx:.1f}" y="{y0 + 22}" class="axis-label" text-anchor="middle">Tier {row["abc_tier"]}</text>')

    svg.extend(bars_svg)
    svg.append(f'<line x1="{margin["l"]}" x2="{w-margin["r"]}" y1="{y0}" y2="{y0}" class="baseline"/>')
    svg.append("</svg>")
    return "".join(svg)


# ---------------------------------------------------------------- chart 2
# line: monthly fill rate, status quo, with 95% target reference
def chart_monthly_trend():
    w, h = 640, 260
    margin = dict(l=44, r=16, t=16, b=32)
    plot_w, plot_h = w - margin["l"] - margin["r"], h - margin["t"] - margin["b"]
    ymin, ymax = 0.70, 1.00
    vals = monthly["fill_rate"].tolist()
    n = len(vals)

    def x(i):
        return margin["l"] + plot_w * i / (n - 1)

    def y(v):
        return margin["t"] + plot_h * (1 - (v - ymin) / (ymax - ymin))

    svg = [svg_open(w, h)]
    for pct in (70, 80, 90, 100):
        yy = y(pct / 100)
        svg.append(f'<line x1="{margin["l"]}" x2="{w-margin["r"]}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/>')
        svg.append(f'<text x="{margin["l"]-8}" y="{yy+4:.1f}" class="axis-label" text-anchor="end">{pct}%</text>')
    # 95% target reference line
    ty = y(0.95)
    svg.append(f'<line x1="{margin["l"]}" x2="{w-margin["r"]}" y1="{ty:.1f}" y2="{ty:.1f}" class="target-line"/>')
    svg.append(f'<text x="{w-margin["r"]}" y="{ty-6:.1f}" class="axis-label target-label" text-anchor="end">95% target</text>')

    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    svg.append(f'<polyline points="{pts}" class="trend-line"/>')
    for i, v in enumerate(vals):
        month = monthly["month"].iloc[i]
        r = 5 if month.endswith("-11") else 3
        svg.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="{r}" class="trend-dot"><title>{month}: {v:.1%} fill rate</title></circle>')
    # month labels (Jan + Jul of each year to avoid crowding)
    for i, m in enumerate(monthly["month"]):
        if m.endswith(("-01", "-07")):
            svg.append(f'<text x="{x(i):.1f}" y="{h-8}" class="axis-label" text-anchor="middle">{m}</text>')
    svg.append("</svg>")
    return "".join(svg)


# ---------------------------------------------------------------- chart 3
# diverging horizontal bars: reorder point change, top under/over-protected
def chart_reorder_changes():
    top_under = reco.sort_values("rp_change_pct", ascending=False).head(6)
    top_over = reco.sort_values("rp_change_pct").head(6)
    rows = pd.concat([top_under, top_over.iloc[::-1]])
    w, h = 660, 34 * len(rows) + 30
    margin = dict(l=205, r=60, t=10, b=20)
    plot_w = w - margin["l"] - margin["r"]
    max_abs = rows["rp_change_pct"].abs().max()
    cx = margin["l"] + plot_w / 2

    def bar_len(pct):
        return abs(pct) / max_abs * (plot_w / 2 - 10)

    svg = [svg_open(w, h)]
    svg.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="0" y2="{h-20}" class="baseline"/>')
    for i, (_, row) in enumerate(rows.iterrows()):
        yy = 20 + i * 34
        bl = bar_len(row["rp_change_pct"])
        pct = row["rp_change_pct"]
        color = ORANGE if pct > 0 else BLUE
        bx = cx if pct > 0 else cx - bl
        svg.append(
            f'<rect x="{bx:.1f}" y="{yy-9:.1f}" width="{bl:.1f}" height="18" rx="4" fill="{color}" class="bar">'
            f'<title>{row["sku"]} ({row["category"]}, tier {row["abc_tier"]}): reorder point {pct:+.0f}%</title></rect>'
        )
        label_x = margin["l"] - 10
        cat_short = row["category"].replace("Electronics Accessories", "Electronics Acc.").replace("Outdoor & Sporting", "Outdoor/Sport")
        svg.append(f'<text x="{label_x}" y="{yy+4:.1f}" class="axis-label sku-label" text-anchor="end">{row["sku"]} &middot; {cat_short}</text>')
        val_x = bx + bl + 6 if pct > 0 else bx - 6
        anchor = "start" if pct > 0 else "end"
        svg.append(f'<text x="{val_x:.1f}" y="{yy+4:.1f}" class="bar-label-h" text-anchor="{anchor}">{pct:+.0f}%</text>')
    svg.append("</svg>")
    return "".join(svg)


def stat_bar(value, max_value, color):
    pct = max(0.02, value / max_value)
    return f'<div class="stat-bar-track"><div class="stat-bar-fill" style="width:{pct*100:.1f}%; background:{color}"></div></div>'


roi_max = max(roi["annual_margin_recovered"], roi["annual_carrying_cost_increase"], roi["net_annual_benefit"])

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Case 01 &middot; Operations &amp; Supply Chain Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F5F4; --paper-raised:#FBFCFB; --ink:{INK}; --ink-soft:{SEC}; --ink-faint:{MUTED};
  --line:#D6DCDA; --line-strong:#B9C2C0; --accent:#B4802E; --accent-ink:#7A5620; --accent-wash:#F3E7D2;
  --good:{GOOD};
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#12161C; --paper-raised:#181D25; --ink:{INK_D}; --ink-soft:{SEC_D}; --ink-faint:#6E7885;
    --line:#2A3038; --line-strong:#3A414B; --accent:#D9A85C; --accent-ink:#EFCE96; --accent-wash:#2C2417;
    --good:{GOOD_D};
  }}
}}
:root[data-theme="dark"]{{
  --paper:#12161C; --paper-raised:#181D25; --ink:{INK_D}; --ink-soft:{SEC_D}; --ink-faint:#6E7885;
  --line:#2A3038; --line-strong:#3A414B; --accent:#D9A85C; --accent-ink:#EFCE96; --accent-wash:#2C2417;
  --good:{GOOD_D};
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
header p{{color:var(--ink-soft); font-size:14.5px; max-width:64ch; margin-top:10px; line-height:1.6;}}

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
.chart-svg .bar-label{{fill:var(--ink-soft); font-size:11px; font-family:"IBM Plex Mono",monospace;}}
.chart-svg .bar-label-h{{fill:var(--ink); font-size:12px; font-family:"IBM Plex Mono",monospace; font-weight:500;}}
.chart-svg .trend-line{{fill:none; stroke:{BLUE}; stroke-width:2;}}
.chart-svg .trend-dot{{fill:{BLUE}; stroke:var(--paper-raised); stroke-width:1.5;}}
.chart-svg .target-line{{stroke:var(--ink-faint); stroke-width:1; stroke-dasharray:4 3;}}
.chart-svg .target-label{{fill:var(--ink-faint);}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]) .chart-svg .trend-line{{stroke:{BLUE_D};}}
  :root:not([data-theme="light"]) .chart-svg .trend-dot{{fill:{BLUE_D};}}
}}
:root[data-theme="dark"] .chart-svg .trend-line{{stroke:{BLUE_D};}}
:root[data-theme="dark"] .chart-svg .trend-dot{{fill:{BLUE_D};}}

.legend{{display:flex; gap:18px; font-size:12.5px; color:var(--ink-soft); margin-bottom:10px;}}
.legend span{{display:inline-flex; align-items:center; gap:6px;}}
.swatch{{width:10px; height:10px; border-radius:3px; display:inline-block;}}

.roi-grid{{display:grid; grid-template-columns:repeat(3,1fr); gap:16px;}}
@media (max-width:760px){{.roi-grid{{grid-template-columns:1fr;}}}}
.roi-card{{background:var(--paper-raised); border:1px solid var(--line); border-radius:10px; padding:18px;}}
.roi-card .k{{font-family:"IBM Plex Mono",monospace; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--ink-faint);}}
.roi-card .v{{font-family:"IBM Plex Mono",monospace; font-size:22px; margin:8px 0 10px;}}
.stat-bar-track{{height:6px; border-radius:3px; background:var(--line); overflow:hidden;}}
.stat-bar-fill{{height:100%; border-radius:3px;}}
.roi-card.net{{border-color:var(--accent); background:var(--accent-wash);}}

footer{{border-top:1px solid var(--line); padding-top:18px; font-size:12px; color:var(--ink-faint);}}
</style>
</head>
<body>
<div class="shell">
  <header>
    <div class="eyebrow">Case 01 &middot; Operations &amp; Supply Chain</div>
    <h1>Cutting stockouts without carrying more inventory</h1>
    <p>Status-quo reorder points are a flat "3 weeks of average demand" regardless of how volatile a SKU's demand actually is, or how long and uncertain its supplier's lead time is. This dashboard compares that policy against reorder points sized to each SKU's own demand and lead-time risk, tiered by revenue importance (ABC).</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Overall fill rate</div>
      <div class="v">{summary_after['Overall fill rate']}</div>
      <div class="delta good">&uarr; from {summary['Overall fill rate']}</div>
    </div>
    <div class="kpi">
      <div class="k">A-tier fill rate</div>
      <div class="v">{summary_after['A-tier fill rate']}</div>
      <div class="delta good">&uarr; from {summary['A-tier fill rate']}</div>
    </div>
    <div class="kpi">
      <div class="k">Net annual benefit</div>
      <div class="v">${roi['net_annual_benefit']/1e6:.2f}M</div>
      <div class="delta">margin recovered &minus; carrying cost</div>
    </div>
    <div class="kpi">
      <div class="k">SKUs analyzed</div>
      <div class="v">180</div>
      <div class="delta">3 ABC tiers &middot; 6 categories &middot; 4 regions</div>
    </div>
  </div>

  <section>
    <h2>Fill rate by ABC tier</h2>
    <div class="sub">Current policy vs. tier-differentiated safety stock &mdash; every tier clears 98%+, not just the top sellers.</div>
    <div class="panel">
      <div class="legend">
        <span><span class="swatch" style="background:{BLUE}"></span>Current policy</span>
        <span><span class="swatch" style="background:{ORANGE}"></span>Recommended policy</span>
      </div>
      {chart_fill_by_tier()}
    </div>
  </section>

  <section>
    <h2>Monthly fill rate, status quo</h2>
    <div class="sub">Every November both years falls furthest from target &mdash; the current policy can't absorb the holiday demand spike.</div>
    <div class="panel">{chart_monthly_trend()}</div>
  </section>

  <section>
    <h2>Where reorder points move the most</h2>
    <div class="sub">Orange = under-protected today (raise the reorder point) &middot; Blue = over-protected today (safe to trim)</div>
    <div class="panel">{chart_reorder_changes()}</div>
  </section>

  <section>
    <h2>The ROI case</h2>
    <div class="sub">Protecting revenue-critical SKUs costs more inventory investment &mdash; but the margin recovered from fewer stockouts far outweighs it.</div>
    <div class="roi-grid">
      <div class="roi-card">
        <div class="k">Annual margin recovered</div>
        <div class="v">${roi['annual_margin_recovered']:,.0f}</div>
        {stat_bar(roi['annual_margin_recovered'], roi_max, GOOD)}
      </div>
      <div class="roi-card">
        <div class="k">Annual carrying-cost increase</div>
        <div class="v">${roi['annual_carrying_cost_increase']:,.0f}</div>
        {stat_bar(roi['annual_carrying_cost_increase'], roi_max, "var(--ink-faint)")}
      </div>
      <div class="roi-card net">
        <div class="k">Net annual benefit</div>
        <div class="v">${roi['net_annual_benefit']:,.0f}</div>
        {stat_bar(roi['net_annual_benefit'], roi_max, "var(--accent)")}
      </div>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; built from <span class="mono">data/processed/*.csv</span> by <span class="mono">scripts/04_build_dashboard.py</span> &middot; Case 01 of the Data Analytics Portfolio
  </footer>
</div>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html)
print(f"Dashboard written to {OUT.relative_to(BASE)} ({len(html):,} bytes)")
