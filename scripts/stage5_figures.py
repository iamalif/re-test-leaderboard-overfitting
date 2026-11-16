"""Stage 5: figures for the paper. Reads per-competition tables only.

Run from the project root:  python scripts/stage5_figures.py
Output: paper/figures/fig1_gap_level.png, fig2_drift.png, fig3_test_size.png, fig4_prize.png (and .pdf)
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1f1f1e", "#6b6a63", "#e4e3dd"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.titlesize": 9.5, "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False,
                     "figure.dpi": 200, "savefig.bbox": "tight", "font.family": "DejaVu Sans"})
m = pd.read_csv("outputs/stage4/drift_robustness_per_competition.csv")
O, E = m[m.Cohort == "O"], m[m.Cohort == "E"]
LAB = {"O": "Original (to April 2019)", "E": "Extension (after April 2019)"}

def ecdf(ax, v, color, label, ls="-"):
    v = np.sort(v.dropna()); ax.step(v, np.arange(1, len(v) + 1) / len(v), where="post", color=color, lw=2, label=f"{label}, n = {len(v)}", ls=ls)

def bottom_legend(fig, ax, note=None):
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, fontsize=8, bbox_to_anchor=(0.5, -0.06))
    if note: fig.text(0.5, -0.11, note, ha="center", fontsize=7.5, color=MUTED)

def save(fig, name):
    fig.savefig(f"paper/figures/{name}.png"); fig.savefig(f"paper/figures/{name}.pdf"); plt.close(fig)

# Figure 1: gap level, accuracy and AUC
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0))
for ax, grp, scale, lim, xl, thr in ((axs[0], "Accuracy", 100, (-3, 5), "Mean public minus private accuracy (percentage points)", 1),
                                     (axs[1], "AUC", 1, (-0.03, 0.05), "Mean public minus private AUC", 0.01)):
    ecdf(ax, O[O.Group == grp].mean_gap * scale, BLUE, LAB["O"]); ecdf(ax, E[E.Group == grp].mean_gap * scale, ORANGE, LAB["E"])
    ax.axvline(0, color=MUTED, lw=0.8); ax.axvline(thr, color=MUTED, lw=0.8, ls=":")
    ax.set(xlim=lim, ylim=(0, 1), xlabel=xl, ylabel="Share of competitions", title=f"{grp} competitions")
    out = sum(((c[c.Group == grp].mean_gap * scale > lim[1]) | (c[c.Group == grp].mean_gap * scale < lim[0])).sum() for c in (O, E))
    ax.text(0.98, 0.04, f"{out} competitions lie\noutside the axis range\n" + "\n".join(f"{LAB[k].split(' (')[0]}: n = {len(c[c.Group == grp])}" for k, c in (("O", O), ("E", E))),
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=MUTED)
fig.tight_layout(); h = [plt.Line2D([], [], color=BLUE, lw=2), plt.Line2D([], [], color=ORANGE, lw=2)]
fig.legend(h, [LAB["O"], LAB["E"]], loc="lower center", ncol=2, fontsize=8, bbox_to_anchor=(0.5, -0.07))
save(fig, "fig1_gap_level")

# Figure 2: share of competitions with positive drift, with Wilson intervals
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h
rows = []
for coh, x in (("O", O), ("E", E)):
    for g in ("All metrics", "Accuracy", "AUC", "MAP@K", "LogLoss", "MulticlassLoss", "Regression", "Other"):
        v = (x if g == "All metrics" else x[x.Group == g]).drift_mean.dropna()
        if len(v) >= 8: rows.append((coh, g, int((v > 0).sum()), len(v)))
order = ["All metrics", "Accuracy", "AUC", "MAP@K", "LogLoss", "MulticlassLoss", "Regression", "Other"]
fig, ax = plt.subplots(figsize=(7.2, 3.4))
for coh, g, k, n in rows:
    y = len(order) - 1 - order.index(g) + (0.17 if coh == "O" else -0.17); p, lo, hi = wilson(k, n); col = BLUE if coh == "O" else ORANGE
    ax.plot([lo, hi], [y, y], color=col, lw=2, solid_capstyle="round"); ax.plot(p, y, "o", color=col, ms=6, mec="white", mew=1)
    ax.text(hi + 0.012, y, f"{k} of {n}", va="center", fontsize=7, color=MUTED)
ax.axvline(0.5, color=MUTED, lw=0.8)
ax.set(yticks=range(len(order)), yticklabels=order[::-1], xlim=(0.2, 1.0), xlabel="Share of competitions with positive team drift (95% interval)",
       title="Later submissions favour the public leaderboard more than earlier ones")
ax.grid(axis="y", visible=False)
ax.plot([], [], "o-", color=BLUE, label=LAB["O"]); ax.plot([], [], "o-", color=ORANGE, label=LAB["E"]); fig.tight_layout(); bottom_legend(fig, ax)
save(fig, "fig2_drift")

# Figure 3: test-set size, accuracy competitions with inferred sizes
a = m[(m.Group == "Accuracy") & m.p05_all.notna()].copy(); a["total"] = a.n_pub + a.n_priv
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0))
for coh, col in (("O", BLUE), ("E", ORANGE)):
    x = a[a.Cohort == coh]
    axs[0].scatter(x.total, x.mean_gap.abs() * 100, s=16, color=col, edgecolor="white", linewidth=0.5, label=f"{LAB[coh]}, n = {len(x)}")
    axs[1].scatter(x.total, x.top10_gap_excess * 100, s=16, color=col, edgecolor="white", linewidth=0.5)
axs[0].set(xscale="log", yscale="log", xlabel="Test-set size, public plus private", ylabel="Absolute mean gap (percentage points)", title="Gap size falls with test-set size")
axs[1].set(xscale="log", yscale="symlog", xlabel="Test-set size, public plus private", ylabel="Top-10% gap minus selection-only gap (pp)", title="Excess over selection does not")
axs[1].set_yscale("symlog", linthresh=0.1); axs[1].axhline(0, color=MUTED, lw=0.8)
for ax in axs: ax.axvline(10_000, color=MUTED, lw=0.8, ls=":")
fig.tight_layout(w_pad=4.5); bottom_legend(fig, axs[0], "Accuracy competitions with test-set sizes inferred from scores. Dotted line: 10,000 examples.")
save(fig, "fig3_test_size")

# Figure 4: prize competitions, relative gap of all and of first submissions
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
pz = m[m.Segment.isin(["Featured", "Research"])]
for ax, col_, ttl in ((axs[0], "rel_mean_gap", "All submissions"), (axs[1], "rel_first", "First submission of each team")):
    pz = pz.assign(rel_first=pz.first_mean_gap / pz.team_spread)
    ecdf(ax, pz[pz.Cohort == "O"][col_].clip(-3, 3), BLUE, LAB["O"]); ecdf(ax, pz[pz.Cohort == "E"][col_].clip(-3, 3), ORANGE, LAB["E"])
    ax.axvline(0, color=MUTED, lw=0.8); ax.set_xscale("symlog", linthresh=0.01); ax.set(xlim=(-3, 3), ylim=(0, 1), title=ttl,
        xlabel="Mean gap as a multiple of the team spread")
    ax.set_xticks([-1, -0.1, 0, 0.1, 1]); ax.set_xticklabels(["-1", "-0.1", "0", "0.1", "1"]); ax.minorticks_off()
axs[0].set_ylabel("Share of competitions"); fig.tight_layout(); bottom_legend(fig, axs[0], "Featured and Research competitions. Values beyond 3 team spreads are drawn at the axis edge.")
save(fig, "fig4_prize")
print("figures written")
