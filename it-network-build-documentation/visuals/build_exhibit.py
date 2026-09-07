"""Builds visuals/network-build-exhibit.html — a self-contained inline-SVG
exhibit matching the site's existing dashboard design system, built from
the real blast-radius analysis (see src/network_analysis.py)."""
import csv

with open("data/raw/blast_radius_summary.csv") as f:
    rows = list(csv.DictReader(f))

baseline = next(r for r in rows if r["segment"] == "FLAT_NETWORK_BASELINE")
segments = [r for r in rows if r["segment"] != "FLAT_NETWORK_BASELINE"]
segments.sort(key=lambda r: -int(r["blast_radius_after_segmentation"]))

BEFORE_COLOR = "#c0392b"
AFTER_COLOR = "#2a6f6f"


def blast_radius_chart(rows, baseline_val, width=640, left=170, right=624, row_h=56, top=10):
    n = len(rows)
    height = top + n * row_h + 10
    max_val = baseline_val
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" class="chart-svg">']
    svg.append(f'<line x1="{left}" x2="{left}" y1="0" y2="{height-14}" class="baseline"/>')
    for i, r in enumerate(rows):
        y = top + i * row_h
        segment = r["segment"]
        after = int(r["blast_radius_after_segmentation"])
        pct = float(r["blast_radius_reduction_pct"])
        bw_before = (baseline_val / max_val) * (right - left - 40)
        bw_after = (after / max_val) * (right - left - 40)
        svg.append(f'<rect x="{left}" y="{y}" width="{bw_before:.1f}" height="16" rx="3" fill="{BEFORE_COLOR}" opacity="0.35">'
                    f'<title>{segment} before (flat network): {baseline_val} reachable</title></rect>')
        svg.append(f'<text x="{left+bw_before+8:.1f}" y="{y+13}" class="bar-label-h" text-anchor="start" opacity="0.6">{baseline_val} before</text>')
        y2 = y + 20
        svg.append(f'<rect x="{left}" y="{y2}" width="{bw_after:.1f}" height="16" rx="3" fill="{AFTER_COLOR}">'
                    f'<title>{segment} after segmentation: {after} reachable ({pct:.1f}% reduction)</title></rect>')
        svg.append(f'<text x="{left+bw_after+8:.1f}" y="{y2+13}" class="bar-label-h" text-anchor="start">{after} after (-{pct:.0f}%)</text>')
        svg.append(f'<text x="{left-10}" y="{y+18}" class="axis-label sku-label" text-anchor="end">{segment}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


chart_svg = blast_radius_chart(segments, int(baseline["blast_radius_after_segmentation"]))

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Manufacturing &middot; Riverside Branch Network Build Exhibit</title>
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
.panel img{{max-width:100%; display:block; margin:0 auto;}}

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
    <h1>Building the Riverside branch network segmented from day one</h1>
    <p>A greenfield 78-device branch office defaults to one flat network unless someone deliberately designs otherwise. This build separates office, warehouse, VoIP, guest, and management traffic into 5 VLANs with a default-deny inter-VLAN firewall policy &mdash; before a single device is ever compromised.</p>
  </header>

  <div class="kpis">
    <div class="kpi">
      <div class="k">Devices at go-live</div>
      <div class="v">78</div>
      <div class="delta">across 5 segments</div>
    </div>
    <div class="kpi">
      <div class="k">Legacy/unpatched devices isolated</div>
      <div class="v">14</div>
      <div class="delta good">warehouse scanners &amp; printers, own VLAN</div>
    </div>
    <div class="kpi">
      <div class="k">Worst-case blast radius reduction</div>
      <div class="v">64.9%</div>
      <div class="delta good">77 &rarr; 27 devices (Office VLAN)</div>
    </div>
    <div class="kpi">
      <div class="k">Best-case blast radius reduction</div>
      <div class="v">93.5%</div>
      <div class="delta good">77 &rarr; 5 devices (Management VLAN)</div>
    </div>
  </div>

  <section>
    <h2>Network topology</h2>
    <div class="sub">One firewall, one L3 core switch, two L2 access switches &mdash; 5 VLANs, no VLAN spans a switch that doesn't need it.</div>
    <div class="panel"><img src="network-diagram.png" alt="Riverside branch network topology diagram"></div>
  </section>

  <section>
    <h2>Blast radius, before vs. after segmentation</h2>
    <div class="sub">Devices reachable from one compromised device. Before = every other device on a flat network (77). After = only the devices sharing that VLAN, since inter-VLAN traffic defaults to deny.</div>
    <div class="panel">{chart_svg}</div>
  </section>

  <section>
    <h2>What the firewall policy actually allows</h2>
    <div class="sub">16 numbered rules, evaluated top-to-bottom, default-deny. Every "pass" rule below names a specific host and/or port &mdash; there is no blanket VLAN-to-VLAN allow anywhere in the policy.</div>
    <div class="roi-grid">
      <div class="roi-card net">
        <div class="k">Guest &rarr; internal network</div>
        <div class="v">0 paths allowed</div>
        <div class="sub2">Guest can reach the internet (web/DNS only) and nothing else &mdash; no RFC1918 destination, ever</div>
      </div>
      <div class="roi-card">
        <div class="k">Warehouse &rarr; Office</div>
        <div class="v">1 host, 1 port</div>
        <div class="sub2">a single pinhole to the WMS integration server's API port &mdash; not "Warehouse can reach Office"</div>
      </div>
      <div class="roi-card">
        <div class="k">Anything &rarr; Management</div>
        <div class="v">1 source IP</div>
        <div class="sub2">only the designated IT jump host may reach switch/AP/firewall management interfaces, SSH/HTTPS only</div>
      </div>
    </div>
  </section>

  <footer>
    Data and configs are simulated (see README for methodology) &middot; built from <span class="mono">src/network_analysis.py</span> &middot; IT Support case, IT &amp; Cybersecurity track
  </footer>
</div>
</body>
</html>
"""

with open("visuals/network-build-exhibit.html", "w") as f:
    f.write(html)
print("Wrote visuals/network-build-exhibit.html")
