"""Clean the BCT task data.
Go from cognition.run csv format to usable dataframe.

I'm mostly adopting the language of Wong 2018 by
referring to sections of the task as "cycles"
(instead of trials, since the participant determines the length).
A cycle can be:
    - "correct" (right press on breath 9)
    - "miscount" (right press on not 9)
    - "reset" (press spacebar)

Extract the relevant stuff from the jspsych/cognition
output and does some calculations on that.

IMPORTS
=======
    - cleaned task output, derivatives/empathy-data.csv

EXPORTS
=======
    - csv with 1 row for each press, derivatives/bct-data_presses.csv
    - csv with 1 row for each cycle, derivatives/bct-data_cycles.csv
"""
import os
import glob

import numpy as np
import pandas as pd

import helpers

############  handle import/export filenames

fname_glob = os.path.join(helpers.Config.data_directory, "source", "*.csv")
import_fnames = sorted(glob.glob(fname_glob))

export_fname_press = os.path.join(helpers.Config.data_directory, "derivatives", "bct-data_presses.csv")
export_fname_cycle = os.path.join(helpers.Config.data_directory, "derivatives", "bct-data_cycles.csv")


# # reduce to pilot subjects
# if "pilot" in helpers.Config.data_directory:
#     def subj_is_keeper(fn):
#         sub_id = int(os.path.basename(fn).split(".")[0])
#         return sub_id < helpers.Config.first_subject_batch2
# else:
#     def subj_is_keeper(fn):
#         sub_id = int(os.path.basename(fn).split(".")[0])
#         return sub_id >= helpers.Config.first_subject_batch2

# import_fnames = [ fn for fn in import_fnames if subj_is_keeper(fn) ]


############  make some functions that will be used to parse input
#######
####### these all work on a *single subject's* data

def count_breaths(resp):
    """count the participant's subjective breath count
    (ie, according to their button presses)
    """
    global breath_counter, last_response
    if last_response != "arrowdown" and resp == last_response:
        return 99 # mark to count/remove later
    if last_response == "arrowright":
        breath_counter = 0
    if resp == "arrowdown":
        breath_counter += 1
    elif resp == "arrowright":
        breath_counter += 1
    elif resp == "space":
        breath_counter = 0
    last_response = resp
    return breath_counter

def determine_press_accuracy(row):
    if row["bc"] < 9 and row["response"] == "arrowdown":
        return True
    elif row["bc"] == 9 and row["response"] == "arrowright":
        return True
    else:
        return False

def count_cycles(bc):
    """a cycle is a sequence determined by the participant.
    A cycle ends whenever they press right arrow or spacebar
    """
    global cycle_counter
    if bc == 99:
        return np.nan
    elif bc == 1:
        cycle_counter += 1
    return cycle_counter

def determine_cycle_accuracy(df):
    lastrow = df.iloc[-1]
    if lastrow.press_correct:
        return "correct"
    else:
        if lastrow.response == "space":
            return "reset"
        else: # arrowright
            return "miscount"


############  parse input of each subject and stack together

df_list = []
for fn in import_fnames:

    df_ = pd.read_csv(fn)

    # make sure this participant did the BCT
    if df_["condition"].map(helpers.Config.condition_mapping).eq("bct").all():
        ##### handle *one participant's* dataframe
        """need to do a few things
        small --> large
        press --> cycle
        1. each press needs an accuracy label
        2. each cycle needs to be numbered
            - discount double-presses of space and arrowright
        """
        df_ = df_.rename(columns={"run_id":"participant_id"})

        # preprocess the jspsych output
        df_ = df_[df_["phase"]=="bct-test"]
        if df_.size == 0:
            sub_id = os.path.basename(fn).split(".")[0]
            print(f"Skipping participant {sub_id} bc they had no BCT trials (but should have!)")
            continue
        ## what's going on with the last row????
        ## no stimulus, but says it's correct and in the test phase???
        df_ = df_[df_["stimulus"].str.contains(r"\+")]

        df_["rt"] = df_["rt"].astype(float)
        df_["response"] = df_["response"].replace({" ":"space"})

        df_ = df_[["participant_id", "response", "rt"]]

        # generate a breath counter column
        breath_counter = 0
        last_response = None
        df_["bc"] = df_["response"].apply(count_breaths)

        cycle_counter = 0
        df_["cycle"] = df_["bc"].apply(count_cycles)

        # drop the last trial if they didn't finish it
        if df_.iloc[-1]["response"] == "arrowdown":
            df_ = df_[df_["cycle"]<df_["cycle"].max()]

        df_["press_correct"] = df_.apply(determine_press_accuracy, axis=1)

        # add a press counter for the timecourse plot
        df_["pc"] = np.arange(df_.shape[0]) + 1
        # add a cumulative RT for timecourse plot
        df_["rt_sum"] = df_["rt"].cumsum()

        df_list.append(df_)


df_press = pd.concat(df_list, ignore_index=True)
# assert not df_press.isnull().values.any()

# # duplicate_press_indx = ( (df.response.isin(["space","arrowright"]))
# #     & (df.response.shift() == df.response) )
# # n_duplicate_presses = duplicate_press_indx.sum()
# # print(f"{n_duplicate_presses} duplicate presses know that")
# # df = df.loc[~duplicate_press_indx]
# # df = df.reset_index(drop=True)

# drop the repeat press rows (rights and spaces)
df_cycle = df_press.dropna(subset=["cycle"]).reset_index(drop=True)
df_cycle["cycle"] = df_cycle["cycle"].astype(int)

cycle_acc = df_cycle.groupby(["participant_id", "cycle"]
    ).apply(determine_cycle_accuracy
    ).rename("accuracy")
cycle_rt = df_cycle.groupby(["participant_id", "cycle"]
    )["rt"].mean(
    ).rename("rt_mean")
cycle_rt_std = df_cycle.groupby(["participant_id", "cycle"]
    )["rt"].std(
    ).rename("rt_std")
cycle_bc = df_cycle.groupby(["participant_id", "cycle"]
    # )["bc"].apply(lambda s: s.max()+1 if 0 in s.tolist() else s.max()
    ).apply(lambda df: df.iloc[-2].bc+1 if df.iloc[-1].response=="space" else df.iloc[-1].bc
    ).rename("final_breath")

# cycle_df = cycle_acc.to_frame().join(cycle_bc).sort_index()
cycle_df = pd.concat([cycle_bc, cycle_acc, cycle_rt, cycle_rt_std], axis=1)
# cycle_acc["acc2"] = cycle_acc["acc1"].str.split("-").str[0]
# cycle_acc["acc3"] = (cycle_acc["acc1"] == "correct")

assert not cycle_df.isnull().values.any()
# cycle_acc = cycle_acc.reset_index(drop=False)


# export
df_press.round(1).to_csv(export_fname_press, index=False, na_rep="NA")
cycle_df.round(1).to_csv(export_fname_cycle, index=True)
