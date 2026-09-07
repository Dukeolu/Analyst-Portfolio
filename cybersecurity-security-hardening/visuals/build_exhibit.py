"""Builds visuals/hardening-exhibit.html — matches the site's dashboard
design system, built from the real hardening analysis numbers."""
import csv

with open("data/raw/hardening_summary.csv") as f:
    summary = {row["metric"]: row["value"] for row in csv.DictReader(f)}

with open("data/raw/attack_surface_metrics.csv") as f:
    surface = list(csv.DictReader(f))

with open("data/raw/cis_hardening_checklist.csv") as f:
    controls = list(csv.DictReader(f))

from collections import defaultdict
by_category = defaultdict(lambda: [0, 0, 0])
for c in controls:
    cat = c["category"]
    by_category[cat][0] += 1
    by_category[cat][1] += 1 if c["baseline_pass"] == "True" else 0
    by_category[cat][2] += 1 if c["remediated_pass"] == "True" else 0

BEFORE_COLOR = "#c0392b"
AFTER_COLOR = "#8b2f2f"
AFTER_GOOD = "#2a6f6f"


def category_compliance_chart(width=640, left=190, right=624, row_h=44, top=10):
    cats = list(by_category.items())
    n = len(cats)
    height = top + n * row_h + 10
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    max_val = max(tot for tot, _, _ in by_category.values())
    for i, (cat, (tot, base, rem)) in enumerate(cats):
        y = top + i * row_h
        bw_base = (base / max_val) * (right - left - 60)
        bw_rem = (rem / max_val) * (right - left - 60)
        svg.append(f'<rect x="{left}" y="{y}" width="{bw_base:.1f}" height="15" rx="3" fill="{BEFORE_COLOR}" opacity="0.55">'
                    f'<title>{cat} before: {base}/{tot}</title></rect>')
        svg.append(f'<text x="{left+bw_base+8:.1f}" y="{y+12}" class="bar-label-h" text-anchor="start" opacity="0.7">{base}/{tot} before</text>')
        y2 = y + 19
        svg.append(f'<rect x="{left}" y="{y2}" width="{bw_rem:.1f}" height="15" rx="3" fill="{AFTER_GOOD}">'
                    f'<title>{cat} after: {rem}/{tot}</title></rect>')
        svg.append(f'<text x="{left+bw_rem+8:.1f}" y="{y2+12}" class="bar-label-h" text-anchor="start">{rem}/{tot} after</text>')
        svg.append(f'<text x="{left-10}" y="{y+18}" class="axis-label sku-label" text-anchor="end">{cat}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def surface_chart(width=640, left=250, right=624, row_h=40, top=10):
    n = len(surface)
    height = top + n * row_h + 10
    max_val = max(int(r["baseline_count"]) for r in surface)
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    for i, r in enumerate(surface):
        y = top + i * row_h
        before = int(r["baseline_count"])
        after = int(r["remediated_count"])
        bw_before = (before / max_val) * (right - left - 40)
        bw_after = (after / max_val) * (right - left - 40) if max_val else 0
        svg.append(f'<rect x="{left}" y="{y}" width="{bw_before:.1f}" height="14" rx="3" fill="{BEFORE_COLOR}" opacity="0.55">'
                    f'<title>{r["metric"]} before: {before}</title></rect>')
        svg.append(f'<text x="{left+bw_before+8:.1f}" y="{y+11}" class="bar-label-h" text-anchor="start" opacity="0.7">{before} before</text>')
        y2 = y + 18
        svg.append(f'<rect x="{left}" y="{y2}" width="{max(bw_after,2):.1f}" height="14" rx="3" fill="{AFTER_GOOD}">'
                    f'<title>{r["metric"]} after: {after}</title></rect>')
        svg.append(f'<text x="{left+max(bw_after,2)+8:.1f}" y="{y2+11}" class="bar-label-h" text-anchor="start">{after} after</text>')
        svg.append(f'<text x="{left-10}" y="{y+16}" class="axis-label sku-label" text-anchor="end">{r["metric"]}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


compliance_svg = category_compliance_chart()
surface_svg = surface_chart()

baseline_pct = float(summary["baseline_pass_pct"])
remediated_pct = float(summary["remediated_pass_pct"])
avg_reduction = float(summary["avg_attack_surface_reduction_pct"])
exceptions = int(summary["risk_accepted_exceptions"])

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Manufacturing &middot; Security Hardening Exhibit</title>
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

footer{{border-top:1px solid var(--line); padding-top:18px; font-size:12px; color:var(--ink-faint);}}
</style>
</head>
<body>
<div class="shell">
  <header>
    <div class="eyebrow">Cybersecurity &middot; Meridian Manufacturing (simulated)</div>
    <h1>Hardening the ERP/WMS integration server past its one patched CVE</h1>
    <p>Patching Log4Shell (see the Vulnerability Assessment case) fixes the one vulnerability the scan found. It doesn't fix the other 24 baseline hardening gaps on the same host &mdash; permissive SSH, no host firewall, no audit logging, weak file permissions. This is that second pass.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Baseline compliance</div>
      <div class="v">{baseline_pct:.0f}%</div>
      <div class="delta bad">5 of 25 controls passing</div>
    </div>
    <div class="kpi">
      <div class="k">Post-remediation compliance</div>
      <div class="v">{remediated_pct:.0f}%</div>
      <div class="delta good">24 of 25 controls passing</div>
    </div>
    <div class="kpi">
      <div class="k">Avg. attack-surface reduction</div>
      <div class="v">{avg_reduction:.1f}%</div>
      <div class="delta good">across 6 concrete metrics</div>
    </div>
    <div class="kpi">
      <div class="k">Risk-accepted exceptions</div>
      <div class="v">{exceptions}</div>
      <div class="delta">legacy TLS, disclosed &amp; time-boxed</div>
    </div>
  </div>

  <section>
    <h2>Compliance by control category</h2>
    <div class="sub">Every category started under 30% and ended fully or nearly compliant &mdash; Access &amp; SSH went from 0/6 to 6/6.</div>
    <div class="panel">{compliance_svg}</div>
  </section>

  <section>
    <h2>Attack surface, before vs. after</h2>
    <div class="sub">Concrete counts, not abstract scores &mdash; the kind of numbers that show up if someone actually enumerates the host.</div>
    <div class="panel">{surface_svg}</div>
  </section>

  <section>
    <h2>The one honest exception</h2>
    <div class="sub">Not every control gets remediated to 100% &mdash; and pretending otherwise would be the less credible answer.</div>
    <div class="roi-grid">
      <div class="roi-card net">
        <div class="k">Control 6.3</div>
        <div class="v">Risk accepted</div>
        <div class="sub2">Legacy TLS 1.0/1.1 stays enabled on the integration API for one EDI partner's legacy client</div>
      </div>
      <div class="roi-card">
        <div class="k">Why not just force it</div>
        <div class="v">Business dependency</div>
        <div class="sub2">forcing TLS 1.2+ today would break a live trading-partner integration with no fallback</div>
      </div>
      <div class="roi-card">
        <div class="k">The actual plan</div>
        <div class="v">Time-boxed exception</div>
        <div class="sub2">tracked, disclosed, partner migration scheduled next quarter &mdash; not silently ignored</div>
      </div>
    </div>
  </section>

  <footer>
    Data and configs are simulated (see README for methodology) &middot; built from <span class="mono">src/hardening_analysis.py</span> &middot; Cybersecurity case, IT &amp; Cybersecurity track
  </footer>
</div>
</body>
</html>
"""

with open("visuals/hardening-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/hardening-exhibit.html")
