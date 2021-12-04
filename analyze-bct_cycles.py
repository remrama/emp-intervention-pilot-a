"""
some stuff about press frequency ("breathing rate")
- press frequency, aka "breathing rate" mean and variability

for now just try and predict accuracy on each cycle
with the press/breath rate
"""
import os
import numpy as np
import pandas as pd

import config as c

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

import_fname = os.path.join(c.DATA_DIR, "derivatives", "bct-cycles.csv")
export_fname = os.path.join(c.DATA_DIR, "results", "bct-respiration.png")


df = pd.read_csv(import_fname)

df["participant_id"] = pd.Categorical(df["participant_id"], ordered=True)

df["correct"] = df["accuracy"]=="correct"

# # temp remove fake outlier
# df = df[df["rt_mean"]<30000]

plot_df = df.melt(value_vars=["rt_mean", "rt_std"],
    id_vars=["participant_id", "correct"],
    var_name="rt_measure", value_name="rt")

g = sea.lmplot(data=plot_df, x="rt", y="correct",
    col="rt_measure", hue="rt_measure",
    # row="participant_id",
    logistic=True, height=2, aspect=1)



plt.savefig(export_fname)
plt.close()
