"""Plot all raw timecourses.

It's not the most optimal but it's not a big deal.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import config as c

import seaborn as sea
import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
# plt.rcParams["mathtext.fontset"] = "custom"
# plt.rcParams["mathtext.rm"] = "Arial"
# plt.rcParams["mathtext.it"] = "Arial:italic"
# plt.rcParams["mathtext.bf"] = "Arial:bold"

SAMPLE_RATE = .5


import_fname = os.path.join(c.DATA_DIR, "derivatives", "empathy.csv")
export_fname = os.path.join(c.DATA_DIR, "results", "empathy-all.png")


# load data
df = pd.read_csv(import_fname)


# this whole colormapping is a bit lazy atm
# but change participant numbers so they aren't so spread out
# so we can use a categorical colormap
# (this will change once there are more subjects)
COLORMAP = "Accent"
cmap = plt.cm.get_cmap(COLORMAP)
assert df["participant_id"].nunique() <= cmap.N
df["participant_id"] = df["participant_id"].map(df["participant_id"].unique().tolist().index)


# build the plots
FIGSIZE = (4, 6)
fig, axes = plt.subplots(nrows=5, ncols=2, figsize=FIGSIZE,
    sharex=True, sharey=False, constrained_layout=True)

for (video_id, vid_df), ax in zip(df.groupby("video_id"), axes.flat):
    actor_id  = video_id.split("id")[1].split("-")[0]
    actor_nid = video_id.split("vid")[1]
    actor_basename = f"target_{actor_id}_{actor_nid}_normal.csv"
    crowd_basename = f"results_{actor_id}_{actor_nid}.csv"
    actor_filename = os.path.join(c.DATA_DIR, "SENDv1", "ratings", actor_basename)
    crowd_filename = os.path.join(c.DATA_DIR, "SENDv1", "ratings", crowd_basename)
    actor_ratings = pd.read_csv(actor_filename, index_col="time")[" rating"].values
    crowd_ratings = pd.read_csv(crowd_filename, index_col="time")["evaluatorWeightedEstimate"].values
    actor_ratings = stats.zscore(actor_ratings, nan_policy="raise")
    crowd_ratings = stats.zscore(crowd_ratings, nan_policy="raise")
    # plot the actor and crowd nice and bold
    xvals1 = np.arange(0, len(actor_ratings)*SAMPLE_RATE, SAMPLE_RATE)
    xvals2 = np.arange(0, len(crowd_ratings)*SAMPLE_RATE, SAMPLE_RATE)
    ax.plot(xvals1, actor_ratings, label="actor", color="k", alpha=1, lw=1, ls="solid", zorder=3)
    ax.plot(xvals2, crowd_ratings, label="crowd", color="k", alpha=1, lw=1, ls="dashed", zorder=2)
    ax.text(1, 0, video_id, ha="right", va="bottom", transform=ax.transAxes,
        fontsize=6)
    # loop over all the subjects
    for participant_id, ser in vid_df.groupby("participant_id")["rating"]:
        color = cmap(participant_id)
        subj_ratings = stats.zscore(ser.values, nan_policy="raise")
        xvals = np.arange(0, len(subj_ratings)*SAMPLE_RATE, SAMPLE_RATE)
        ax.plot(xvals, subj_ratings, color=color, alpha=.5, lw=1, ls="solid", zorder=1)
    # ax.set_xbound(lower=0)
    # ax.set_ylim(0, 1)
    ax.xaxis.set(major_locator=plt.MultipleLocator(60),
                 minor_locator=plt.MultipleLocator(10),
                 major_formatter=plt.FuncFormatter(c.no_leading_zeros))
    # ax.yaxis.set(major_locator=plt.MultipleLocator(1),
    #              minor_locator=plt.MultipleLocator(.1),
    #              major_formatter=plt.FuncFormatter(c.no_leading_zeros))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if ax.get_subplotspec().is_first_col() and ax.get_subplotspec().is_last_row():
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Emotion rating\nz-score")
        legend = ax.legend(bbox_to_anchor=(0, 1), loc="upper left",
            # title="Rater",
            fontsize=8,
            borderaxespad=0, frameon=False,
            handlelength=1,
            labelspacing=.2,  # vertical space between entries
            handletextpad=.2) # space between legend markers and labels
        # legend._legend_box.align = "left"
plt.savefig(export_fname)
plt.close()