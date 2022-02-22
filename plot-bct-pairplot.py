############################# plot correlation between
############################# respiration rate and number of presses
############################# with marginals
############################# should be near 1 to 1, but this
############################# also shows outliers for both press count and RR
# pairplot with subject
# respiration rate mean
# respiration rate variance
# respiration rate slope
# BCT accuracy
# n presses
# empathy task BEFORE intervention

import os
import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.pyplot as plt
# from mpl_toolkits.axes_grid1 import make_axes_locatable
import utils

utils.load_matplotlib_settings()
subj_palette = utils.load_subject_palette()

print("still unclear about handling nan cycles from repeated presses")
# # assert not df.isnull().values.any()
# df.dropna(inplace=True)


# # convert RTs to seconds
# df["rt"] /= 1000



export_fname = os.path.join(utils.Config.data_directory, "results", "bct-pairplot.png")


#### Loading in a lot of different data for this.
#### Bc relating lots of different measures that were
#### derived in other scripts.
data_dir = utils.Config.data_directory


##### Load/extract subject-level variables for respiration rate.
import_fname = os.path.join(data_dir, "results", "bct-respirationrate.csv")
rr_subj_descriptives = pd.read_csv(import_fname, index_col="participant_id")
RESPIRATION_VARIABLES = ["mean", "std", "slope"]
rr_subj_descriptives = rr_subj_descriptives[RESPIRATION_VARIABLES]

##### Load/calculate subject-level variables for BCT accuracy.
import_fname = os.path.join(data_dir, "derivatives", "bct-data_cycles.csv")
bct_cycles = pd.read_csv(import_fname)
bct_cycles["correct"] = bct_cycles["accuracy"].eq("correct")
bct_acc = bct_cycles.groupby("participant_id")["correct"].mean().rename("bct_acc")

##### Load/calculate subject-level variables for Empathy task accuracy.
import_fname  = os.path.join(utils.Config.data_directory, "derivatives", "empathy-correlation_avgs.csv")
empathy_corrs = pd.read_csv(import_fname)
empathy_baseline = empathy_corrs.query("task_condition=='bct'"
    ).query("pre_post=='pre'").set_index("participant_id"
    )["correlation"].rename("empathy_baseline")
empathy_change = empathy_corrs[empathy_corrs.duplicated("participant_id", keep=False) # keep only subjs with both pre and post
    ].query("task_condition=='bct'" # only care about BCT here
    ).pivot(index="participant_id", columns="pre_post", values="correlation" # reshape for confidence
    ).reindex(columns=["pre", "post"]).diff(axis=1 # reorder and take diff so increases are positive
    )["post"].rename("empathy_change")

df = pd.concat([rr_subj_descriptives, bct_acc,
    empathy_baseline, empathy_change], axis=1)



var_order = df.columns.tolist()
n_vars = len(var_order)
figsize = (n_vars*.8, n_vars*.8)
fig, axes = plt.subplots(ncols=n_vars, nrows=n_vars,
    figsize=figsize, sharex=False, sharey=False)


# LIMITS = {
#     # "n_presses": (0, 510),
#     "mean": (0, 60),
#     "std": (0, 8),
#     "slope": (-.12, .12),
#     "bct_acc": (0, 1),
#     "empathy_baseline": (0, 1),
#     "empathy_change": (-1, 1),
# }

LABELS = {
    # "n_presses": r"$n$ presses",
    "mean": r"$\bar{f_{R}}$",
    "std": r"$\sigma_{\bar{f_{R}}}$",
    "slope": r"$m_{f_{R}}$",
    "bct_acc": "BCT %",
    "empathy_baseline": r"Empathy $r_{pre}$",
    "empathy_change": r"$r_{post}-r_{pre}$",
}

SCATTER_KWARGS = dict(s=30, alpha=.75, linewidth=.5, edgecolor="white", clip_on=False)
HIST_KWARGS = dict(density=True, histtype="stepfilled", color="white",
    clip_on=False, edgecolor="black", linewidth=1)
RUG_KWARGS = dict(ymax=.1, alpha=.75, linewidth=2)

SYMMETRIC_VARS = ["slope", "empathy_change"]

colors = [ subj_palette[s] for s in df.index ]

for r in range(n_vars):
    for c in range(n_vars):
        ax = axes[r, c]
        ax.set_box_aspect(1)
        yvar = var_order[r]
        xvar = var_order[c]
        ax.grid(False)

        ax.tick_params(left=False, bottom=False, top=False, right=False)

        symmetric_xticks = xvar in SYMMETRIC_VARS
        symmetric_yticks = yvar in SYMMETRIC_VARS
        major_xlocator = plt.MaxNLocator(nbins=2, min_n_ticks=2, symmetric=symmetric_xticks, steps=[1, 5, 10], prune=None)
        major_ylocator = plt.MaxNLocator(nbins=2, min_n_ticks=2, symmetric=symmetric_yticks, steps=[1, 5, 10], prune=None)
        major_formatter = plt.FuncFormatter(utils.no_leading_zeros)
        ax.xaxis.set(major_locator=major_xlocator, major_formatter=major_formatter)
        if r > c: # lower triangle
            ax.yaxis.set(major_locator=major_ylocator, major_formatter=major_formatter)

        if c == r: # xvar == yvar
            # ax.get_shared_y_axes().join(ax, axes[0,0])
            # for x in ax._shared_y_axes:
            #     for xx in x:
            #         ax.get_shared_y_axes().remove(xx)
            data = df[xvar].values
            n, bins, patches = ax.hist(data, **HIST_KWARGS)
            # assert np.all(bins >= LIMITS[xvar][0])
            # assert np.all(bins <= LIMITS[xvar][1])
            # ax.set_xlim(*LIMITS[xvar])
            for side, spine in ax.spines.items():
                if side in ["top", "left", "right"]:
                    spine.set_visible(False)
            ax.tick_params(left=False, labelleft=False, top=False, right=False)
            if c+1 < n_vars:
                ax.tick_params(bottom=False, labelbottom=False)
            
            # rugplot
            for col, x in zip(colors, data):
                ax.axvline(x, color=col, **RUG_KWARGS)

        elif r < c: # upper triangle
            ax.axis("off")
        elif r > c: # lower triangle
            # assert df[xvar].dropna().between(*LIMITS[xvar], inclusive="both").all()
            # assert df[yvar].dropna().between(*LIMITS[yvar], inclusive="both").all()
            # ax.get_shared_y_axes().join(ax, axes[r, c-1])
            ax.scatter(xvar, yvar, data=df, color=colors, **SCATTER_KWARGS)
            # ax.set_xlim(*LIMITS[xvar])
            # ax.set_ylim(*LIMITS[yvar])
            if c > 0:
                ax.tick_params(which="both", labelleft=False)

            # run correlation
            x = df.dropna(subset=[xvar, yvar])[xvar].values
            y = df.dropna(subset=[xvar, yvar])[yvar].values
            slope, intercept, rval, pval, stderr = stats.linregress(x, y)
            r_txt = fr"$r={rval:.2f}$"
            if abs(rval) > 0 and abs(rval) < 1:
                r_txt = r_txt.replace("0", "", 1)
            sigchars = "*" * sum([ pval < x for x in (.05, .01, .001) ])
            r_txt = sigchars + r_txt
            # if p < .001:
            #     p_txt = r"$p<.001$"
            # else:
            #     p_txt = fr"$p={pval:.2f}$"
            txt_color = "black" if pval < .1 else "gainsboro"
            ax.text(.95, .05, r_txt, color=txt_color,
                transform=ax.transAxes, ha="right", va="bottom")

        if c == 0:
            ax.set_ylabel(LABELS[yvar], labelpad=1)
        if r+1 == n_vars:
            ax.set_xlabel(LABELS[xvar], labelpad=1)
        else:
            ax.tick_params(labelbottom=False)





# fig.align_ylabels(axes)
# fig.align_xlabels(axes)
fig.align_labels()




####################### Legend by itself

ax_inset = fig.add_axes([.6, .6, .3, .3])
ax_inset.axis("off")

# Add a dummy item at the end so each column is from a specific intervention task
# (found the number manually, but could get it by looking for the point where IDs stop increasing)
subj_palette["dummy1"] = "none"
subj_palette["dummy2"] = "none"
handles = [ plt.matplotlib.patches.Patch(edgecolor="none",
        facecolor=c, label="" if isinstance(s, str) else s)
    for s, c in subj_palette.items() ]

legend = ax_inset.legend(handles=handles,
    title="Participant ID",
    loc="center", borderaxespad=2,
    framealpha=1, frameon=True,
    ncol=2, columnspacing=1,
    labelspacing=.2, handletextpad=.2,
    handlelength=2,
)
# for patch in legend.get_patches():
#     patch.set_height(22)
legend.get_frame().set_edgecolor("black")
legend.get_frame().set_linewidth(1)



plt.savefig(export_fname)
utils.save_hires_copies(export_fname)
plt.close()