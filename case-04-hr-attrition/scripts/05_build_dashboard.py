"""
Case 04 -- Step 5: build the dashboard.

Same approach as Cases 01-03: Tableau isn't installable here, so this is
a self-contained static HTML file, hand-built inline SVG, zero external
dependencies.
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
P = BASE / "data" / "processed"
OUT = BASE / "dashboard" / "index.html"

emp = pd.read_csv(RAW / "employees.csv")
funnel = pd.read_csv(RAW / "recruiting_funnel.csv")
drivers = pd.read_csv(P / "driver_ranking.csv")
meta = pd.read_csv(P / "model_metadata.csv").iloc[0]
early_by_channel = pd.read_csv(P / "early_attrition_by_channel.csv")
dept_risk = pd.read_csv(P / "department_risk_ranking.csv")
reco = pd.read_csv(P / "recommendation_summary.csv").iloc[0]

overall_attrition = (emp["terminated_voluntary"] == "Yes").mean()

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
BLUE_D, ORANGE_D = "#3987e5", "#d95926"
GOOD, GOOD_D = "#0ca30c", "#0ca30c"
RED = "#e34948"
INK, INK_D = "#0b0b0b", "#ffffff"
SEC, SEC_D = "#52514e", "#c3c2b7"
MUTED = "#898781"


def svg_open(w, h):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img" class="chart-svg">'


# ---------------------------------------------------------------- chart 1: funnel comparison
def chart_funnel():
    stages = ["applied", "screened", "interviewed", "offered", "hired"]
    stage_labels = ["Applied", "Screened", "Interviewed", "Offered", "Hired"]
    wo_jb = funnel[(funnel.department == "Warehouse & Ops") & (funnel.channel == "Job Board")][stages].sum()
    jb_all = funnel[funnel.channel == "Job Board"][stages].sum()
    wo_pct = (wo_jb / wo_jb["applied"] * 100)
    jb_pct = (jb_all / jb_all["applied"] * 100)

    w, h = 660, 300
    margin = dict(l=44, r=16, t=16, b=32)
    plot_w, plot_h = w - margin["l"] - margin["r"], h - margin["t"] - margin["b"]
    n = len(stages)

    def x(i):
        return margin["l"] + plot_w * i / (n - 1)

    def y(v):
        return margin["t"] + plot_h * (1 - v / 100)

    svg = [svg_open(w, h)]
    for pct in (0, 25, 50, 75, 100):
        yy = y(pct)
        svg.append(f'<line x1="{margin["l"]}" x2="{w-margin["r"]}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/>')
        svg.append(f'<text x="{margin["l"]-8}" y="{yy+4:.1f}" class="axis-label" text-anchor="end">{pct}%</text>')
    for i, lbl in enumerate(stage_labels):
        svg.append(f'<text x="{x(i):.1f}" y="{h-8}" class="axis-label" text-anchor="middle">{lbl}</text>')

    for series, color in [(jb_pct, BLUE), (wo_pct, ORANGE)]:
        pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(series))
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" class="series-line"/>')
        for i, v in enumerate(series):
            svg.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="4" fill="{color}"><title>{stage_labels[i]}: {v:.1f}% of applicants remaining</title></circle>')
    svg.append("</svg>")
    return "".join(svg)


# ---------------------------------------------------------------- chart 2: early attrition by channel
def chart_early_attrition():
    d = early_by_channel.sort_values("early_attrition_rate", ascending=False)
    w, h = 660, 260
    margin = dict(l=150, r=50, t=10, b=20)
    plot_w = w - margin["l"] - margin["r"]
    max_v = d["early_attrition_rate"].max() * 1.15
    row_h = 40

    svg = [svg_open(w, h)]
    for i, row in enumerate(d.itertuples()):
        yy = 16 + i * row_h + row_h / 2
        bl = row.early_attrition_rate / max_v * plot_w
        color = RED if row.channel == "Job Board" else (GOOD if row.channel == "Employee Referral" else "#8792A0")
        svg.append(f'<rect x="{margin["l"]}" y="{yy-11:.1f}" width="{bl:.1f}" height="22" rx="5" fill="{color}"><title>{row.channel}: {row.early_attrition_rate:.1%} early attrition ({int(row.early_departures)} of {int(row.hires)} hires)</title></rect>')
        svg.append(f'<text x="{margin["l"]-10}" y="{yy+4:.1f}" class="axis-label sku-label" text-anchor="end">{row.channel}</text>')
        svg.append(f'<text x="{margin["l"]+bl+8:.1f}" y="{yy+4:.1f}" class="bar-label-h" text-anchor="start">{row.early_attrition_rate:.1%}</text>')
    svg.append("</svg>")
    return "".join(svg)


# ---------------------------------------------------------------- chart 3: driver ranking
def chart_driver_ranking():
    top = drivers.reindex(drivers.standardized_coefficient.abs().sort_values(ascending=False).index).head(8)
    w, h = 660, 34 * len(top) + 30
    margin = dict(l=195, r=55, t=10, b=20)
    plot_w = w - margin["l"] - margin["r"]
    max_abs = top["standardized_coefficient"].abs().max()
    cx = margin["l"] + plot_w / 2

    def bar_len(v):
        return abs(v) / max_abs * (plot_w / 2 - 55)

    label_map = {
        "department_Marketing": "Dept: Marketing", "channel_Employee Referral": "Channel: Referral",
        "department_Engineering": "Dept: Engineering", "channel_Job Board": "Channel: Job Board",
        "department_Warehouse & Ops": "Dept: Warehouse & Ops", "department_Finance & Accounting": "Dept: Finance",
        "channel_Internal Transfer": "Channel: Internal Transfer", "avg_engagement_score": "Engagement score",
        "comp_ratio": "Comp-to-market ratio", "manager_span": "Manager span", "overtime_hours_monthly": "Overtime hours",
        "level_Manager": "Level: Manager", "level_Mid": "Level: Mid", "level_Senior": "Level: Senior",
        "channel_Campus": "Channel: Campus", "department_Sales": "Dept: Sales",
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
        svg.append(f'<rect x="{bx:.1f}" y="{yy-9:.1f}" width="{max(bl,2):.1f}" height="18" rx="4" fill="{color}"><title>{label}: {row.direction} ({v:+.2f})</title></rect>')
        svg.append(f'<text x="{margin["l"]-10}" y="{yy+4:.1f}" class="axis-label sku-label" text-anchor="end">{label}</text>')
        val_x = bx + bl + 6 if v > 0 else bx - 6
        anchor = "start" if v > 0 else "end"
        svg.append(f'<text x="{val_x:.1f}" y="{yy+4:.1f}" class="bar-label-h" text-anchor="{anchor}">{v:+.2f}</text>')
    svg.append("</svg>")
    return "".join(svg)


html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Case 04 &middot; HR &amp; People Operations Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F5F4; --paper-raised:#FBFCFB; --ink:{INK}; --ink-soft:{SEC}; --ink-faint:{MUTED};
  --line:#D6DCDA; --line-strong:#B9C2C0; --accent:#5C7A52; --accent-ink:#44603B; --accent-wash:#E4EBE1;
  --good:{GOOD};
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#12161C; --paper-raised:#181D25; --ink:{INK_D}; --ink-soft:{SEC_D}; --ink-faint:#6E7885;
    --line:#2A3038; --line-strong:#3A414B; --accent:#A2C295; --accent-ink:#C3DDB9; --accent-wash:#212B1E;
    --good:{GOOD_D};
  }}
}}
:root[data-theme="dark"]{{
  --paper:#12161C; --paper-raised:#181D25; --ink:{INK_D}; --ink-soft:{SEC_D}; --ink-faint:#6E7885;
  --line:#2A3038; --line-strong:#3A414B; --accent:#A2C295; --accent-ink:#C3DDB9; --accent-wash:#212B1E;
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
.roi-card .v{{font-family:"IBM Plex Mono",monospace; font-size:22px; margin:8px 0 2px;}}
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
    <div class="eyebrow">Case 04 &middot; HR &amp; People Operations</div>
    <h1>Where the hiring funnel &mdash; and headcount &mdash; leaks</h1>
    <p>Overall voluntary attrition is {overall_attrition:.1%}. It traces back to the same root cause as a recruiting-funnel bottleneck: Job Board hires cost the least to source but leave at more than 3x the rate of Employee Referral hires in their first 90 days &mdash; and Warehouse &amp; Ops' Job Board pipeline has its own screening backlog on top of that.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Overall attrition rate</div>
      <div class="v">{overall_attrition:.1%}</div>
      <div class="delta">across {len(emp):,} hires observed</div>
    </div>
    <div class="kpi">
      <div class="k">Job Board early attrition</div>
      <div class="v">{reco['job_board_early_attrition_rate']:.1%}</div>
      <div class="delta">vs. {reco['referral_early_attrition_rate']:.1%} for Referral</div>
    </div>
    <div class="kpi">
      <div class="k">Warehouse &amp; Ops x Job Board</div>
      <div class="v">{reco['wo_jobboard_interview_rate']:.0%}</div>
      <div class="delta">screen&rarr;interview vs {reco['jobboard_overall_interview_rate']:.0%} network-wide</div>
    </div>
    <div class="kpi">
      <div class="k">Annual savings available</div>
      <div class="v">${reco['annual_savings_channel_mix']:,.0f}</div>
      <div class="delta">from sourcing-mix shift alone</div>
    </div>
  </div>

  <section>
    <h2>The funnel bottleneck</h2>
    <div class="sub">Share of applicants remaining at each stage. Screening rates match &mdash; the gap opens specifically at screen&rarr;interview.</div>
    <div class="panel">
      <div class="legend">
        <span><span class="swatch" style="background:{BLUE}"></span>Job Board, all departments</span>
        <span><span class="swatch" style="background:{ORANGE}"></span>Job Board, Warehouse &amp; Ops only</span>
      </div>
      {chart_funnel()}
    </div>
  </section>

  <section>
    <h2>Early (&le;3 month) attrition by hiring channel</h2>
    <div class="sub">Job Board hires leave in their first 90 days at more than 3x the rate of Employee Referral hires.</div>
    <div class="panel">{chart_early_attrition()}</div>
  </section>

  <section>
    <h2>What actually predicts attrition</h2>
    <div class="sub">Standardized logistic regression coefficients (test AUC {meta['test_auc']:.2f}) &mdash; tenure itself is excluded as a feature since it's mechanically tied to the outcome. Orange raises risk, blue lowers it, holding the other features constant.</div>
    <div class="panel">{chart_driver_ranking()}</div>
    <div class="callout">
      <b>Read the AUC honestly:</b> 0.59 is modest, not impressive &mdash; and that's expected once tenure (the dominant, but circular, signal) is removed. What's left corroborates the SQL and Excel findings independently: channel and department carry real signal; manager span, despite being built into the simulation as a mild risk factor, doesn't come through reliably in this sample size and should be read as noise here, not a finding.
    </div>
  </section>

  <section>
    <h2>The recommendation</h2>
    <div class="sub">Two fixes, both traced to the same channel: shift sourcing mix away from Job Board where better alternatives exist, and clear the Warehouse &amp; Ops screening backlog.</div>
    <div class="roi-grid">
      <div class="roi-card">
        <div class="k">Departures avoided (24mo)</div>
        <div class="v">{reco['departures_avoided_24mo']:.0f}</div>
      </div>
      <div class="roi-card">
        <div class="k">Missed interviews/yr (WH&amp;Ops backlog)</div>
        <div class="v">{reco['annual_missed_interviews_wo_bottleneck']:.0f}</div>
      </div>
      <div class="roi-card net">
        <div class="k">Net annual savings</div>
        <div class="v">${reco['annual_savings_channel_mix']:,.0f}</div>
      </div>
    </div>
  </section>

  <section>
    <h2>Attrition rate by department</h2>
    <div class="sub">Warehouse &amp; Ops and Marketing run highest; Customer Support lowest. Warehouse &amp; Ops' elevated rate lines up with above-average overtime load and its funnel bottleneck &mdash; Marketing's does not have an obvious structural driver in this data and would need more digging.</div>
    <div class="panel">
      <table class="seg-table">
        <thead><tr><th>Department</th><th>Employees</th><th>Attrition rate</th><th>Avg. overtime hrs/mo</th><th>Avg. manager span</th></tr></thead>
        <tbody>
        {''.join(f"<tr><td>{r.department}</td><td class='num'>{r.employees}</td><td class='num'>{r.term_rate_pct:.1f}%</td><td class='num'>{r.avg_overtime_hours:.1f}</td><td class='num'>{r.avg_manager_span:.1f}</td></tr>" for r in dept_risk.itertuples())}
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; built from <span class="mono">data/processed/*.csv</span> by <span class="mono">scripts/05_build_dashboard.py</span> &middot; Case 04 of the Data Analytics Portfolio &middot; see also <span class="mono">excel/case04_hr_analysis.xlsx</span>
  </footer>
</div>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html)
print(f"Dashboard written to {OUT.relative_to(BASE)} ({len(html):,} bytes)")
