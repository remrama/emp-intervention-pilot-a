"""Plot the aggregate correlation results and run stats.

IMPORTS
=======
    - correlations for each subj/video, derivatives/empathy-correlations.csv

EXPORTS
=======
    - correlation group stats, derivatives/empathy-correlation_avgs.csv
    - correlation group stats, derivatives/empathy-correlation_stats.csv
    - correlation group stats, derivatives/empathy-correlation_plot.png
"""
import os
import numpy as np
import pandas as pd
import pingouin as pg

import matplotlib.pyplot as plt

import utils

utils.load_matplotlib_settings()
subj_palette = utils.load_subject_palette()


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "empathy-correlations.csv")
export_fname_avgs  = os.path.join(utils.Config.data_directory, "derivatives", "empathy-correlation_avgs.csv")
export_fname_stats = os.path.join(utils.Config.data_directory, "results", "empathy-correlation_stats.csv")
export_fname_plot  = os.path.join(utils.Config.data_directory, "results", "empathy-correlation_plot.png")


# load data
df = pd.read_csv(import_fname)

# average within pre and post for each subject
df = df.groupby(["participant_id", "task_condition", "pre_post"]
    )["correlation"].mean(
    ).reset_index(
    ).sort_values(["participant_id", "task_condition", "pre_post"],
                  ascending=[True, True, False])

df.to_csv(export_fname_avgs, index=False, encoding="utf-8", na_rep="NA")


################ run stats

print("manually removing 3 subjects without both pre and post (both BCT)")
stats_df = df[~df["participant_id"].isin([147, 246, 256])]

anova_stats = pg.mixed_anova(data=stats_df, dv="correlation",
    between="task_condition", within="pre_post", subject="participant_id",
    effsize="np2", correction="auto")

pairwise_stats = pg.pairwise_ttests(data=stats_df, dv="correlation",
    between="task_condition", within="pre_post", subject="participant_id",
    effsize="hedges", correction="auto",
    parametric=False, marginal=True, padjust="none",
    return_desc=False, interaction=True, within_first=False)

anova_stats.to_csv(export_fname_stats, index=False, encoding="utf-8", na_rep="NA")

################


# variables
# COLORS = dict(rest="gainsboro", bct="orchid")
COLORS = dict(pre="white", post="gainsboro")
FIGSIZE = (2.5, 3.5)
TASK_ORDER = ["rest", "bct"]
INTERVENTION_ORDER = ["pre", "post"]

ordered_indx = pd.MultiIndex.from_product([TASK_ORDER, INTERVENTION_ORDER], names=["task_condition", "pre_post"])

summary_df = df.groupby(["task_condition", "pre_post"]
    )["correlation"].agg(["mean", "sem"]
    ).reindex(index=ordered_indx)

# draw
fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

XLIM_EDGEBUFFER = .5
XLIM_GAPBUFFER = .5
xvals = np.array([0., 1, 2, 3])
xvals[2:] += XLIM_GAPBUFFER

SUBJ_JITTER = 0.05    
BAR_KWARGS = dict(width=1, edgecolor="black", linewidth=1,
    error_kw=dict(capsize=0, ecolor="black", elinewidth=1))
PLOT_KWARGS = dict(alpha=1, markeredgewidth=.5, markeredgecolor="white",
    linewidth=.5, markersize=4)

summary_df["color"] = summary_df.index.map(lambda x: COLORS[x[1]])
summary_df["xloc"] = xvals

bars = ax.bar("xloc", "mean", yerr="sem", color="color",
    data=summary_df, **BAR_KWARGS)
bars.errorbar.lines[2][0].set_capstyle("round")

np.random.seed(1)

for subj, subj_df in df.groupby("participant_id"):
    c = subj_palette[subj]
    data = subj_df.set_index(["task_condition", "pre_post"]
        ).reindex(index=ordered_indx
        )["correlation"].values
    jittered_xvals = xvals + np.random.normal(loc=0, scale=SUBJ_JITTER)
    ax.plot(jittered_xvals, data, "-o", color=c, **PLOT_KWARGS)


ax.axhline(0, linewidth=1, linestyle="solid", color="black")
ax.set_xticks([xvals[:2].mean(), xvals[2:].mean()])
xticklabels = [ x.upper() + "\nintervention" for x in TASK_ORDER ]
ax.set_xticklabels(xticklabels)
ylabel = r"Empathetic accuracy, $r_{E}$"
#ylabel += "\n" + r"$\rightarrow$ perfect agreement"
ax.set_ylabel(ylabel)
ax.tick_params(bottom=False)
xmin = xvals[0] - BAR_KWARGS["width"]/2 - XLIM_EDGEBUFFER
xmax = xvals[-1] + BAR_KWARGS["width"]/2 + XLIM_EDGEBUFFER
ax.set_xlim(xmin, xmax)
ax.set_ylim(-.2, 1)
ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
    minor_locator=plt.MultipleLocator(.1),
    major_formatter=plt.FuncFormatter(utils.no_leading_zeros))
# ax.spines["top"].set_visible(False)
# ax.spines["right"].set_visible(False)
ax.grid(False)


# legend
legend_handles = [ plt.matplotlib.patches.Patch(edgecolor="black",
        linewidth=.5,
        facecolor=c, label=l+"-intervention") for l, c in COLORS.items() ]
legend = ax.legend(handles=legend_handles,
    # title="Intervention task",
    bbox_to_anchor=(.05, 1), loc="upper left")
legend._legend_box.align = "left"


# significance text
# (there are lots to choose from so be selective)

sigcolor = lambda p: "black" if p < .1 else "gainsboro"

for test in ["Interaction", "bct", "rest"]:
    ytxt = .84 # in axis coordinates
    TEXT_VBUFF = .01
    if test == "Interaction":
        pval = anova_stats.set_index("Source").loc[test, "p-unc"]
        xtxt = xvals[1:3].mean()
        ax.scatter([xtxt], [ytxt], s=15, marker="x",
            transform=ax.get_xaxis_transform(),
            color=sigcolor(pval), linewidth=.5)
        ax.scatter([xtxt], [ytxt], s=30, marker="o",
            transform=ax.get_xaxis_transform(),
            facecolor="none", edgecolor=sigcolor(pval), linewidth=.5)
    else:
        pval = pairwise_stats.set_index("task_condition").loc[test, "p-unc"]
        xindx = TASK_ORDER.index(test)
        xmin, xmax = xvals[2*xindx:2*xindx+2]
        xtxt = xvals[2*xindx:2*xindx+2].mean()
        ax.hlines(y=ytxt, xmin=xmin, xmax=xmax,
            linewidth=1, color=sigcolor(pval), capstyle="round",
            transform=ax.get_xaxis_transform())
    # sigchars = "*" * sum([ pval<cutoff for cutoff in [.05, .01, .001] ])
    ptxt = r"p<0.001" if pval < .001 else fr"$p={pval:.2f}$"
    ptxt = ptxt.replace("0", "", 1)
    ax.text(xtxt, ytxt+TEXT_VBUFF, ptxt, color=sigcolor(pval),
        transform=ax.get_xaxis_transform(), ha="center", va="bottom")



## draw pvalues
# pval_ser = anova_stats.set_index("Source")["p-unc"]
# for test, p in pval_ser.items():
#     if p < .001:
#         pval_str = r"$p<.001$"
#     else:
#         pval_str = f"{p:.3f}".lstrip("0")
#         pval_str = rf"$p={pval_str}$"
#     if test == "task_condition":
#         txt = f"BCT/rest effect: {pval_str}"
#         yval = 1
#         weight = "normal"
#     elif test == "pre_post":
#         txt = f"Pre/post effect: {pval_str}"
#         yval = .95
#         weight = "normal"
#     elif test == "task_condition * pre_post":
#         txt = f"Interaction: {pval_str}"
#         yval = .9
#         weight = "bold"
#     ax.text(1, yval, txt, transform=ax.transAxes,
#         fontsize=8, ha="right", va="top", weight=weight)

    # sigchars = "*" * sum([ p<cutoff for cutoff in [.05, .01, .001] ])
    # if not sigchars:
    #     sigchars = "^" if p < .1 else "ns"
    # SPACER = .2 # space between each stacked significance text
    # y = max(yvals+yerrs) # highest of the two bars
    # x = sum(xvals)/len(xvals) # middle of the two bars
    # # draw a line a bit up from that
    # ax.hlines(y=y+SPACER, xmin=xvals[0], xmax=xvals[1],
    #     linewidth=2, color="k", capstyle="round")
    # # asterisks above that
    # weight = "bold" if not sigchars.isalpha() else "normal"
    # valign = "center" if not sigchars.isalpha() else "bottom"
    # fsize = 14 if not sigchars.isalpha() else 10
    # ax.text(x, y+SPACER, sigchars, weight=weight,
    #     fontsize=fsize, ha="center", va=valign)
    # # effect size above that
    # ax.text(x+BAR_ARGS["width"], y+SPACER*2, effsize_str,
    #     fontsize=10, ha="right", va="bottom")
    # # pvalue above that
    # ax.text(x+BAR_ARGS["width"], y+SPACER*3, pval_str,
    #     fontsize=10, ha="right", va="bottom")



plt.savefig(export_fname_plot)
utils.save_hires_copies(export_fname_plot)
plt.close()