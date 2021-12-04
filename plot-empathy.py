"""Plot the aggregate correlation results and run stats.
"""
import os
import pandas as pd
import pingouin as pg
import config as c

import seaborn as sea
import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = "Arial"
plt.rcParams["mathtext.it"] = "Arial:italic"
plt.rcParams["mathtext.bf"] = "Arial:bold"


import_fname = os.path.join(c.DATA_DIR, "derivatives", "empathy-correlations.csv")
export_fname_stats = os.path.join(c.DATA_DIR, "results", "empathy.csv")
export_fname_plot  = os.path.join(c.DATA_DIR, "results", "empathy.png")


# load data
df = pd.read_csv(import_fname)

# average within pre and post for each subject
df = df.groupby(["participant_id", "task_condition", "pre_post"]
    )["correlation"].mean(
    ).reset_index()


################ run stats

stats = pg.rm_anova(data=df, dv="correlation", subject="participant_id",
    within=["task_condition", "pre_post"],
    detailed=True, effsize="np2", correction="auto")

stats.to_csv(export_fname_stats, index=False, encoding="utf-8", na_rep="NA")

################


# variables
COLORS = dict(mw="gainsboro", bct="orchid")
FIGSIZE = (3, 3)

# draw
fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)
sea.barplot(data=df, y="correlation",
    x="pre_post", order=["pre", "post"],
    hue="task_condition", hue_order=["mw", "bct"],
    palette=COLORS, errwidth=1, capsize=.05, errcolor="k")
sea.swarmplot(data=df, y="correlation",
    x="pre_post", order=["pre", "post"],
    hue="task_condition", hue_order=["mw", "bct"],
    dodge=2,
    palette=COLORS, edgecolor="k", linewidth=1)

# aesthetics
trim_lead0 = lambda x, pos: f"{x:.2f}"[1:] if 0<abs(x)<1 else f"{x:.2f}"
ax.set_xlabel("")
ax.set_xticks([0, 1])
ax.set_xticklabels(["before\ntask", "after\ntask"])
ax.set_xlim(-.7, 1.7)
ax.set_ylim(0, 1)
ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
             minor_locator=plt.MultipleLocator(.1),
             major_formatter=plt.FuncFormatter(c.no_leading_zeros))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# legend
legend_handles = [ plt.matplotlib.patches.Patch(edgecolor="none",
        facecolor=c, label=l.upper()) for l, c in COLORS.items() ]
legend = ax.legend(handles=legend_handles,
    title="Intervention task",
    bbox_to_anchor=(0, 1), loc="upper left",
    borderaxespad=0, frameon=False,
    labelspacing=.2, # vertical space between entries
    handletextpad=.2) # space between legend markers and labels
legend._legend_box.align = "left"

# draw pvalues
pval_ser = stats.set_index("Source")["p-unc"]
for test, p in pval_ser.items():

    if p < .001:
        pval_str = r"$p<.001$"
    else:
        pval_str = f"{p:.3f}".lstrip("0")
        pval_str = rf"$p={pval_str}$"
    if test == "task_condition":
        txt = f"BCT/MW effect: {pval_str}"
        yval = 1
        weight = "normal"
    elif test == "pre_post":
        txt = f"Pre/post effect: {pval_str}"
        yval = .95
        weight = "normal"
    elif test == "task_condition * pre_post":
        txt = f"Interaction: {pval_str}"
        yval = .9
        weight = "bold"
    ax.text(1, yval, txt, transform=ax.transAxes,
        fontsize=8, ha="right", va="top", weight=weight)

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
plt.close()