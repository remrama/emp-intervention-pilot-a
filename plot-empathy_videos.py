"""video by video with power analysis
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import utils

utils.load_matplotlib_settings()
subj_palette = utils.load_subject_palette()


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "empathy-correlations.csv")
export_fname = os.path.join(utils.Config.data_directory, "results", "emp-videocorrs.png")

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


colors = [ subj_palette[s] for s in table.index ]

FIGSIZE = (3, 3)
NROWS = 3
NCOLS = 2
GRIDSPEC_KWARGS = dict(wspace=.1, height_ratios=[2, 1, 3])
SUBJ_JITTER = .05

BAR_KWARGS = dict(edgecolor="black", linewidth=1,
    width=.6, error_kw=dict(capsize=0, ecolor="black", elinewidth=1))
PLOT_KWARGS = dict(alpha=.1, markeredgewidth=.5, markeredgecolor="white",
    linewidth=.5, markersize=2, clip_on=False)


fig, axes = plt.subplots(nrows=NROWS, ncols=NCOLS,
    figsize=FIGSIZE, gridspec_kw=GRIDSPEC_KWARGS,
    sharex="col", sharey="row")

# xticks = []

for r in range(NROWS):
    for c in range(NCOLS):
        ax = axes[r, c]
        video_list = videos[c]
        n_videos = len(video_list)
        xvals = np.arange(n_videos)
        # xvals = i*n_videos + i*1 + np.arange(n_videos)
        # xticks.extend(xvals)

        if r == 2: # bottom plot
            bars = ax.bar(xvals, "mean", yerr="sem",
                data=summary.loc[video_list], color="white", **BAR_KWARGS)
            bars.errorbar.lines[2][0].set_capstyle("round")

            ticksmid = np.mean(xvals)
            txt = "Video Set A" if c == 0 else "Video Set B"
            ax.text(ticksmid, -.9, txt, ha="center", va="bottom", color="gainsboro")

            np.random.seed(1)
            for subj, subj_row in table[video_list].iterrows():
                c = subj_palette[subj]
                jittered_xvals = xvals + np.random.normal(loc=0, scale=SUBJ_JITTER)
                ax.plot(jittered_xvals, subj_row.values, "-", color=c, **PLOT_KWARGS)

            ax.axhline(0, color="black", linewidth=1)
            if ax.get_subplotspec().is_first_col():
                ax.set_ylabel(r"$\mathrm{Empathetic\ accuracy,\ }r_{E}$")
            ax.set_xticks(xvals)
            ax.set_xticklabels(video_list, rotation=45, ha="right")
            ax.set_xlim(xvals[0]-1, xvals[-1]+1)
            ax.set_ylim(-1, 1)
            ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
                minor_locator=plt.MultipleLocator(.1))

        elif r == 1: # middle plot, variance across subjs
            ax.bar(xvals, "std", data=summary.loc[video_list],
                color="gainsboro", **BAR_KWARGS)
            ax.grid(False)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.tick_params(bottom=False, labelbottom=False, top=False, right=False)
            if ax.get_subplotspec().is_first_col():
                ax.set_ylabel(r"$\sigma_{r_{E}}$")

        elif r == 0: # upper plot, power analysis thing
            yvals, evals = table[video_list].expanding(axis=1).mean(
                ).agg(["mean", "sem"]).values
            ax.fill_between(xvals, yvals-evals, yvals+evals,
                linewidth=0, color="gainsboro", alpha=1, zorder=8)
            ax.plot(xvals, yvals, color="black", alpha=1, linewidth=.5, zorder=9)

            np.random.seed(1)
            for subj, subj_row in table[video_list].expanding(axis=1).mean().iterrows():
                c = subj_palette[subj]
                jittered_xvals = xvals + np.random.normal(loc=0, scale=SUBJ_JITTER)
                ax.plot(jittered_xvals, subj_row.values, "-", color=c, **PLOT_KWARGS)

            ax.set_ylim(-1, 1)
            ax.grid(False)
            ax.axhline(0, color="black", linewidth=1)
            ax.tick_params(bottom=False, labelbottom=False, top=False, right=False)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            if ax.get_subplotspec().is_first_col():
                ax.set_ylabel(r"$F(r_{E})$")

        # ### clnkYYYYY
        # yvals, evals = table.loc[bct_subjs, video_list].expanding(axis=1).mean().agg(["mean", "sem"]).values
        # ax_top2.fill_between(xvals, yvals-evals, yvals+evals, color="royalblue", alpha=.2, linewidth=0)
        # ax_top2.plot(xvals, yvals, color="royalblue", alpha=1, linewidth=.5)
        # yvals, evals = table.loc[rest_subjs, video_list].expanding(axis=1).mean().agg(["mean", "sem"]).values
        # ax_top2.fill_between(xvals, yvals-evals, yvals+evals, color="indianred", alpha=.2, linewidth=0)
        # ax_top2.plot(xvals, yvals, color="indianred", alpha=1, linewidth=.5)



fig.align_labels()


plt.savefig(export_fname)
utils.save_hires_copies(export_fname)
plt.close()