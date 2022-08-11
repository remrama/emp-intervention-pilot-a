"""
some stuff about press frequency ("breathing rate")
- press frequency, aka "breathing rate" mean and variability

for now just try and predict accuracy on each cycle
with the press/breath rate
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import utils

utils.load_matplotlib_settings()
subj_palette = utils.load_subject_palette()


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "bct-data_cycles.csv")
export_fname = os.path.join(utils.Config.data_directory, "results", "bct-rtXpresses.png")


df = pd.read_csv(import_fname)

df["participant_id"] = pd.Categorical(df["participant_id"], ordered=True)

# don't use true/false bc indexing later is weird
df["accuracy"] = df["accuracy"].replace("reset", "miscount")

# # This is a hackey way to get the length of the trial/cycle
# # since it wasn't save initially. Could go back and make it
# # part of cleaning output
# cycle_length = df.groupby("participant_id"
#     )["final_breath_rt_sum"].diff(
#     ).fillna(df["final_breath_rt_sum"]) # fill to get the first press length back
# # Get respiration rate.
# # Average press rate in that time frame.
# # convert to rate per minute 
# # How many presses/breaths occured in the amount of time
# # and convert to minutes.

# Is it this easy? Convert from ms to sec and under 60 seconds?
# Even if so this should be slightly diff than other script
# because of averaging first and such?? right?
df["rr_avg"] = df["rt_mean"].div(1000).rdiv(60)
# df["rr_std"] = df["rt_std"].div(1000).rdiv(60)
print("SD is wrong need to get that manually, substituting for now")
df["rr_std"] = df["rt_std"].div(1000).copy()

subavgs = df.groupby(["participant_id", "accuracy"]
    )[["rr_avg", "rr_std"]].agg("mean")

summdf = subavgs.groupby("accuracy").agg(["mean", "sem"])
# subavgs.unstack("correct")

trialcounts = df.groupby(["participant_id", "accuracy"]).size().unstack()

measure_order = ["rr_avg", "rr_std"]
correct_order = ["miscount", "correct"]
correct_colors = ["gainsboro", "white"]

labels = {
    "rr_avg": r"$\mathrm{Respiration\ rate,\ }\bar{f_{R}}$",
    "rr_std": r"$\mathrm{Respiration\ rate\ variation,\ }\sigma_{\bar{f_{R}}}$",
}

colors = [ subj_palette[s] if s in subj_palette else "white"
    for s in subavgs.index.get_level_values("participant_id").unique() ]
# color_cycler = plt.cycler("color", colors)

FIGSIZE = (3, 3)
SUBJ_JITTER = .05
XLIM_EDGEBUFFER = .8
BAR_KWARGS = dict(edgecolor="black", linewidth=1, width=.6,
    error_kw=dict(capsize=0, ecolor="black", elinewidth=1))
PLOT_KWARGS = dict(markersize=4, alpha=1, linewidth=.5,
    markeredgewidth=.5, markeredgecolor="white")
SCATTER_KWARGS = dict(alpha=1, linewidth=.5, edgecolor="white",
    clip_on=False, zorder=100)


fig, axes = plt.subplots(ncols=2, figsize=FIGSIZE,
    gridspec_kw=dict(wspace=.1))

for ax, m in zip(axes, measure_order):

    # barplot
    yvals = summdf[m].loc[correct_order, "mean"]
    evals = summdf[m].loc[correct_order, "sem"]
    xvals = np.arange(yvals.size)

    bars = ax.bar(xvals, yvals, yerr=evals,
        color=correct_colors, **BAR_KWARGS)
    bars.errorbar.lines[2][0].set_capstyle("round")

    ax.set_xticks(xvals)
    ax.set_xticklabels(correct_order)
    ax.set_ylabel(labels[m])
    ax.tick_params(bottom=False)
    ax.set_xlabel("BCT trial accuracy")

    data = subavgs[m].unstack()[correct_order].values
    sizedata = trialcounts[correct_order].values
    # sizedatanorm = plt.(sizedata - sizedata.min()) / sizedata.max()
    sizedatanorm = plt.Normalize(0, sizedata.max())
    np.random.seed(1)
    for c, row, sizes in zip(colors, data, sizedata):
        jittered_xvals = xvals + np.random.normal(loc=0, scale=SUBJ_JITTER)
        ax.plot(jittered_xvals, row, "-", color=c, **PLOT_KWARGS)
        msizes = 30*sizedatanorm(sizes)
        ax.scatter(jittered_xvals, row, s=msizes,
            color=c, **SCATTER_KWARGS)

    smin = sizedata.min()
    smax = sizedata.max()
    smid = int(np.mean([smin, smax]))
    legend_handles = [ plt.matplotlib.lines.Line2D([0], [0],
            label=s, marker="o", markersize=np.sqrt(30*sizedatanorm(s)),            linewidth=0, markeredgewidth=.5,
            markerfacecolor="gainsboro", markeredgecolor="white")
        for s in [10, smid, smax] ]
    legend = ax.legend(handles=legend_handles[::-1],
        loc="upper right", bbox_to_anchor=(1, .85),
        title=r"$n$ trials", handletextpad=0)

    ax.set_xlim(xvals[0]-XLIM_EDGEBUFFER, xvals[-1]+XLIM_EDGEBUFFER)
    ax.yaxis.set(major_locator=plt.MaxNLocator(nbins=5, min_n_ticks=3, steps=[1, 10]))


plt.savefig(export_fname)
utils.save_hires_copies(export_fname)
plt.close()