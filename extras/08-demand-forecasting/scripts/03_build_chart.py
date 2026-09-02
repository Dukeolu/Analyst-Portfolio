"""Extra 08 -- Step 3: one chart -- actual vs. all three forecasts over the holdout,
with the training history for context."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
CHARTS = BASE / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

full = pd.read_csv(RAW / "weekly_demand.csv", parse_dates=["week_start"])
fc = pd.read_csv(PROCESSED / "forecast_vs_actual.csv", parse_dates=["week_start"])

BLUE, ORANGE, AQUA, INK, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#1a1a1a", "#d9dcd8"

fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
history = full[full["week_start"] < fc["week_start"].min()]
ax.plot(history["week_start"], history["units_sold"], color="#9a988f", linewidth=1.2, label="History (train)")
ax.plot(fc["week_start"], fc["actual"], color=INK, linewidth=1.8, label="Actual (holdout)")
ax.plot(fc["week_start"], fc["naive"], color="#c0392b", linewidth=1.1, linestyle=":", label="Naive (flat)")
ax.plot(fc["week_start"], fc["seasonal_naive"], color=ORANGE, linewidth=1.3, linestyle="--", label="Seasonal naive")
ax.plot(fc["week_start"], fc["holt_winters"], color=BLUE, linewidth=1.8, label="Holt-Winters")

ax.axvline(fc["week_start"].min(), color="#898781", linewidth=0.8, linestyle=(0, (1, 2)))
ax.text(fc["week_start"].min(), ax.get_ylim()[1] * 0.97, "  holdout starts", fontsize=8.5, color="#898781", va="top")

ax.set_title("Weekly demand: actual vs. forecast (52-week holdout)", fontsize=13, fontweight="bold", loc="left")
ax.set_ylabel("Units sold")
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.legend(frameon=False, fontsize=9, loc="upper left", ncols=2)
fig.tight_layout()
fig.savefig(CHARTS / "actual_vs_forecast.png")
print(f"Chart written to {(CHARTS / 'actual_vs_forecast.png').relative_to(BASE)}")
