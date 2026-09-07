"""Builds visuals/intrusion-detection-exhibit.html — a self-contained inline-SVG
dashboard matching the site's existing dashboard design system, built from
the real analysis numbers (see notebooks/intrusion_detection_analysis.ipynb)."""

RULES = [
    ("Current rule\n(burst only)", 83.3, 0),
    ("Fan-out v1\n(naive)", 33.3, 1),
    ("Fan-out v2\n(refined)", 33.3, 0),
    ("Both rules\ntogether", 100.0, 0),
]

TAKEOVER = [
    ("Recall\n(compromises caught)", 100.0),
    ("Precision\n(flags that were real)", 66.7),
]

GOOD = "#5C7A52"
BAD = "#c0392b"


def vbar_chart(rows, value_fmt, max_val, width=640, height=280, bar_w=100, gap=40, top=20, bottom=48, color=None):
    n = len(rows)
    left = 50
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{width-20}" y1="{height-bottom}" y2="{height-bottom}" class="baseline"/>')
    for i, (label, val) in enumerate(rows):
        x = left + i * (bar_w + gap) + 20
        bar_h = (val / max_val) * (height - top - bottom)
        y = (height - bottom) - bar_h
        c = color(val) if color else "#2a78d6"
        svg.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" rx="4" fill="{c}">'
                    f'<title>{label}: {value_fmt(val)}</title></rect>')
        svg.append(f'<text x="{x+bar_w/2}" y="{y-8:.1f}" class="bar-label-h" text-anchor="middle">{value_fmt(val)}</text>')
        for j, line in enumerate(label.split("\n")):
            svg.append(f'<text x="{x+bar_w/2}" y="{height-bottom+18+j*14}" class="axis-label sku-label" text-anchor="middle">{line}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def grouped_recall_fp_chart(rows, width=680, height=300):
    """rows: (label, recall_pct, fp_count)"""
    n = len(rows)
    left = 60
    right = width - 30
    top = 20
    bottom = 60
    bar_w = 46
    group_w = (right - left) / n
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{right}" y1="{height-bottom}" y2="{height-bottom}" class="baseline"/>')
    max_fp = 2
    for i, (label, recall, fp) in enumerate(rows):
        gx = left + i * group_w + group_w/2
        recall_h = (recall / 100) * (height - top - bottom)
        recall_x = gx - bar_w - 4
        recall_y = (height - bottom) - recall_h
        svg.append(f'<rect x="{recall_x:.1f}" y="{recall_y:.1f}" width="{bar_w}" height="{recall_h:.1f}" rx="4" fill="{GOOD}">'
                    f'<title>{label}: {recall:.1f}% recall</title></rect>')
        svg.append(f'<text x="{recall_x+bar_w/2:.1f}" y="{recall_y-8:.1f}" class="bar-label-h" text-anchor="middle">{recall:.0f}%</text>')

        fp_h = (fp / max_fp) * (height - top - bottom) if max_fp else 0
        fp_x = gx + 4
        fp_y = (height - bottom) - fp_h
        svg.append(f'<rect x="{fp_x:.1f}" y="{fp_y:.1f}" width="{bar_w}" height="{max(fp_h,2):.1f}" rx="4" fill="{BAD}">'
                    f'<title>{label}: {fp} false positives</title></rect>')
        svg.append(f'<text x="{fp_x+bar_w/2:.1f}" y="{fp_y-8:.1f}" class="bar-label-h" text-anchor="middle">{fp}</text>')

        for j, line in enumerate(label.split("\n")):
            svg.append(f'<text x="{gx:.1f}" y="{height-bottom+18+j*14}" class="axis-label sku-label" text-anchor="middle">{line}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


rules_svg = grouped_recall_fp_chart(RULES)
takeover_svg = vbar_chart(TAKEOVER, lambda v: f"{v:.1f}%", max_val=110, color=lambda v: GOOD if v >= 90 else "#eb6834")

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Manufacturing &middot; Intrusion Detection Exhibit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F5F4; --paper-raised:#FBFCFB; --ink:#0b0b0b; --ink-soft:#52514e; --ink-faint:#898781;
  --line:#D6DCDA; --line-strong:#B9C2C0; --accent:#7A3B3B; --accent-ink:#5C2A2A; --accent-wash:#F3E0E0;
  --good:#0ca30c;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#12161C; --paper-raised:#181D25; --ink:#ffffff; --ink-soft:#c3c2b7; --ink-faint:#6E7885;
    --line:#2A3038; --line-strong:#3A414B; --accent:#D98787; --accent-ink:#EFBABA; --accent-wash:#2C1A1A;
    --good:#0ca30c;
  }}
}}
:root[data-theme="dark"]{{
  --paper:#12161C; --paper-raised:#181D25; --ink:#ffffff; --ink-soft:#c3c2b7; --ink-faint:#6E7885;
  --line:#2A3038; --line-strong:#3A414B; --accent:#D98787; --accent-ink:#EFBABA; --accent-wash:#2C1A1A;
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
    <div class="eyebrow">Cybersecurity &middot; Meridian Manufacturing (simulated)</div>
    <h1>Does the current alert rule actually catch the attacks that matter?</h1>
    <p>The security team's rule flags 5+ failed VPN logins in 10 minutes. It reliably catches loud brute force &mdash; but a slow, distributed credential-stuffing attack can walk through it undetected, and whether it gets caught at all can come down to timing luck.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Current rule recall</div>
      <div class="v">83.3%</div>
      <div class="delta">5 of 6 attacker IPs &mdash; one caught by luck</div>
    </div>
    <div class="kpi">
      <div class="k">Naive fan-out false positive</div>
      <div class="v">Office NAT IP</div>
      <div class="delta bad">would alert on ~120 employees daily</div>
    </div>
    <div class="kpi">
      <div class="k">Refined rules, combined</div>
      <div class="v">100% recall</div>
      <div class="delta good">0 false positives</div>
    </div>
    <div class="kpi">
      <div class="k">Account compromise recall</div>
      <div class="v">100%</div>
      <div class="delta">all 4 confirmed compromises flagged</div>
    </div>
  </div>

  <section>
    <h2>Detection recall vs. false positives, by rule</h2>
    <div class="sub">Recall = % of the 6 known attacker IPs caught. False positives = legitimate sources incorrectly flagged.</div>
    <div class="panel">
      <div class="legend">
        <span><span class="swatch" style="background:{GOOD}"></span>Recall (%)</span>
        <span><span class="swatch" style="background:{BAD}"></span>False positives (count)</span>
      </div>
      {rules_svg}
    </div>
  </section>

  <section>
    <h2>Account-takeover rule: perfect recall, imperfect precision</h2>
    <div class="sub">Flags a successful login within 24h of 3+ recent failed attempts on the same account.</div>
    <div class="panel">{takeover_svg}</div>
  </section>

  <section>
    <h2>What the analysis recommends</h2>
    <div class="roi-grid">
      <div class="roi-card net">
        <div class="k">Run both IP-level rules together</div>
        <div class="v">100% / 0 FP</div>
        <div class="sub2">current burst rule + refined failed-only fan-out rule</div>
      </div>
      <div class="roi-card">
        <div class="k">Add the account-takeover rule</div>
        <div class="v">catches all 4</div>
        <div class="sub2">confirmed compromises, plus 2 near-miss accounts worth a reset</div>
      </div>
      <div class="roi-card">
        <div class="k">Firewall logs corroborate</div>
        <div class="v">6 of 6</div>
        <div class="sub2">every attacker IP also shows port-scan activity &mdash; 0 false positives</div>
      </div>
    </div>
  </section>

  <footer>
    Data is simulated (see README for methodology) &middot; built from <span class="mono">notebooks/intrusion_detection_analysis.ipynb</span> &middot; Cybersecurity case, IT &amp; Cybersecurity track
  </footer>
</div>
</body>
</html>
"""

with open("intrusion-detection-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/intrusion-detection-exhibit.html")
