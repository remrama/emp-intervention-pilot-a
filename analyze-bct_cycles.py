"""
some stuff about press frequency ("breathing rate")
- press frequency, aka "breathing rate" mean and variability

for now just try and predict accuracy on each cycle
with the press/breath rate
"""
import os
import pandas as pd

import seaborn as sea
import matplotlib.pyplot as plt

import helpers

helpers.load_matplotlib_settings()


import_fname = os.path.join(helpers.Config.data_directory, "derivatives", "bct-data_cycles.csv")
export_fname = os.path.join(helpers.Config.data_directory, "results", "bct-respiration.png")


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
# helpers.save_hires_figs(export_fname)
plt.close()
