"""Plot the aggregate correlation results
"""
import os
import pandas as pd
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


import_fname = os.path.join(c.DATA_DIR, "derivatives", "empathy-correlations.csv")
export_fname = os.path.join(c.DATA_DIR, "results", "empathy.png")


# load data
df = pd.read_csv(import_fname)

# average within pre and post for each subject
df = df.groupby(["participant_id", "task_condition", "pre_post"]
    )["correlation"].mean(
    ).reset_index()


COLORS = dict(bct="orchid", mw="gainsboro")

fig, ax = plt.subplots(figsize=(3, 3), constrained_layout=True)

sea.barplot(data=df, y="correlation",
    x="pre_post", order=["pre", "post"],
    hue="task_condition", hue_order=["mw", "bct"],
    palette=COLORS, errwidth=1, capsize=.05, errcolor="k")

sea.swarmplot(data=df, y="correlation",
    x="pre_post", order=["pre", "post"],
    hue="task_condition", hue_order=["mw", "bct"],
    dodge=2,
    palette=COLORS, edgecolor="k", linewidth=1)


trim_lead0 = lambda x, pos: f"{x:.2f}"[1:] if 0<abs(x)<1 else f"{x:.2f}"
ax.set_xlabel("")
ax.set_xticks([0, 1])
ax.set_xticklabels(["before\ntask", "after\ntask"])
ax.set_xlim(-.7, 1.7)
ax.set_ylim(0, 1)
ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
             minor_locator=plt.MultipleLocator(.1),
             major_formatter=plt.FuncFormatter(c.no_leading_zeros))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


plt.savefig(export_fname)
plt.close()