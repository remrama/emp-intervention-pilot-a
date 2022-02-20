import os
import numpy as np
import pandas as pd
import pingouin as pg

import colorcet as cc
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import utils

utils.load_matplotlib_settings()


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "empathy-correlations.csv")

df = pd.read_csv(import_fname)


VIDEO_SERIES_A = ["id113-vid3", "id130-vid6",
    "id168-vid1", "id174-vid3", "id181-vid2"]
VIDEO_SERIES_B = ["id116-vid6", "id118-vid5",
    "id128-vid2", "id131-vid1", "id165-vid4"]
videos = [VIDEO_SERIES_A, VIDEO_SERIES_B]
summary = df.groupby("video_id")["correlation"].agg(["mean", "sem", "std"])
table = df.pivot(index="participant_id", columns="video_id", values="correlation")

# VIDEO_SERIES_A = [1, 2, 3, 4, 5]
# VIDEO_SERIES_B = [6, 7, 8, 9, 10]
# videos = [VIDEO_SERIES_A, VIDEO_SERIES_B]
# summary = df.groupby("trial")["correlation"].agg(["mean", "sem", "std"])
# table = df.pivot(index="participant_id", columns="trial", values="correlation")

# hacky bc adding this late
subj_list = table.index.values


### sooooo hacky.
## Whole thing should be reorganized.
get_subjs = df.groupby("task_condition").participant_id.unique()
bct_subjs = get_subjs.loc["bct"]
rest_subjs = get_subjs.loc["rest"]


colormap = cc.cm.CET_R3.copy()
n_subs = df["participant_id"].nunique()
color_normvals = [ i/(n_subs-1) for i in range(n_subs) ]
colors = colormap(color_normvals)


fig, ax = plt.subplots(figsize=(3, 4), constrained_layout=True)


xticks = []

for i, video_list in enumerate(videos):

    n_videos = len(video_list)
    xvals = i*n_videos + i*1 + np.arange(n_videos)
    xticks.extend(xvals)
    bars = ax.bar(xvals, "mean", yerr="sem",
        data=summary.loc[video_list],
        color="white", edgecolor="black", linewidth=1, width=.6,
        error_kw=dict(capsize=0, ecolor="black", elinewidth=1))
    bars.errorbar.lines[2][0].set_capstyle("round")

    ticksmid = np.mean(xvals)
    txt = "Video Set A" if i == 0 else "Video Set B"
    ax.text(ticksmid, -.9, txt, ha="center", va="bottom", color="gainsboro")

    np.random.seed(1)
    JITTER = 0.05
    data = table[video_list].values
    # gross change this
    for ss, (c, row) in enumerate(zip(colors, data)):
        subject = subj_list[ss]
        condition = df[df["participant_id"].eq(subject)]["task_condition"].values[0]
        # alpha = .8 if condition == "bct" else .1
        alpha = .1
        jittered_xvals = xvals + np.random.normal(loc=0, scale=JITTER)
        ax.plot(jittered_xvals, row, "-", color=c, alpha=alpha,
            markeredgewidth=.5, markeredgecolor="white",
            linewidth=.5, markersize=2, clip_on=False)

ax.axhline(0, color="black", linewidth=1)
ax.set_ylim(-1, 1)
ax.set_ylabel(r"$\mathrm{Empathetic\ accuracy,\ }r_{E}$")
ax.tick_params(axis="both", which="both", direction="in",
    top=True, right=True)
# xlim_buffer = .8
# ax.set_xlim(xvals[0]-xlim_buffer, xvals[-1]+xlim_buffer)
ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
    minor_locator=plt.MultipleLocator(.1))
ax.set_xticks(xticks)
ax.set_xticklabels(VIDEO_SERIES_A+VIDEO_SERIES_B, rotation=45, ha="right")
# ax.set_xticklabels([r"$1^{\mathrm{st}}$ half", r"$2^{\mathrm{nd}}$ half"])
ax.grid(visible=True, axis="y", which="major",
    linewidth=1, alpha=1, color="gainsboro")
ax.set_axisbelow(True)


# Plotting variance
divider = make_axes_locatable(ax)
ax_top = divider.append_axes("top", .5, pad=.1, sharex=ax)
ax_top.bar(xticks, "std",
    data=summary.loc[VIDEO_SERIES_A+VIDEO_SERIES_B],
    color="gainsboro", edgecolor="black", linewidth=1, width=.6)
ax_top.set_ylabel(r"$\sigma_{r_{E}}$")
ax_top.tick_params(axis="both", which="both", direction="in",
    bottom=False, labelbottom=False)
ax_top.spines["top"].set_visible(False)
ax_top.spines["right"].set_visible(False)
# ax_top.spines["bottom"].set_visible(False)


# Plotting power analysis thing.
ax_top2 = divider.append_axes("top", 1, pad=.1, sharex=ax)

for i, video_list in enumerate(videos):
    n_videos = len(video_list)
    xvals = i*n_videos + i*1 + np.arange(n_videos)
    yvals, evals = table[video_list].expanding(axis=1).mean(
        ).agg(["mean", "sem"]).values
    ax_top2.fill_between(xvals, yvals-evals, yvals+evals,
        linewidth=0, color="gainsboro", alpha=1)
    ax_top2.plot(xvals, yvals, color="black", alpha=1, linewidth=.5)

    ### clnkYYYYY
    yvals, evals = table.loc[bct_subjs, video_list].expanding(axis=1).mean().agg(["mean", "sem"]).values
    ax_top2.fill_between(xvals, yvals-evals, yvals+evals, color="royalblue", alpha=.2, linewidth=0)
    ax_top2.plot(xvals, yvals, color="royalblue", alpha=1, linewidth=.5)
    yvals, evals = table.loc[rest_subjs, video_list].expanding(axis=1).mean().agg(["mean", "sem"]).values
    ax_top2.fill_between(xvals, yvals-evals, yvals+evals, color="indianred", alpha=.2, linewidth=0)
    ax_top2.plot(xvals, yvals, color="indianred", alpha=1, linewidth=.5)

    np.random.seed(1)
    JITTER = 0.05
    data = table[video_list].expanding(axis=1).mean().values
    for ss, (c, row) in enumerate(zip(colors, data)):
        subject = subj_list[ss]
        condition = df[df["participant_id"].eq(subject)]["task_condition"].values[0]
        # alpha = .8 if condition == "bct" else .1
        alpha = .1
        jittered_xvals = xvals + np.random.normal(loc=0, scale=JITTER)
        ax_top2.plot(jittered_xvals, row, "-", color=c, alpha=alpha,
            markeredgewidth=.5, markeredgecolor="white",
            linewidth=.5, markersize=2, clip_on=False)

ax_top2.set_ylabel(r"$F(r_{E})$")
ax_top2.tick_params(axis="both", which="both", direction="in",
    bottom=False, labelbottom=False)
ax_top2.spines["top"].set_visible(False)
ax_top2.spines["right"].set_visible(False)
ax_top2.spines["bottom"].set_visible(False)


# fig.align_ylabels([ax, ax_top])

export_fname = os.path.join(utils.Config.data_directory, "results",
    "emp-videocorrs.png")
plt.savefig(export_fname)
plt.close()



# ax_inset = ax.inset_axes([.4, .1, .2, .3])

fig, ax = plt.subplots(figsize=(2, 2), constrained_layout=True)

counts = df.query("pre_post=='pre'").query("trial==1"
    ).groupby(["task_condition", "video_id"]).size(
    ).rename("count").reset_index("video_id"
    ).replace(dict(video_id={"id113-vid3": "Set A", "id116-vid6": "Set B"})
    )

xvals = [0, 1, 3, 4]
yvals = counts["count"].values
ax.bar(xvals, yvals)

ax.set_ylabel(r"$n$ participants that started with this set")
ax.set_xticks(xvals)
ax.set_xticklabels(["Set A", "Set B", "Set A", "Set B"])

export_fname = os.path.join(utils.Config.data_directory, "results",
    "emp-videosets.png")
plt.savefig(export_fname)
plt.close()
