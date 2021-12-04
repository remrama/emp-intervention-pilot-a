"""plot descriptives of the SEND dataset
(for purpose of figuring out how to subset)

Exports multiple figures and 1 csv with features for each video.
The csv is what's used for the figures. Could probably
move to separate scripts in the future.
"""
import os
import glob
import numpy as np
import pandas as pd
import config as c

from scipy import stats

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


EXPORT_DIR = os.path.join(c.DATA_DIR, "derivatives")
SEND_DIR = os.path.join(c.DATA_DIR, "SENDv1")
# send as in video dataset send

# get a list of all the SEND video filenames
video_fname_glob = os.path.join(SEND_DIR, "videos", "*.mp4")
video_fnames = sorted(glob.glob(video_fname_glob))

# other filenames can be compiled when needed
def feature_fname(actor, video, feature_type):
    if feature_type == "acoustic":
        dirname = "acoustic-egemaps"
        basename = f"ID{actor}_vid{video}_acousticFeatures.csv"
    elif feature_type == "emotion":
        # this one is annoying bc the basename endings are inconsistent
        dirname = "emotient"
        basename_glob = f"ID{actor}_vid{video}_*.txt"
        fullpath_glob = os.path.join(SEND_DIR, "features", dirname, basename_glob)
        fname_opts = glob.glob(fullpath_glob)
        assert len(fname_opts) == 1
        basename = os.path.basename(fname_opts[0])
    elif feature_type == "linguistic":
        dirname = "linguistic"
        basename = f"ID{actor}_vid{video}_aligned.tsv"
    return os.path.join(SEND_DIR, "features", dirname, basename)

def rating_fname(actor, video, rating_type):
    if rating_type == "actor":
        basename = f"target_{actor}_{video}_normal.csv"
    elif rating_type == "crowd":
        basename = f"results_{actor}_{video}.csv"
    return os.path.join(SEND_DIR, "ratings", basename)



# turn it into a dataframe to build on
video_basenames = map(os.path.basename, video_fnames)
df = pd.DataFrame(video_basenames, columns=["filename"])

# def parse_bname(basename):
#     rater_id, video_id = basename.split("_")[:2]
#     rater_num = int("".join([ char for char in rater_id if char.isdigit() ]))
#     video_num = int("".join([ char for char in video_id if char.isdigit() ]))
#     return rater_num, video_num
# df["rater"], df["video"] = zip(*df["filename"].apply(parse_bname))

# extract info from filenames
df["actor"] = df["filename"].str.split("_").str[0].str[2:].astype(int)
df["video"] = df["filename"].str.split("_").str[1].str[3:].astype(int)


def get_ratings(actor, video):
    # sometimes the 2 rating files are misaligned by a second or so
    # so trim them to their last consistent point
    actor_ratings = pd.read_csv(rating_fname(actor, video, "actor"), index_col="time")
    crowd_ratings = pd.read_csv(rating_fname(actor, video, "crowd"), index_col="time")
    # weird thing in the actor csv where there's a space before rating (like " rating")
    # actor_ratings.columns = actor_ratings.columns.str.strip()
    actor_ratings = actor_ratings.rename(columns={" rating": "actor"})
    crowd_ratings = crowd_ratings.rename(columns={"evaluatorWeightedEstimate": "crowd"})
    crowd_ratings = crowd_ratings.rename(columns={"SDofEWE": "crowd_variability"})
    # I *think* actor ratings are normed between 0 and 1
    ratings = actor_ratings.join(crowd_ratings[["crowd","crowd_variability"]], how="inner")
    assert not ratings.isnull().any().any()
    return ratings


def get_correlation(row):
    actor, video = row[["actor", "video"]]
    ratings = get_ratings(actor, video)
    actor_ratings = ratings.actor
    crowd_ratings = ratings.crowd
    actor_ratings = stats.zscore(ratings.actor, nan_policy="raise")
    crowd_ratings = stats.zscore(ratings.crowd, nan_policy="raise")
    correlation, _ = stats.pearsonr(actor_ratings, crowd_ratings)
    return correlation

def get_crowd_variability(row):
    actor, video = row[["actor", "video"]]
    ratings = get_ratings(actor, video)
    return ratings.crowd_variability.mean()

df["actor2crowd_r"] = df.apply(get_correlation, axis=1)

df["video_length"] = df.apply(lambda row: get_ratings(*row[["actor", "video"]]).index.max()/60, axis=1)

df["crowd_variability"] = df.apply(get_crowd_variability, axis=1)


### plot 
g = sea.jointplot(data=df, x="actor2crowd_r", y="crowd_variability")

export_fname = os.path.join(EXPORT_DIR, "SEND-crowd_variability.png")
plt.savefig(export_fname)
plt.close()





# get the facial emotion scores

## build a dataframe with emotion scores and then merge it
emo_columns = [ f"{e}Evidence" for e in 
    ["anger", "contempt", "disgust", "joy", "fear", "sadness", "surprise"] ]

def get_face_emotions(row):
    # return a series so build this separately
    actor, video = row[["actor", "video"]]
    emo = pd.read_csv(feature_fname(actor, video, "emotion"))
    emo = emo[emo_columns]
    emo.columns = emo.columns.str.split("Evidence").str[0]
    emo.columns = emo.columns.map(lambda x: "face-"+x)
    mean_series = emo.mean()
    return mean_series


df = pd.concat([df, df.apply(get_face_emotions, axis=1)], axis=1)


# # this will catch target/actor AND observer/crowdsourced ratings
# rating_fname_glob = os.path.join(SEND_DIR, "*", "*", "*.csv")
# rating_fnames = sorted(glob.glob(rating_fname_glob))
language_features = [
    "SumLIWCNeg", "SumLIWCPos",
    "MeanValence_w", "MeanArousal_w",
    # "MeanValence_a", "MeanArousal_a",
]
def get_linguistic_means(row):
    actor, video = row[["actor", "video"]]
    lang = pd.read_csv(feature_fname(actor, video, "linguistic"), sep="\t")
    lang = lang[language_features]
    lang.columns = lang.columns.map(lambda x: "lang-"+x)
    mean_series = lang.mean(skipna=True)
    return mean_series

df = pd.concat([df, df.apply(get_linguistic_means, axis=1)], axis=1)

glove_cols = [ f"glove{i}" for i in range(300) ]
def get_glove_mean(row):
    actor, video = row[["actor", "video"]]
    lang = pd.read_csv(feature_fname(actor, video, "linguistic"), sep="\t")
    return lang[glove_cols].mean()

df = pd.concat([df, df.apply(get_glove_mean, axis=1)], axis=1)


# plot a distribution of the correlations
_, (ax1, ax2) = plt.subplots(ncols=2, figsize=(5,3),
    sharey=True, constrained_layout=True)
HIST_ARGS = {
    "color": "gray",
    "stat": "count",
    "cumulative": False,
    "element": "bars",
    "fill": True,
    "kde": False,
}
bins1 = np.linspace(-1, 1, 21)
bins2 = np.linspace(0, 5, 21)
sea.histplot(ax=ax1, data=df, x="actor2crowd_r", bins=bins1, **HIST_ARGS)
sea.histplot(ax=ax2, data=df, x="video_length", bins=bins2, **HIST_ARGS)
ax1.set_xlabel("Correlation between\nactor and crowdsource ratings")
ax2.set_xlabel("Video length (minutes)")
ax1.set_xlim(-1, 1)
ax2.set_xlim(0, 5)
ax1.xaxis.set(major_locator=plt.MultipleLocator(1),
              minor_locator=plt.FixedLocator(bins1))
ax2.xaxis.set(major_locator=plt.MultipleLocator(1),
              minor_locator=plt.FixedLocator(bins2))

export_fname = os.path.join(EXPORT_DIR, "SEND-correlations.png")
plt.savefig(export_fname)
plt.close()



SCATTER_ARGS = {
    "s" : 8,
    "color": "w",
    "edgecolor": "k",
    "linewidth" : .5,
    "clip_on" : False
}
PAIRPLOT_ARGS = {
    "kind" : "reg",
    "diag_kind" : "hist",
    "height" : 1,
    "aspect" : 1,
    "corner" : True,
    # "plot_kws" : dict(cmap="mako"),
    "plot_kws" : dict(scatter_kws=SCATTER_ARGS),
    "diag_kws" : dict(color="black"),
    "grid_kws" : dict(diag_sharey=False, despine=True, layout_pad=.5),
}
plot_columns = [ c for c in df if c.startswith("face-") ]
g = sea.pairplot(data=df, vars=plot_columns, **PAIRPLOT_ARGS)

maxlim = 6
g.set(xlim=(-maxlim, maxlim), ylim=(-maxlim, maxlim))
for ax in g.axes.flat:
    if ax is not None:
        if ax.get_subplotspec().is_first_col() and not ax.get_subplotspec().is_first_row():
            ax.set_ylabel(ax.get_ylabel().split("-")[1])
        if ax.get_subplotspec().is_last_row():
            ax.set_xlabel(ax.get_xlabel().split("-")[1])

g.fig.suptitle("Facial expressions conveyed in videos")


export_fname = os.path.join(EXPORT_DIR, "SEND-facial_expressions.png")
plt.savefig(export_fname)
plt.close()



plot_columns = [ c for c in df if c.startswith("lang-") ]
g = sea.pairplot(data=df, vars=plot_columns, **PAIRPLOT_ARGS)

RENAMINGS = {
    "lang-SumLIWCNeg" : "negative\nword count",
    "lang-SumLIWCPos" : "positive\nword count",
    "lang-MeanValence_w" : "language\nvalence",
    "lang-MeanArousal_w" : "language\narousal",
}
for ax in g.axes.flat:
    if ax is not None:
        if ax.get_subplotspec().is_first_col() and not ax.get_subplotspec().is_first_row():
            ax.set_ylabel(RENAMINGS[ax.get_ylabel()])
        if ax.get_subplotspec().is_last_row():
            ax.set_xlabel(RENAMINGS[ax.get_xlabel()])


g.fig.suptitle("Language use in videos")
g.tight_layout()

export_fname = os.path.join(EXPORT_DIR, "SEND-language.png")
plt.savefig(export_fname)
plt.close()




### plot glove

from sklearn import decomposition

X = df[glove_cols].values

pca = decomposition.PCA(n_components=2)
X_pca = pca.fit_transform(X)

fig, ax = plt.subplots(figsize=(4,4), constrained_layout=True)
fig.suptitle("Videos in semantic language space")
ax.set_xlabel("GLoVE word embedding dimension 1")
ax.set_ylabel("GLoVE word embedding dimension 2")
ax.scatter(X_pca[:,0], X_pca[:,1],
    s=20, color="blue", edgecolor="k",
    linewidth=.5, alpha=.8)

export_fname = os.path.join(EXPORT_DIR, "SEND-embeddings.png")
plt.savefig(export_fname)
plt.close()


## for all videos
fig, ax = plt.subplots(figsize=(5,3), constrained_layout=True)
fig.suptitle("Sample video actor vs crowd timecourses")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Valence rating\n(z-scored)")
for i, row in df.sample(4).reset_index(drop=True).iterrows():
    actor, video = row[["actor", "video"]]
    ratings = get_ratings(actor, video)
    actor_ratings = ratings.actor
    crowd_ratings = ratings.crowd
    actor_ratings = stats.zscore(actor_ratings, nan_policy="raise")
    crowd_ratings = stats.zscore(crowd_ratings, nan_policy="raise")
    correlation, _ = stats.pearsonr(actor_ratings, crowd_ratings)
    ax.plot(actor_ratings, alpha=.5, color=plt.cm.tab10(i), lw=2, ls="-")
    ax.plot(crowd_ratings, alpha=.5, color=plt.cm.tab10(i), lw=2, ls="--")

ax.set_ylim(-6, 6)
ax.yaxis.set(major_locator=plt.MultipleLocator(5),
             minor_locator=plt.MultipleLocator(1))



export_fname = os.path.join(EXPORT_DIR, "SEND-sample_tcourses.png")
plt.savefig(export_fname)
plt.close()





export_fname = os.path.join(EXPORT_DIR, "SEND-video_stats.csv")
df.to_csv(export_fname, index=False)