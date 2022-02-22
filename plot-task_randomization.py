"""visualize condition randomization
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import utils

utils.load_matplotlib_settings()
subj_palette = utils.load_subject_palette()

import_fname = os.path.join(utils.Config.data_directory, "derivatives", "empathy-correlations.csv")
export_fname = os.path.join(utils.Config.data_directory, "results", "emp-videosets.png")

df = pd.read_csv(import_fname)

FIGSIZE = (2, 2)
fig, ax = plt.subplots(figsize=FIGSIZE)


counts = df.query("pre_post=='pre'").query("trial==1"
    ).groupby(["task_condition", "video_id"]).size(
    ).rename("count").reset_index("video_id"
    ).replace(dict(video_id={"id113-vid3": "Set A", "id116-vid6": "Set B"}))


xvals = [0, 1, 3, 4]
xticks = [.5, 3.5]
xlim = (-1.5, 5.5)
ymax = 10
xticklabels = ["BCT", "REST"]
colors = ["white", "gainsboro", "white", "gainsboro"]
yvals = counts["count"].values

ax.bar(xvals, yvals, color=colors, width=1, edgecolor="black", linewidth=1)

ax.set_ylabel(r"$n$ participants")
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(*xlim)
ax.set_ybound(upper=ymax)

legend_handles = [ plt.matplotlib.patches.Patch(
        label=l, facecolor=c, linewidth=.5, edgecolor="black")
    for c, l in zip(colors, ["Set A", "Set B"]) ]
legend = ax.legend(handles=legend_handles,
    loc="upper center",
    title="First video set")


plt.savefig(export_fname)
utils.save_hires_copies(export_fname)
plt.close()