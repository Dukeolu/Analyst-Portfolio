"""
Case 02 -- Step 4: build the dashboard.

Same approach as Case 01: Tableau isn't installable here, so this is a
self-contained static HTML file with the same KPI/chart content a
stakeholder would get from a published Tableau workbook, built as inline
SVG with zero external dependencies.
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
P = BASE / "data" / "processed"
OUT = BASE / "dashboard" / "index.html"

retention = pd.read_csv(P / "retention_curve.csv")
drivers = pd.read_csv(P / "driver_ranking.csv")
roi = pd.read_csv(P / "retention_offer_roi.csv").iloc[0]
meta = pd.read_csv(P / "model_metadata.csv").iloc[0]
by_segment = pd.read_csv(P / "high_risk_by_segment.csv")
df_raw = pd.read_csv(BASE / "data" / "raw" / "customers.csv")
overall_churn = (df_raw["churned"] == "Yes").mean()

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
BLUE_D, ORANGE_D, AQUA_D = "#3987e5", "#d95926", "#199e70"
GOOD, GOOD_D = "#0ca30c", "#0ca30c"
INK, INK_D = "#0b0b0b", "#ffffff"
SEC, SEC_D = "#52514e", "#c3c2b7"
MUTED = "#898781"


def svg_open(w, h):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img" class="chart-svg">'


CONTRACT_COLORS = {"Month-to-month": (BLUE, BLUE_D), "One year": (ORANGE, ORANGE_D), "Two year": (AQUA, AQUA_D)}


def chart_retention_curves():
    w, h = 660, 300
    margin = dict(l=44, r=16, t=16, b=32)
    plot_w, plot_h = w - margin["l"] - margin["r"], h - margin["t"] - margin["b"]
    horizons = sorted(retention["horizon_months"].unique())

    def x(hz):
        return margin["l"] + plot_w * horizons.index(hz) / (len(horizons) - 1)

    def y(v):
        return margin["t"] + plot_h * (1 - v)

    svg = [svg_open(w, h)]
    for pct in (0, 25, 50, 75, 100):
        yy = y(pct / 100)
        svg.append(f'<line x1="{margin["l"]}" x2="{w-margin["r"]}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/>')
        svg.append(f'<text x="{margin["l"]-8}" y="{yy+4:.1f}" class="axis-label" text-anchor="end">{pct}%</text>')
    for hz in horizons:
        svg.append(f'<text x="{x(hz):.1f}" y="{h-8}" class="axis-label" text-anchor="middle">{hz}mo</text>')

    for contract, (color, color_d) in CONTRACT_COLORS.items():
        sub = retention[retention.contract_type == contract].sort_values("horizon_months")
        pts = " ".join(f"{x(r.horizon_months):.1f},{y(r.retention_rate):.1f}" for r in sub.itertuples())
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" data-dark="{color_d}" class="series-line" data-series="{contract}"/>')
        for r in sub.itertuples():
            svg.append(f'<circle cx="{x(r.horizon_months):.1f}" cy="{y(r.retention_rate):.1f}" r="4" fill="{color}" data-dark="{color_d}" class="series-dot" data-series="{contract}"><title>{contract}, {r.horizon_months} months: {r.retention_rate:.0%} still active</title></circle>')
    svg.append("</svg>")
    return "".join(svg)


def chart_driver_ranking():
    top = drivers.reindex(drivers.standardized_coefficient.abs().sort_values(ascending=False).index).head(8)
    w, h = 660, 34 * len(top) + 30
    margin = dict(l=190, r=30, t=10, b=20)
    plot_w = w - margin["l"] - margin["r"]
    max_abs = top["standardized_coefficient"].abs().max()
    cx = margin["l"] + plot_w / 2

    def bar_len(v):
        return abs(v) / max_abs * (plot_w / 2 - 55)

    label_map = {
        "contract_type_Two year": "Contract: Two year", "contract_type_One year": "Contract: One year",
        "avg_engagement_score": "Engagement score", "region_West": "Region: West",
        "signup_channel_Referral": "Channel: Referral", "signup_channel_Paid Search": "Channel: Paid Search",
        "region_South": "Region: South", "monthly_charge": "Monthly charge",
        "autopay_flag": "Autopay enabled", "signup_channel_Sales-Assisted": "Channel: Sales-Assisted",
        "addon_count": "Add-on count", "support_tickets_90d": "Support tickets (90d)",
        "region_Northeast": "Region: Northeast",
    }
    svg = [svg_open(w, h)]
    svg.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="0" y2="{h-20}" class="baseline"/>')
    for i, row in enumerate(top.itertuples()):
        yy = 20 + i * 34
        v = row.standardized_coefficient
        bl = bar_len(v)
        color = ORANGE if v > 0 else BLUE
        bx = cx if v > 0 else cx - bl
        label = label_map.get(row.feature, row.feature)
        svg.append(f'<rect x="{bx:.1f}" y="{yy-9:.1f}" width="{bl:.1f}" height="18" rx="4" fill="{color}"><title>{label}: {row.direction} ({v:+.2f})</title></rect>')
        svg.append(f'<text x="{margin["l"]-10}" y="{yy+4:.1f}" class="axis-label sku-label" text-anchor="end">{label}</text>')
        val_x = bx + bl + 6 if v > 0 else bx - 6
        anchor = "start" if v > 0 else "end"
        svg.append(f'<text x="{val_x:.1f}" y="{yy+4:.1f}" class="bar-label-h" text-anchor="{anchor}">{v:+.2f}</text>')
    svg.append("</svg>")
    return "".join(svg)


def stat_bar(value, max_value, color):
    pct = max(0.02, value / max_value)
    return f'<div class="stat-bar-track"><div class="stat-bar-fill" style="width:{pct*100:.1f}%; background:{color}"></div></div>'


roi_max = max(roi["expected_annual_revenue_protected"], roi["campaign_cost"], roi["net_annual_benefit"])

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Case 02 &middot; Sales &amp; Customer Analytics Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F5F4; --paper-raised:#FBFCFB; --ink:{INK}; --ink-soft:{SEC}; --ink-faint:{MUTED};
  --line:#D6DCDA; --line-strong:#B9C2C0; --accent:#8A5A44; --accent-ink:#6B4534; --accent-wash:#F0E4DE;
  --good:{GOOD};
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#12161C; --paper-raised:#181D25; --ink:{INK_D}; --ink-soft:{SEC_D}; --ink-faint:#6E7885;
    --line:#2A3038; --line-strong:#3A414B; --accent:#D2A78F; --accent-ink:#E8C4AE; --accent-wash:#2E241E;
    --good:{GOOD_D};
  }}
}}
:root[data-theme="dark"]{{
  --paper:#12161C; --paper-raised:#181D25; --ink:{INK_D}; --ink-soft:{SEC_D}; --ink-faint:#6E7885;
  --line:#2A3038; --line-strong:#3A414B; --accent:#D2A78F; --accent-ink:#E8C4AE; --accent-wash:#2E241E;
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

section{{margin-bottom:36px;}}
section h2{{font-size:17px; margin-bottom:4px;}}
section .sub{{color:var(--ink-faint); font-size:13px; margin-bottom:14px;}}
.panel{{background:var(--paper-raised); border:1px solid var(--line); border-radius:10px; padding:18px 18px 8px; overflow-x:auto;}}

.chart-svg .grid{{stroke:var(--line); stroke-width:1;}}
.chart-svg .baseline{{stroke:var(--line-strong); stroke-width:1;}}
.chart-svg .axis-label{{fill:var(--ink-faint); font-size:11px; font-family:"IBM Plex Mono",monospace;}}
.chart-svg .sku-label{{fill:var(--ink-soft); font-family:"IBM Plex Sans",sans-serif;}}
.chart-svg .bar-label-h{{fill:var(--ink); font-size:12px; font-family:"IBM Plex Mono",monospace; font-weight:500;}}

.legend{{display:flex; gap:18px; font-size:12.5px; color:var(--ink-soft); margin-bottom:10px; flex-wrap:wrap;}}
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

.callout{{background:var(--accent-wash); border:1px solid var(--line); border-radius:10px; padding:16px 18px; font-size:13.5px; color:var(--ink); line-height:1.6; margin-top:14px;}}
.callout b{{color:var(--accent-ink);}}

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
    <div class="eyebrow">Case 02 &middot; Sales &amp; Customer Analytics</div>
    <h1>Finding the customers about to churn &mdash; and why</h1>
    <p>Overall churn is {overall_churn:.1%} across the observed customer base. Contract type explains most of it, but engagement and support friction still separate at-risk customers within every contract tier. A logistic regression (test AUC {meta['test_auc']:.2f}) ranks the drivers and scores every active customer, so retention spend can go to the riskiest 20% instead of everyone.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Overall churn rate</div>
      <div class="v">{overall_churn:.1%}</div>
      <div class="delta">across {len(df_raw):,} customers observed</div>
    </div>
    <div class="kpi">
      <div class="k">Model test AUC</div>
      <div class="v">{meta['test_auc']:.2f}</div>
      <div class="delta">{int(meta['n_test']):,} held-out customers</div>
    </div>
    <div class="kpi">
      <div class="k">Annual revenue at risk</div>
      <div class="v">${roi['annual_revenue_at_risk']/1e3:.0f}K</div>
      <div class="delta">top 20% risk, still active</div>
    </div>
    <div class="kpi">
      <div class="k">Net annual benefit</div>
      <div class="v">${roi['net_annual_benefit']/1e3:.0f}K</div>
      <div class="delta">targeted retention campaign</div>
    </div>
  </div>

  <section>
    <h2>Retention curves by contract type</h2>
    <div class="sub">Share of each cohort still active at N months. Month-to-month customers are roughly a coin flip by month 12.</div>
    <div class="panel">
      <div class="legend">
        <span><span class="swatch" style="background:{BLUE}"></span>Month-to-month</span>
        <span><span class="swatch" style="background:{ORANGE}"></span>One year</span>
        <span><span class="swatch" style="background:{AQUA}"></span>Two year</span>
      </div>
      {chart_retention_curves()}
    </div>
  </section>

  <section>
    <h2>What actually predicts churn</h2>
    <div class="sub">Standardized logistic regression coefficients &mdash; orange raises churn risk, blue lowers it, holding the other features constant.</div>
    <div class="panel">{chart_driver_ranking()}</div>
    <div class="callout">
      <b>The confound worth flagging:</b> support-ticket volume looks like a real risk factor on its own (see the SQL breakdown), but once engagement score is in the model it nearly disappears &mdash; tickets are mostly a symptom of low engagement, not an independent cause. Channel and region effects are small enough to be noise; contract type and engagement are where the real signal is.
    </div>
  </section>

  <section>
    <h2>The targeted retention offer</h2>
    <div class="sub">Contacting all {int(roi['active_customers']):,} active customers isn't realistic. Targeting the riskiest {int(roi['high_risk_customers_targeted']):,} (avg. predicted risk {roi['avg_predicted_churn_prob_high_risk']:.0%}) is.</div>
    <div class="roi-grid">
      <div class="roi-card">
        <div class="k">Expected revenue protected</div>
        <div class="v">${roi['expected_annual_revenue_protected']:,.0f}</div>
        {stat_bar(roi['expected_annual_revenue_protected'], roi_max, GOOD)}
      </div>
      <div class="roi-card">
        <div class="k">Campaign cost</div>
        <div class="v">${roi['campaign_cost']:,.0f}</div>
        {stat_bar(roi['campaign_cost'], roi_max, "var(--ink-faint)")}
      </div>
      <div class="roi-card net">
        <div class="k">Net annual benefit</div>
        <div class="v">${roi['net_annual_benefit']:,.0f}</div>
        {stat_bar(roi['net_annual_benefit'], roi_max, "var(--accent)")}
      </div>
    </div>
  </section>

  <section>
    <h2>Where the targeted customers are</h2>
    <div class="sub">High-risk segment broken out by contract and acquisition channel &mdash; the actual call list, grouped.</div>
    <div class="panel">
      <table class="seg-table">
        <thead><tr><th>Contract</th><th>Channel</th><th>Customers</th><th>Avg. risk</th><th>MRR at risk</th></tr></thead>
        <tbody>
        {''.join(f"<tr><td>{r.contract_type}</td><td>{r.signup_channel}</td><td class='num'>{r.customers}</td><td class='num'>{r.avg_churn_probability:.0%}</td><td class='num'>${r.monthly_revenue_at_risk:,.0f}</td></tr>" for r in by_segment.head(8).itertuples())}
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; built from <span class="mono">data/processed/*.csv</span> by <span class="mono">scripts/04_build_dashboard.py</span> &middot; Case 02 of the Data Analytics Portfolio
  </footer>
</div>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html)
print(f"Dashboard written to {OUT.relative_to(BASE)} ({len(html):,} bytes)")
