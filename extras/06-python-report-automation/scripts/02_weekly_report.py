"""
Extra 06 -- Step 2: the actual "automation" -- pull, clean, and export.

In a real deployment this would be triggered by a Monday-morning cron job
against a live source system; here it reads the simulated raw export,
cleans it the same way every time (so it's safe to re-run), computes the
past week's KPIs against the week before, and renders a single self-
contained HTML report -- the kind of thing that gets emailed out, not an
interactive dashboard someone has to go open.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
REPORT = BASE / "report"
PROCESSED.mkdir(parents=True, exist_ok=True)
REPORT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- 1. pull + clean
def load_and_clean(path):
    df = pd.read_csv(path, dtype=str)
    before = len(df)

    # dedupe exact duplicate rows -- an upstream logging bug re-sends some rows
    df = df.drop_duplicates()
    deduped = before - len(df)

    # normalize status casing/whitespace to a fixed vocabulary
    df["status"] = df["status"].str.strip().str.title()
    df["status"] = df["status"].replace({"Canceled": "Cancelled"})

    # flag and drop rows missing a required field rather than silently guessing
    missing_warehouse = (df["warehouse"].isna() | (df["warehouse"].str.strip() == "")).sum()
    df = df[df["warehouse"].notna() & (df["warehouse"].str.strip() != "")]

    # flag and drop nonsensical unit counts
    df["units"] = pd.to_numeric(df["units"], errors="coerce")
    bad_units = (df["units"] < 0).sum()
    df = df[df["units"] >= 0]

    # dates arrive in two different formats from two different upstream systems
    def parse_mixed_date(s):
        if pd.isna(s) or s == "":
            return pd.NaT
        return pd.to_datetime(s, format="%Y-%m-%d", errors="coerce") if re.match(r"^\d{4}-", str(s)) \
            else pd.to_datetime(s, format="%m/%d/%Y", errors="coerce")

    for col in ["order_date", "promised_ship_date", "actual_ship_date"]:
        df[col] = df[col].apply(parse_mixed_date)

    df["days_late"] = (df["actual_ship_date"] - df["promised_ship_date"]).dt.days

    cleaning_log = {
        "rows_in": before,
        "duplicate_rows_removed": int(deduped),
        "missing_warehouse_removed": int(missing_warehouse),
        "negative_units_removed": int(bad_units),
        "rows_out": len(df),
    }
    return df, cleaning_log


# ---------------------------------------------------------------- 2. weekly KPIs
def week_window(df, week_end):
    week_start = week_end - pd.Timedelta(days=6)
    return df[(df["order_date"] >= week_start) & (df["order_date"] <= week_end)]


def kpis_for_week(wk):
    # "Shipped" and "Delayed" are status labels the source system assigns at
    # log time; what actually matters for on-time rate is whether an order
    # has a completed ship date yet, and whether that date beat the promise
    # -- a "Delayed"-labeled order that did ship is still a completed,
    # just-late shipment, not an open item.
    total = len(wk)
    delayed_label = wk[wk["status"] == "Delayed"]
    cancelled = wk[wk["status"] == "Cancelled"]
    completed = wk[wk["actual_ship_date"].notna()]
    on_time = completed[completed["days_late"] <= 0]
    still_open = wk[(wk["status"] == "Delayed") & wk["actual_ship_date"].isna()]
    return {
        "total_orders": total,
        "shipped": len(completed),
        "delayed": len(delayed_label),
        "cancelled": len(cancelled),
        "on_time_rate": (len(on_time) / len(completed)) if len(completed) else np.nan,
        "backlog_open": len(still_open),
    }


def by_warehouse(wk):
    def rate(g):
        completed = g[g["actual_ship_date"].notna()]
        on_time = completed[completed["days_late"] <= 0]
        return pd.Series({
            "orders": len(g),
            "on_time_rate": (len(on_time) / len(completed)) if len(completed) else np.nan,
        })
    return wk.groupby("warehouse").apply(rate, include_groups=False).reset_index()


# ---------------------------------------------------------------- 3. render report
def bar_svg(rows, value_col, label_col, w=560, row_h=34, fmt="{:.0%}", flag_below=None):
    h = row_h * len(rows) + 20
    margin_l, margin_r = 150, 60
    plot_w = w - margin_l - margin_r
    max_v = max(0.01, rows[value_col].max()) * 1.1
    svg = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" class="chart-svg">']
    for i, r in enumerate(rows.itertuples()):
        y = 14 + i * row_h + row_h / 2
        val = getattr(r, value_col)
        bl = 0 if pd.isna(val) else (val / max_v) * plot_w
        flagged = flag_below is not None and pd.notna(val) and val < flag_below
        color = "var(--red)" if flagged else "var(--accent)"
        svg.append(f'<rect x="{margin_l}" y="{y-10:.1f}" width="{bl:.1f}" height="20" rx="4" fill="{color}"/>')
        svg.append(f'<text x="{margin_l-10}" y="{y+4:.1f}" text-anchor="end" class="lbl">{getattr(r, label_col)}</text>')
        val_txt = "—" if pd.isna(val) else fmt.format(val)
        svg.append(f'<text x="{margin_l+bl+8:.1f}" y="{y+4:.1f}" class="val">{val_txt}</text>')
    svg.append("</svg>")
    return "".join(svg)


def render_report(week_end, this_wk_kpi, prev_wk_kpi, this_wh, prev_wh, cleaning_log):
    def delta(cur, prev, pct=True, higher_is_good=None):
        if prev in (0, None) or pd.isna(prev):
            return ""
        d = cur - prev
        arrow = "▲" if d > 0 else ("▼" if d < 0 else "—")
        if higher_is_good is None or d == 0:
            cls = "flat"  # neutral metric (e.g. order volume) -- don't imply good/bad
        else:
            is_good = (d > 0) == higher_is_good
            cls = "up" if is_good else "down"
        val = f"{d:+.1%}" if pct else f"{d:+.0f}"
        return f'<span class="delta {cls}">{arrow} {val} vs prior week</span>'

    wh_merged = this_wh.merge(prev_wh, on="warehouse", how="left", suffixes=("", "_prev"))
    wh_merged = wh_merged.sort_values("on_time_rate")
    worst = wh_merged.iloc[0]
    alert_html = ""
    if pd.notna(worst["on_time_rate"]) and worst["on_time_rate"] < 0.80:
        prev_rate = worst.get("on_time_rate_prev", np.nan)
        prev_txt = f" (was {prev_rate:.0%} the week before)" if pd.notna(prev_rate) else ""
        alert_html = f'''<div class="alert">
          <b>⚠ Flagged this week:</b> {worst['warehouse']} on-time rate is {worst['on_time_rate']:.0%}{prev_txt} —
          well below the other warehouses. Worth a same-day check before it repeats next week.
        </div>'''

    wh_chart = bar_svg(wh_merged, "on_time_rate", "warehouse", flag_below=0.80)

    cleaning_html = (
        f"Pulled {cleaning_log['rows_in']:,} raw rows from the source export; removed "
        f"{cleaning_log['duplicate_rows_removed']} duplicate log entries, "
        f"{cleaning_log['missing_warehouse_removed']} rows missing a warehouse, and "
        f"{cleaning_log['negative_units_removed']} rows with an invalid unit count — "
        f"{cleaning_log['rows_out']:,} clean rows carried into this report."
    )

    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weekly Ops Report — week ending {week_end:%b %d, %Y}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#F3F5F4; --paper-raised:#FBFCFB; --ink:#0b0b0b; --ink-soft:#52514e; --ink-faint:#898781;
  --line:#D6DCDA; --accent:#5C7A52; --accent-wash:#E4EBE1; --red:#c94a3f; --red-wash:#F7E4E1;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#12161C; --paper-raised:#181D25; --ink:#fff; --ink-soft:#c3c2b7; --ink-faint:#6E7885;
    --line:#2A3038; --accent:#A2C295; --accent-wash:#212B1E; --red:#e07a70; --red-wash:#3a2220;
  }}
}}
*{{box-sizing:border-box;}}
body{{margin:0; background:var(--paper); color:var(--ink); font-family:"IBM Plex Sans",sans-serif;}}
.shell{{max-width:760px; margin:0 auto; padding:36px 24px 60px;}}
h1{{font-family:"Spectral",serif; font-weight:600; font-size:24px; margin:0 0 6px;}}
.eyebrow{{font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); margin-bottom:8px;}}
.subtitle{{color:var(--ink-faint); font-size:13px; margin-bottom:28px;}}
.kpi-row{{display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:28px;}}
.kpi{{background:var(--paper-raised); border:1px solid var(--line); border-radius:9px; padding:14px 16px;}}
.kpi .k{{font-family:"IBM Plex Mono",monospace; font-size:10px; text-transform:uppercase; color:var(--ink-faint);}}
.kpi .v{{font-family:"IBM Plex Mono",monospace; font-size:20px; margin-top:6px;}}
.kpi .delta{{font-size:11px; margin-top:4px; display:block;}}
.delta.up{{color:var(--accent);}} .delta.down{{color:var(--red);}} .delta.flat{{color:var(--ink-faint);}}
.alert{{background:var(--red-wash); border:1px solid var(--red); border-radius:9px; padding:14px 16px; font-size:13.5px; margin-bottom:24px; color:var(--ink);}}
h2{{font-family:"Spectral",serif; font-size:16px; margin:28px 0 10px;}}
.panel{{background:var(--paper-raised); border:1px solid var(--line); border-radius:9px; padding:16px 18px;}}
.chart-svg .lbl{{fill:var(--ink-soft); font-size:12px; font-family:"IBM Plex Sans",sans-serif;}}
.chart-svg .val{{fill:var(--ink); font-size:12px; font-family:"IBM Plex Mono",monospace;}}
.cleaning-note{{font-size:12px; color:var(--ink-faint); margin-top:26px; border-top:1px solid var(--line); padding-top:14px;}}
footer{{font-size:11.5px; color:var(--ink-faint); margin-top:20px;}}
</style>
</head>
<body>
<div class="shell">
  <div class="eyebrow">Automated Weekly Ops Report</div>
  <h1>Week ending {week_end:%B %d, %Y}</h1>
  <div class="subtitle">Generated by scripts/02_weekly_report.py — pulls the raw shipping log, cleans it, and renders this report end to end, no manual steps.</div>

  {alert_html}

  <div class="kpi-row">
    <div class="kpi"><div class="k">Total Orders</div><div class="v">{this_wk_kpi['total_orders']:,}</div>
      <span class="delta">{delta(this_wk_kpi['total_orders'], prev_wk_kpi['total_orders'], pct=False)}</span></div>
    <div class="kpi"><div class="k">On-Time Rate</div><div class="v">{this_wk_kpi['on_time_rate']:.0%}</div>
      <span class="delta">{delta(this_wk_kpi['on_time_rate'], prev_wk_kpi['on_time_rate'], higher_is_good=True)}</span></div>
    <div class="kpi"><div class="k">Delayed</div><div class="v">{this_wk_kpi['delayed']:,}</div>
      <span class="delta">{delta(this_wk_kpi['delayed'], prev_wk_kpi['delayed'], pct=False, higher_is_good=False)}</span></div>
    <div class="kpi"><div class="k">Open Backlog</div><div class="v">{this_wk_kpi['backlog_open']:,}</div>
      <span class="delta">{delta(this_wk_kpi['backlog_open'], prev_wk_kpi['backlog_open'], pct=False, higher_is_good=False)}</span></div>
  </div>

  <h2>On-time rate by warehouse</h2>
  <div class="panel">{wh_chart}</div>

  <div class="cleaning-note">{cleaning_html}</div>
  <footer>This is a static export of one week's run for the portfolio — in production this would be emailed automatically every Monday morning.</footer>
</div>
</body>
</html>
'''
    return html


def main():
    df, cleaning_log = load_and_clean(RAW / "raw_shipping_log.csv")
    df.to_csv(PROCESSED / "cleaned_shipping_log.csv", index=False)

    week_end = df["order_date"].max()
    week_end = week_end - pd.Timedelta(days=week_end.dayofweek + 1) if week_end.dayofweek != 6 else week_end
    prev_week_end = week_end - pd.Timedelta(days=7)

    this_wk = week_window(df, week_end)
    prev_wk = week_window(df, prev_week_end)

    this_kpi = kpis_for_week(this_wk)
    prev_kpi = kpis_for_week(prev_wk)
    this_wh = by_warehouse(this_wk)
    prev_wh = by_warehouse(prev_wk)

    html = render_report(week_end, this_kpi, prev_kpi, this_wh, prev_wh, cleaning_log)
    (REPORT / "index.html").write_text(html)

    pd.DataFrame([{"week_ending": week_end.date(), **this_kpi}]).to_csv(PROCESSED / "weekly_kpi_summary.csv", index=False)

    print("Cleaning log:", cleaning_log)
    print(f"\nWeek ending {week_end.date()} KPIs:", this_kpi)
    print(f"Prior week ({prev_week_end.date()}) KPIs:", prev_kpi)
    print("\nBy warehouse (this week):")
    print(this_wh.to_string(index=False))
    print(f"\nReport written to {(REPORT / 'index.html').relative_to(BASE)}")


if __name__ == "__main__":
    main()
