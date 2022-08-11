"""
Go from raw jsPsych data to a single
csv file with the empathy rating data.

Resample the raw empathic accuracy task ratings
to match the rate of the SEND dataset (.5 seconds).
Also z-score ratings within each video (after resampling).

IMPORTS
=======
    - individual csv files (1 per subject) from data/source

EXPORTS
=======
    - single csv of all subject data, derivatives/empathy-data.csv
"""
import os
import json
import glob
import numpy as np
import pandas as pd
from scipy import stats

import utils

SAMPLE_RATE = .5 # SEND dataset sample rate in seconds
DEFAULT_RATING = 5 # neutral rating to start each video in the task



# choose which columns to keep (timepoint and rating will be there too!)
KEEP_COLUMNS = ["participant_id", "trial", "video_id", "pre_post", "task_condition"]


fname_glob = os.path.join(utils.Config.data_directory, "source", "*.csv")
import_fnames = sorted(glob.glob(fname_glob))

export_fname = os.path.join(utils.Config.data_directory, "derivatives", "empathy-data.csv")


# load in all subjects
df = pd.concat([ pd.read_csv(fn) for fn in import_fnames ], ignore_index=True)

# # remove pilot subjects
# if "pilot" in utils.Config.data_directory:
#     df = utils.remove_subjects(df, above=utils.Config.first_subject_batch2-1)
# else:
#     df = utils.remove_subjects(df, below=utils.Config.first_subject_batch2)

# rename run_id to participant_id bc it makes way more sense
# (convert it to categorical while we're at it)
df["participant_id"] = pd.Categorical(df["run_id"], ordered=False)

# identify which task was played during the middle for this participant
df["task_condition"] = df["condition"].map(utils.Config.condition_mapping)



# reduce to only the empathic accuracy trials
# (either of these will work)
df = df[ df["trial_type"].eq("empathic-accuracy-response") ].reset_index(drop=True).copy()
# df = df[ df["phase"].eq("empathy-test") ].reset_index(drop=True).copy()

# create a trial column
# which has the unique trial for each participant
df["trial"] = 1 + df.groupby("run_id").run_id.transform(lambda s: range(s.size))

# check whether they did stuff (EMPATHY task stuff)
# Do all trials exist in the file?
assert df["trial"].nunique() == 10, "Participant didn't complete all trials :/"

df.query("participant_id==81")["responses"]
# denote whether the trial was pre or post intervention
df["pre_post"] = df["trial"].apply(lambda x: "pre" if x < 6 else "post")
df["pre_post"] = pd.Categorical(df["pre_post"],
        categories=["pre", "post"], ordered=True)


# extract a meaningful code representing the video of each trial
df["video_id"] =  df["stimulus"].str.split('"'
    ).str[1].str.split("_", 2).str[:2].str.join("-").str.lower()


## The empathic accuracy responses column is a custom
## jspsych thing that outputs a lot of stuff in one cell.
## The responses column has in it a list of dictionaries,
## each with a rating, reaction time, and press.
## The press is uninteresting (left or right press)
## but save the current rating and RT of the press.

# turn the responses column from string to list
df["response_list"] = df["responses"].apply(json.loads)


# Did they respond to all (empathy video) trials?
remove_participants = []
for pid, pid_df in df.groupby("participant_id"):
    n_no_response = pid_df["response_list"].str.len().eq(0).sum()
    if n_no_response > 0:
        if n_no_response > 1:
            remove_participants.append(pid)
            action = "Removing"
        else:
            action = "Keeping"
        print(f"WARNING: participant {pid} did not respond to {n_no_response} empathy task trials. {action} them.")

df = df[ ~df["participant_id"].isin(remove_participants) ]

# break out the response list so each row
# is a press rather than a single trial/video
df = df.explode("response_list", ignore_index=True)

# If there is a null trial, that means the list was
# empty and now there's one NA cell for that trial.
n_null_trials = df["response_list"].isnull().sum()
print(f"Dropping {n_null_trials} null trials.")
df = df.dropna(subset=["response_list"]).reset_index(drop=True)

# break out to new columns for each thing
df["rt"]     = df["response_list"].apply(lambda x: x["rt"])
df["rating"] = df["response_list"].apply(lambda x: x["rating"])
# df["press"]  = df["response_list"].apply(lambda x: x["key"])

# convert milliseconds to seconds
df["rt"] = df["rt"].div(1000)


### resampling section
round_to_point5 = lambda val: round(val * 2) / 2
def resample_ratings(df_):
    # extract just the ratings and RTs
    # with RT/time as index (bc pandas like time as index)
    ser_ = df_.set_index("rt")["rating"].rename_axis("time")
    # add the default starting value to begin the series
    ser_.loc[0] = DEFAULT_RATING
    # convert the index to .5
    ser_.index = ser_.index.map(round_to_point5)
    # average over 2 responses that might be in the same half second
    ser_ = ser_.groupby("time").mean()
    ser_ = ser_.sort_index() # redundant after the groupby
    ## reindex with a sample every second and fill the gaps
    # use the original actor ratings to get the final timepoint
    # (there is also the crowd ratings which occasionally misalign
    #  with the actor files somehow, but I think it's only a second)
    video_id = df_["video_id"].unique()[0]
    actor_id  = video_id.split("-")[0][2:]
    actor_nid = video_id.split("-")[1][3:]
    actor_basename = f"target_{actor_id}_{actor_nid}_normal.csv"
    actor_filename = os.path.join(utils.Config.stim_directory, "SENDv1", "ratings", actor_basename)
    max_time = pd.read_csv(actor_filename)["time"].max()
    # max_time = ser_.index.max()
    resampled_indx = np.arange(0, max_time+SAMPLE_RATE, SAMPLE_RATE)
    ser_ = ser_.reindex(resampled_indx, method="ffill")
    # # get back the other attributes
    # out_df = ser_.to_frame()
    # for col in KEEP_COLUMNS:
    #     assert df_[col].nunique() == 1
    #     out_df[col] = df_[col].unique()[0]
    return ser_


# resample while also reducing to relevant columns
out = df.groupby(KEEP_COLUMNS).apply(resample_ratings)


out.to_csv(export_fname, index=True, encoding="utf-8", na_rep="NA")
