"""
Get correlations for all videos/subjects
and export a csv with 1 correlation per row.

This is for stats and plotting elsewhere.
"""
import os
import pandas as pd
from scipy import stats
import config as c


import_fname = os.path.join(c.DATA_DIR, "derivatives", "empathy.csv")
export_fname = os.path.join(c.DATA_DIR, "derivatives", "empathy-correlations.csv")

# load data
df = pd.read_csv(import_fname)


######## load all the "true" empathy ratings
######## (from actors)

# def load_video_ratings(video_id):
    # actor_id  = video_id.split("id")[1].split("-")[0]
    # actor_nid = video_id.split("vid")[1]
    # actor_basename = f"target_{actor_id}_{actor_nid}_normal.csv"
    # crowd_basename = f"results_{actor_id}_{actor_nid}.csv"
    # actor_filename = os.path.join(c.DATA_DIR, "SENDv1", "ratings", actor_basename)
    # crowd_filename = os.path.join(c.DATA_DIR, "SENDv1", "ratings", crowd_basename)
    # # sometimes the 2 rating files are misaligned by a second or so
    # # so trim them to their last consistent point
    # actor_ratings = pd.read_csv(actor_filename, index_col="time")
    # crowd_ratings = pd.read_csv(crowd_filename, index_col="time")
    # # weird thing in the actor csv where there's a space before rating (like " rating")
    # # actor_ratings.columns = actor_ratings.columns.str.strip()
    # actor_ratings = actor_ratings.rename(columns={" rating": "actor"})
    # crowd_ratings = crowd_ratings.rename(columns={"evaluatorWeightedEstimate": "crowd"})
    # # I *think* actor ratings are normed between 0 and 1
    # ratings = actor_ratings.join(crowd_ratings["crowd"], how="inner")
    # assert not ratings.isnull().any().any()
    # return ratings

def load_video_ratings(video_id):
    actor_id  = video_id.split("id")[1].split("-")[0]
    actor_nid = video_id.split("vid")[1]
    actor_basename = f"target_{actor_id}_{actor_nid}_normal.csv"
    actor_filename = os.path.join(c.DATA_DIR, "SENDv1", "ratings", actor_basename)
    actor_ratings = pd.read_csv(actor_filename)[" rating"].values
    return actor_ratings

# get all unique videos from the experiment
video_list = df["video_id"].unique()

# create a dict with the ratings
true_ratings = { vid: load_video_ratings(vid) for vid in video_list }



############ get correlations for each subject/video combo

# def get_correlation(row):
#     actor, video = row[["actor", "video"]]
#     ratings = get_ratings(actor, video)
#     actor_ratings = ratings.actor
#     crowd_ratings = ratings.crowd
#     actor_ratings = stats.zscore(ratings.actor, nan_policy="raise")
#     crowd_ratings = stats.zscore(ratings.crowd, nan_policy="raise")
#     correlation, _ = stats.pearsonr(actor_ratings, crowd_ratings)
#     return correlation

def get_correlation(ser_):
    vid_id = ser_.index.get_level_values("video_id").unique()[0]
    true_ = true_ratings[vid_id]
    subj_ = ser_.values
    last = min((map(len, [true_, subj_])))
    true_z = stats.zscore(true_[:last], nan_policy="raise")
    subj_z = stats.zscore(subj_[:last], nan_policy="raise")
    r, _ = stats.pearsonr(true_z, subj_z)
    return r

groupby_cols = [ c for c in df if c not in ["time", "rating"] ]

corrs = df.set_index(groupby_cols # set index first so the vals are accessible in the groupby function
    ).groupby(groupby_cols)["rating"].apply(get_correlation
    ).rename("correlation")


# export
corrs.to_csv(export_fname, index=True, encoding="utf-8", na_rep="NA")
