# %% [markdown]
# #### 9.11. Charts for the slides
#
# - **Stage:** presentation. No new training: the tuning tables from 5.1 and 6.1, the validation predictions (`PREDS`) and `model_table`.
# - **Three charts**, the same ones as in the PowerPoint, in the deck's colours:
#   1. XGBoost: Poisson deviance by tree depth (best number of trees for each depth), against the baseline.
#   2. Random Forest: Poisson deviance by rows per leaf (best share of features for each leaf size), against the baseline.
#   3. How many more accidents a weekend day has than an ordinary weekday, per year (holidays left out of both).
# - The PNG files are saved in `outputs/figures`, next to the maps (section 9.10).

# %%
# 9.11.1. Deck colours and one helper for the two tuning charts
DECK = {"dark": "#434343", "taupe": "#908269", "light": "#CFC3AC", "muted": "#595959"}
FIGURES = ROOT / "outputs/figures"
FIGURES.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.family"] = ["Catamaran", "Arial", "DejaVu Sans"]   # the deck's body font, if installed

# Poisson deviance of the baseline on the validation weekends and holidays (1.148)
BASELINE_DEV = score_table({"baseline_dayoff_365d": PREDS["baseline_dayoff_365d"]})["Poisson_dev"].iloc[0]


def plot_tuning(dev, labels, title, filename, xmin=1.10, xmax=1.17):
    """Horizontal bars: Poisson deviance per setting, best in dark, baseline in taupe. Lower is better."""
    values = list(dev.values) + [BASELINE_DEV]
    names = list(labels) + ["Baseline"]
    best = int(np.argmin(dev.values))
    names[best] += " (best)"
    colors = [DECK["dark"] if i == best else DECK["light"] for i in range(len(dev))] + [DECK["taupe"]]

    fig, ax = plt.subplots(figsize=(6, 3.6))
    y = np.arange(len(values))[::-1]                      # first setting at the top
    ax.barh(y, [v - xmin for v in values], left=xmin, color=colors, height=0.6)
    for yi, v in zip(y, values):
        ax.text(v + 0.0008, yi, f"{v:.3f}", va="center", fontsize=10, fontweight="bold", color=DECK["dark"])
    ax.set_yticks(y, names, fontsize=10, color=DECK["muted"])
    ax.set_xlim(xmin, xmax)
    ax.xaxis.set_visible(False)
    for side in ["top", "right", "bottom"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(DECK["light"])
    ax.set_title(title, fontsize=12, fontweight="bold", color=DECK["dark"])
    fig.text(0.01, 0.01, f"Poisson deviance, validation weekends and holidays · lower is better · axis starts at {xmin:.2f}",
             fontsize=8, color=DECK["muted"])
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIGURES / filename, dpi=200, bbox_inches="tight")
    plt.show()

# %%
# 9.11.2. XGBoost: best Poisson deviance for each tree depth (over the numbers of trees tried)
xgb_by_depth = xgb_tuning.groupby(level="max_depth")["Poisson_dev"].min().sort_index()
plot_tuning(xgb_by_depth, [f"Depth {d}" for d in xgb_by_depth.index],
            "XGBoost · tree depth", "tuning_xgboost_depth.png")
xgb_by_depth.round(3).to_frame()

# %%
# 9.11.3. Random Forest: best Poisson deviance for each leaf size (over the shares of features tried), largest leaves first
rf_by_leaf = rf_tuning.groupby(level="min_samples_leaf")["Poisson_dev"].min().sort_index(ascending=False)
plot_tuning(rf_by_leaf, [f"{n} rows" for n in rf_by_leaf.index],
            "Random Forest · rows per leaf", "tuning_random_forest_leaf.png")
rf_by_leaf.round(3).to_frame()

# %%
# 9.11.4. Weekend effect per year: accidents per region and weekend day vs per region and ordinary weekday
# Holidays are left out of both groups, so the bars show the weekend effect alone
years = [2023, 2024, 2025]
mt = model_table[model_table["date"].dt.year.isin(years) & (model_table["is_holiday"] == 0)]
per_day = mt.groupby([mt["date"].dt.year, "is_weekend"])["accidents"].mean().unstack()
weekend_uplift = per_day[1] / per_day[0] - 1          # 0.138, 0.097, 0.059

fig, ax = plt.subplots(figsize=(5, 3.8))
labels = [str(y) if y != 2025 else "2025 (test)" for y in weekend_uplift.index]
colors = [DECK["light"]] * (len(labels) - 1) + [DECK["taupe"]]
bars = ax.bar(labels, weekend_uplift.values, color=colors, width=0.6)
for b, v in zip(bars, weekend_uplift.values):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.003, f"+{v:.0%}", ha="center", fontsize=11,
            fontweight="bold", color=DECK["dark"])
ax.set_ylim(0, 0.16)
ax.yaxis.set_visible(False)
for side in ["top", "right", "left"]:
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(DECK["light"])
ax.tick_params(axis="x", colors=DECK["muted"], labelsize=10)
ax.set_title("Extra accidents per weekend day vs a weekday", fontsize=12, fontweight="bold", color=DECK["dark"])
fig.tight_layout()
fig.savefig(FIGURES / "weekend_uplift_by_year.png", dpi=200, bbox_inches="tight")
plt.show()

# The holiday figure quoted beside the chart: accidents per region and holiday, 2024 -> 2025 (1.92 -> 2.40)
hol = model_table[model_table["date"].dt.year.isin(years) & (model_table["is_holiday"] == 1)]
display(pd.DataFrame({"weekend_vs_weekday_%": (100 * weekend_uplift).round(1),
                      "accidents_per_region_holiday": hol.groupby(hol["date"].dt.year)["accidents"].mean().round(2)}))
