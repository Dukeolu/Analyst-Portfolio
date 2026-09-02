"""
Case 03 -- Step 4: build the dashboard.

Same approach as Cases 01-02: Power BI isn't installable here, so this is
a self-contained static HTML file, hand-built inline SVG, zero external
dependencies.
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
P = BASE / "data" / "processed"
OUT = BASE / "dashboard" / "index.html"

bridge = pd.read_csv(P / "margin_bridge.csv").iloc[0]
ranked = pd.read_csv(P / "variance_ranked.csv")
recovery = pd.read_csv(P / "recovery_scenario.csv").iloc[0]
monthly = pd.read_csv(P / "monthly_trend_worst_combos.csv")

BLUE, ORANGE = "#2a78d6", "#eb6834"
BLUE_D, ORANGE_D = "#3987e5", "#d95926"
RED, RED_D = "#e34948", "#e66767"
GOOD, GOOD_D = "#0ca30c", "#0ca30c"
INK, INK_D = "#0b0b0b", "#ffffff"
SEC, SEC_D = "#52514e", "#c3c2b7"
MUTED = "#898781"

categories = sorted(ranked["category"].unique())
regions = sorted(ranked["region"].unique())


def svg_open(w, h):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img" class="chart-svg">'


# ---------------------------------------------------------------- chart 1a: budget vs actual (own scale)
def chart_totals():
    w, h = 300, 300
    margin = dict(l=54, r=16, t=16, b=36)
    plot_w, plot_h = w - margin["l"] - margin["r"], h - margin["t"] - margin["b"]
    vmax = bridge["budget_profit"] * 1.08
    bar_w = 90
    gap = 36

    def y(v):
        return margin["t"] + plot_h * (1 - v / vmax)

    svg = [svg_open(w, h)]
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        val = frac * vmax
        yy = y(val)
        svg.append(f'<line x1="{margin["l"]}" x2="{w-margin["r"]}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/>')
        svg.append(f'<text x="{margin["l"]-8}" y="{yy+4:.1f}" class="axis-label" text-anchor="end">${val/1e6:.0f}M</text>')

    for i, (label, val, fill) in enumerate([("Budget", bridge["budget_profit"], "#8792A0"), ("Actual", bridge["actual_profit"], RED)]):
        cx = margin["l"] + gap + i * (bar_w + gap * 1.6) + bar_w / 2
        by = y(val)
        bh = y(0) - by
        svg.append(f'<rect x="{cx-bar_w/2:.1f}" y="{by:.1f}" width="{bar_w}" height="{bh:.1f}" rx="4" fill="{fill}"><title>{label} profit: ${val:,.0f}</title></rect>')
        svg.append(f'<text x="{cx:.1f}" y="{by-8:.1f}" class="bar-label" text-anchor="middle">${val/1e6:.2f}M</text>')
        svg.append(f'<text x="{cx:.1f}" y="{h-12}" class="axis-label" text-anchor="middle">{label}</text>')
    svg.append("</svg>")
    return "".join(svg)


# ---------------------------------------------------------------- chart 1b: the three effects, own scale
def chart_effects():
    steps = [("Volume / revenue effect", bridge["volume_effect"]), ("Discount effect", bridge["discount_effect"]), ("COGS effect", bridge["cogs_effect"])]
    w, h = 340, 300
    margin = dict(l=14, r=70, t=30, b=20)
    plot_w = w - margin["l"] - margin["r"]
    max_abs = max(abs(v) for _, v in steps) * 1.15
    row_h = 70
    cx = margin["l"] + plot_w * 0.32

    def bar_len(v):
        return abs(v) / max_abs * (plot_w - plot_w * 0.32 - 10)

    svg = [svg_open(w, h)]
    svg.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{margin["t"]-8}" y2="{h-10}" class="baseline"/>')
    for i, (label, val) in enumerate(steps):
        yy = margin["t"] + i * row_h + row_h / 2
        bl = bar_len(val)
        color = GOOD if val > 0 else RED
        bx = cx if val > 0 else cx - bl
        svg.append(f'<rect x="{bx:.1f}" y="{yy-11:.1f}" width="{max(bl,2):.1f}" height="22" rx="5" fill="{color}"><title>{label}: ${val:+,.0f}</title></rect>')
        svg.append(f'<text x="{margin["l"]}" y="{yy-16:.1f}" class="axis-label sku-label" text-anchor="start">{label}</text>')
        val_x = bx + bl + 8 if val > 0 else bx - 8
        anchor = "start" if val > 0 else "end"
        svg.append(f'<text x="{val_x:.1f}" y="{yy+4:.1f}" class="bar-label-h" text-anchor="{anchor}">${val:+,.0f}</text>')
    svg.append("</svg>")
    return "".join(svg)


# ---------------------------------------------------------------- chart 2: heatmap grid
def chart_heatmap():
    pivot = ranked.pivot(index="category", columns="region", values="variance").reindex(index=categories, columns=regions)
    vmax = pivot.abs().max().max()

    def color_for(v):
        t = min(1.0, abs(v) / vmax)
        if v >= 0:
            # interpolate white -> good green
            r = int(255 - t * (255 - 12)); g = int(255 - t * (255 - 163)); b = int(255 - t * (255 - 12))
        else:
            r = int(255 - t * (255 - 227)); g = int(255 - t * (255 - 73)); b = int(255 - t * (255 - 72))
        return f"rgb({r},{g},{b})"

    cell_w, cell_h = 140, 46
    label_w, label_h = 170, 30
    w = label_w + cell_w * len(regions) + 10
    h = label_h + cell_h * len(categories) + 10
    svg = [svg_open(w, h)]
    for j, reg in enumerate(regions):
        svg.append(f'<text x="{label_w + j*cell_w + cell_w/2:.1f}" y="20" class="axis-label" text-anchor="middle">{reg}</text>')
    for i, cat in enumerate(categories):
        yy = label_h + i * cell_h
        svg.append(f'<text x="{label_w-10}" y="{yy+cell_h/2+4:.1f}" class="axis-label sku-label" text-anchor="end">{cat}</text>')
        for j, reg in enumerate(regions):
            v = pivot.loc[cat, reg]
            xx = label_w + j * cell_w
            svg.append(f'<rect x="{xx+2}" y="{yy+2}" width="{cell_w-4}" height="{cell_h-4}" rx="5" fill="{color_for(v)}" stroke="var(--line)"><title>{cat} / {reg}: ${v:,.0f}</title></rect>')
            txt_color = "#ffffff" if abs(v) / vmax > 0.55 else "var(--ink)"
            svg.append(f'<text x="{xx+cell_w/2:.1f}" y="{yy+cell_h/2+4:.1f}" text-anchor="middle" style="fill:{txt_color}; font-family:\'IBM Plex Mono\',monospace; font-size:12px;">${v/1000:+.0f}K</text>')
    svg.append("</svg>")
    return "".join(svg)


# ---------------------------------------------------------------- chart 3: monthly trend, worst combo
def chart_worst_trend():
    worst = ranked.iloc[0]
    sub = monthly[(monthly.category == worst["category"]) & (monthly.region == worst["region"])].sort_values("month")
    w, h = 660, 260
    margin = dict(l=48, r=16, t=16, b=32)
    plot_w, plot_h = w - margin["l"] - margin["r"], h - margin["t"] - margin["b"]
    n = len(sub)
    ymin, ymax = -0.01, 0.09

    def x(i):
        return margin["l"] + plot_w * i / (n - 1)

    def y(v):
        return margin["t"] + plot_h * (1 - (v - ymin) / (ymax - ymin))

    svg = [svg_open(w, h)]
    for pct in (0, 2, 4, 6, 8):
        yy = y(pct / 100)
        svg.append(f'<line x1="{margin["l"]}" x2="{w-margin["r"]}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/>')
        svg.append(f'<text x="{margin["l"]-8}" y="{yy+4:.1f}" class="axis-label" text-anchor="end">+{pct}pt</text>')
    zero_y = y(0)
    svg.append(f'<line x1="{margin["l"]}" x2="{w-margin["r"]}" y1="{zero_y:.1f}" y2="{zero_y:.1f}" class="baseline"/>')

    for col, color, color_d, label in [("cogs_variance_pts", ORANGE, ORANGE_D, "COGS variance"), ("discount_variance_pts", BLUE, BLUE_D, "Discount variance")]:
        pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(sub[col]))
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" class="series-line"/>')
    for i, m in enumerate(sub["month"]):
        if i % 3 == 0:
            svg.append(f'<text x="{x(i):.1f}" y="{h-8}" class="axis-label" text-anchor="middle">{m}</text>')
    svg.append("</svg>")
    return "".join(svg)


worst = ranked.iloc[0]

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Case 03 &middot; Finance &amp; Budgeting Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F5F4; --paper-raised:#FBFCFB; --ink:{INK}; --ink-soft:{SEC}; --ink-faint:{MUTED}; --ink-faint-solid:#8792A0;
  --line:#D6DCDA; --line-strong:#B9C2C0; --accent:#4C5B8C; --accent-ink:#38446B; --accent-wash:#E1E4EF;
  --good:{GOOD};
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#12161C; --paper-raised:#181D25; --ink:{INK_D}; --ink-soft:{SEC_D}; --ink-faint:#6E7885;
    --line:#2A3038; --line-strong:#3A414B; --accent:#9CA9DB; --accent-ink:#C3CCEB; --accent-wash:#20263A;
    --good:{GOOD_D};
  }}
}}
:root[data-theme="dark"]{{
  --paper:#12161C; --paper-raised:#181D25; --ink:{INK_D}; --ink-soft:{SEC_D}; --ink-faint:#6E7885;
  --line:#2A3038; --line-strong:#3A414B; --accent:#9CA9DB; --accent-ink:#C3CCEB; --accent-wash:#20263A;
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
header p{{color:var(--ink-soft); font-size:14.5px; max-width:66ch; margin-top:10px; line-height:1.6;}}

.kpis{{display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:32px;}}
@media (max-width:820px){{.kpis{{grid-template-columns:1fr 1fr;}}}}
.kpi{{background:var(--paper-raised); border:1px solid var(--line); border-radius:10px; padding:18px 18px 16px;}}
.kpi .k{{font-family:"IBM Plex Mono",monospace; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--ink-faint);}}
.kpi .v{{font-family:"IBM Plex Mono",monospace; font-size:25px; margin-top:8px;}}
.kpi .delta{{font-size:12.5px; color:var(--ink-soft); margin-top:4px;}}

section{{margin-bottom:36px;}}
section h2{{font-size:17px; margin-bottom:4px;}}
section .sub{{color:var(--ink-faint); font-size:13px; margin-bottom:14px;}}
.panel{{background:var(--paper-raised); border:1px solid var(--line); border-radius:10px; padding:18px 18px 8px; overflow-x:auto;}}

.chart-svg .grid{{stroke:var(--line); stroke-width:1;}}
.chart-svg .baseline{{stroke:var(--line-strong); stroke-width:1;}}
.chart-svg .connector{{stroke:var(--line-strong); stroke-width:1; stroke-dasharray:3 3;}}
.chart-svg .axis-label{{fill:var(--ink-faint); font-size:11px; font-family:"IBM Plex Mono",monospace;}}
.chart-svg .sku-label{{fill:var(--ink-soft); font-family:"IBM Plex Sans",sans-serif;}}
.chart-svg .bar-label{{fill:var(--ink); font-size:11.5px; font-family:"IBM Plex Mono",monospace; font-weight:500;}}
.chart-svg .bar-label-h{{fill:var(--ink); font-size:12px; font-family:"IBM Plex Mono",monospace; font-weight:500;}}

.bridge-row{{display:grid; grid-template-columns:300px 1fr; gap:16px; align-items:stretch;}}
@media (max-width:700px){{.bridge-row{{grid-template-columns:1fr;}}}}

.legend{{display:flex; gap:18px; font-size:12.5px; color:var(--ink-soft); margin-bottom:10px; flex-wrap:wrap;}}
.legend span{{display:inline-flex; align-items:center; gap:6px;}}
.swatch{{width:10px; height:10px; border-radius:3px; display:inline-block;}}

.roi-grid{{display:grid; grid-template-columns:repeat(3,1fr); gap:16px;}}
@media (max-width:760px){{.roi-grid{{grid-template-columns:1fr;}}}}
.roi-card{{background:var(--paper-raised); border:1px solid var(--line); border-radius:10px; padding:18px;}}
.roi-card .k{{font-family:"IBM Plex Mono",monospace; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--ink-faint);}}
.roi-card .v{{font-family:"IBM Plex Mono",monospace; font-size:22px; margin:8px 0 2px;}}
.roi-card.net{{border-color:var(--accent); background:var(--accent-wash);}}

table.seg-table{{width:100%; border-collapse:collapse; font-size:13px;}}
table.seg-table th{{text-align:left; font-family:"IBM Plex Mono",monospace; font-size:10.5px; text-transform:uppercase; letter-spacing:.04em; color:var(--ink-faint); padding:8px 10px; border-bottom:1px solid var(--line-strong);}}
table.seg-table td{{padding:8px 10px; border-bottom:1px solid var(--line); color:var(--ink-soft);}}
table.seg-table td.num{{font-family:"IBM Plex Mono",monospace; color:var(--ink); text-align:right;}}

footer{{border-top:1px solid var(--line); padding-top:18px; font-size:12px; color:var(--ink-faint);}}
</style>
</head>
<body>
<div class="shell">
  <header>
    <div class="eyebrow">Case 03 &middot; Finance &amp; Budgeting</div>
    <h1>Finding where margin is quietly leaking</h1>
    <p>The business is profitable overall, but ${abs(bridge['budget_profit']-bridge['actual_profit']):,.0f} of profit came in below budget over the trailing 24 months. Region x category breakdown finds it isn't spread evenly &mdash; 4 of 24 combos account for {recovery['share_of_total_leak_addressed_pct']:.0f}% of the entire shortfall.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Actual profit (24mo)</div>
      <div class="v">${bridge['actual_profit']/1e6:.2f}M</div>
      <div class="delta">vs. ${bridge['budget_profit']/1e6:.2f}M budgeted</div>
    </div>
    <div class="kpi">
      <div class="k">Total variance</div>
      <div class="v">${bridge['actual_profit']-bridge['budget_profit']:,.0f}</div>
      <div class="delta">{(bridge['actual_profit']/bridge['budget_profit']-1):.1%} vs. plan</div>
    </div>
    <div class="kpi">
      <div class="k">Leak concentration</div>
      <div class="v">{recovery['share_of_total_leak_addressed_pct']:.0f}%</div>
      <div class="delta">of shortfall in just 4 of 24 combos</div>
    </div>
    <div class="kpi">
      <div class="k">Recoverable (annualized)</div>
      <div class="v">${recovery['profit_recovered_annualized']:,.0f}</div>
      <div class="delta">if those 4 combos hold budget rates</div>
    </div>
  </div>

  <section>
    <h2>Margin bridge: budget to actual</h2>
    <div class="sub">Volume was fine &mdash; the shortfall is almost entirely a discount and COGS story, not a demand problem. The three effects are shown on their own scale since they're two orders of magnitude smaller than total profit.</div>
    <div class="panel">
      <div class="bridge-row">
        {chart_totals()}
        {chart_effects()}
      </div>
    </div>
  </section>

  <section>
    <h2>Profit variance by region &times; category</h2>
    <div class="sub">Green = ahead of budget, red = behind. Two problems, cleanly localized: Electronics Accessories (West/Northeast) and Outdoor &amp; Sporting (South/Midwest).</div>
    <div class="panel">{chart_heatmap()}</div>
  </section>

  <section>
    <h2>The worst offender: {worst['category']} &middot; {worst['region']}</h2>
    <div class="sub">COGS variance ramps through the year &mdash; a cost problem that's still getting worse, not a one-month blip.</div>
    <div class="panel">
      <div class="legend">
        <span><span class="swatch" style="background:{ORANGE}"></span>COGS variance (pts above budget)</span>
        <span><span class="swatch" style="background:{BLUE}"></span>Discount variance (pts above budget)</span>
      </div>
      {chart_worst_trend()}
    </div>
  </section>

  <section>
    <h2>The recommendation</h2>
    <div class="sub">Hold the four worst combos to their budgeted discount% and COGS% &mdash; same volume, same effort, just back on plan.</div>
    <div class="roi-grid">
      <div class="roi-card">
        <div class="k">Actual profit, 24mo</div>
        <div class="v">${recovery['actual_profit_24mo']:,.0f}</div>
      </div>
      <div class="roi-card">
        <div class="k">Counterfactual profit, 24mo</div>
        <div class="v">${recovery['counterfactual_profit_24mo']:,.0f}</div>
      </div>
      <div class="roi-card net">
        <div class="k">Profit recovered (annualized)</div>
        <div class="v">${recovery['profit_recovered_annualized']:,.0f}</div>
      </div>
    </div>
  </section>

  <section>
    <h2>All 24 combos, ranked</h2>
    <div class="sub">Worst 8 by total variance, with cumulative share of the total leak.</div>
    <div class="panel">
      <table class="seg-table">
        <thead><tr><th>Category</th><th>Region</th><th>Variance $</th><th>Variance %</th><th>Cumulative % of leak</th></tr></thead>
        <tbody>
        {''.join(f"<tr><td>{r.category}</td><td>{r.region}</td><td class='num'>${r.variance:,.0f}</td><td class='num'>{r.variance_pct:+.1f}%</td><td class='num'>{r.cumulative_pct_of_total_leak:.0f}%</td></tr>" for r in ranked.head(8).itertuples())}
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; built from <span class="mono">data/processed/*.csv</span> by <span class="mono">scripts/04_build_dashboard.py</span> &middot; Case 03 of the Data Analytics Portfolio &middot; see also <span class="mono">excel/case03_margin_analysis.xlsx</span>
  </footer>
</div>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html)
print(f"Dashboard written to {OUT.relative_to(BASE)} ({len(html):,} bytes)")
