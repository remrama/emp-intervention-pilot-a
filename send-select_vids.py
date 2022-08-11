"""
generate matched video sets based on apriori criteria
- 3 groups of 5

1. restrict based on correlation between actor and crowd
xxxx ---- 2. restrict based on variation in crowd ---- xxxx
3. only allow vids between 1:45 and 2:15
4. don't allow multiple videos of a single actor

Outputs a plot that has text on it to choose 3 groups from.
First group starts with vid 1
Second group starts with vid 2
Third group starts with vid 3
For each group skip every 3 videos.
"""
import os
import numpy as np
import pandas as pd

from scipy.stats import zscore
from sklearn import metrics

import utils

import seaborn as sea
import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "SEND-video_stats.csv")
export_fname = os.path.join(utils.Config.data_directory, "results", "SEND-final_videos.png")


df = pd.read_csv(import_fname)

# get rid of some columns just to clean up
df = df[["actor", "video", "actor2crowd_r", "video_length", "crowd_variability"]]

df["z_actor2crowd_r"] = zscore(df["actor2crowd_r"].values)
df["z_crowd_variability"] = zscore(df["crowd_variability"].values)


CORR_PCTILE = .75
VAR_PCTILE = .75
correlation_cutoff = df.actor2crowd_r.quantile(CORR_PCTILE)
crowdvar_cutoff = df.crowd_variability.quantile(VAR_PCTILE)
z_correlation_cutoff = df.z_actor2crowd_r.quantile(CORR_PCTILE)
z_crowdvar_cutoff = df.z_crowd_variability.quantile(VAR_PCTILE)

# get a distance and make cutoff
center = np.array([[z_correlation_cutoff, z_crowdvar_cutoff]])
locations = df[["z_actor2crowd_r","z_crowd_variability"]].values

df["distance"] = metrics.euclidean_distances(locations, center)
# def distance(p1, p2):
#     return math.hypot(p2[0]-p1[0], p2[1]-p1[1])
#     # return np.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
# df["distance"] = [ distance(l, center.ravel()) for l in locations ]


# take the closest points but ignore duplicates
used_actors = []
N_VIDEOS = 15
df = df.sort_values("distance", ignore_index=True)
def check_passing(row):
    actor, length = row[["actor", "video_length"]]
    if length < 1.75 or length > 2.25:
        return False
    elif actor in used_actors:
        return False
    elif len(used_actors) >= N_VIDEOS:
        return False
    else:
        used_actors.append(actor)
        return True
df["selected"] = df.apply(check_passing, axis=1)

# cutoff = df["distance"].sort_values(ignore_index=True)[N_VIDEOS-1]
# df["selected"] = df["distance"] <= cutoff

# df = df[df["distance"]<2000]
g = sea.JointGrid(data=df, x="actor2crowd_r", y="crowd_variability")
# g.plot(sea.scatterplot, sea.histplot, alpha=.7, edgecolor=".2", linewidth=.5)
# g.plot_marginals(sea.histplot, kde=True)
g.plot_joint(sea.scatterplot, hue=df["selected"],
    palette={True: "forestgreen", False: "gainsboro"},
    alpha=.7, edgecolor=".2", linewidth=.5)
g.refline(x=correlation_cutoff, y=crowdvar_cutoff)
g.plot_marginals(sea.histplot, color="white")
g.set_axis_labels("Correlation between actor and crowd valence ratings",
    "Variability of crowds valence ratings")

corr_txt = str(int(CORR_PCTILE*100)) + "th percentile "
g.ax_joint.text(correlation_cutoff, .9, corr_txt, ha="right",
    transform=g.ax_joint.get_xaxis_transform())
var_txt = " " + str(int(VAR_PCTILE*100)) + "th percentile"
g.ax_joint.text(.05, crowdvar_cutoff, var_txt, va="bottom",
    rotation=90, transform=g.ax_joint.get_yaxis_transform())

selected_videos = df.loc[df.selected, ["actor", "video", "video_length"]]
selected_videos = selected_videos.sort_values(["video_length", "actor", "video"]
    ).reset_index(drop=True)

txt = "SELECTED VIDEOS\n" + selected_videos.round(1).to_string(index=False)
g.ax_joint.text(.25, .9, txt, transform=g.ax_joint.transAxes,
    ha="left", va="top")


# # sea.histplot(x=x, fill=False, linewidth=2, ax=g.ax_marg_x)
# # sea.kdeplot(y=y, linewidth=2, ax=g.ax_marg_y)
# # g.plot(sea.regplot, sea.boxplot)

# g = sea.jointplot(data=df, x="actor2crowd_r", y="crowd_variability")
# g = sns.jointplot(data=penguins, x="bill_length_mm", y="bill_depth_mm")
# g.plot_joint(sns.kdeplot, color="r", zorder=0, levels=6)
# g.plot_marginals(sns.rugplot, color="r", height=-.15, clip_on=False)

plt.savefig(export_fname)
plt.close()

