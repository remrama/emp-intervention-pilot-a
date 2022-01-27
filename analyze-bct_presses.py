"""Draw a big descriptive plot
showing *every press* from every participant.

and another descriptive plot showing timecourse (for troubleshooting mostly)
"""
import os
import numpy as np
import pandas as pd

import colorcet as cc
import seaborn as sea
import matplotlib.pyplot as plt

import helpers

helpers.load_matplotlib_settings()


import_fname = os.path.join(helpers.Config.data_directory, "derivatives", "bct-data_presses.csv")

export_fname1 = os.path.join(helpers.Config.data_directory, "results", "bct-respiration.png")
export_fname2 = os.path.join(helpers.Config.data_directory, "results", "bct-allpresses.png")


df = pd.read_csv(import_fname)

# convert RTs to seconds
df["rt"] /= 1000


print("still unclear about handling nan cycles from repeated presses")
# assert not df.isnull().values.any()
df.dropna(inplace=True)



"""========================================================
plot the timecourse of all presses all subjects
"""

cmap = cc.cm.CET_R3

_, ax = plt.subplots(figsize=(5,3), constrained_layout=True)
sea.lineplot(data=df, x="pc", y="rt",
    hue="participant_id",
    palette=cmap,
    # units="participant_id", estimator=None
    ax=ax)

ax.set_xbound(lower=0)
ax.set_ybound(lower=0)
ax.set_xlabel("Cumulative press count")
ax.set_ylabel("Time between presses (s)")
ax.xaxis.set(major_locator=plt.MultipleLocator(50),
    minor_locator=plt.MultipleLocator(10))
# ax.yaxis.set(major_locator=plt.MultipleLocator(1),
#     minor_locator=plt.MultipleLocator(.2))

plt.savefig(export_fname1)
plt.close()



"""========================================================
plot a "map" of all presses/accuracy/rt/responses
for each participant individually

- each participant gets their own "row"
- each press response (space/down/right) gets its own shape
    - also size is impacted, spaces and rights are bigger bc they end "cycles"
- each press accuracy (correct/miscount/reset) gets its own color
"""

# flip to a dataframe with RTs in columns and press count as index.
# we need, for each participant and press,
# the RT, the response, and the press accuracy
df_ = df.pivot(
    columns="participant_id",
    index="pc",
    values=["rt", "press_correct", "response"],
    # values=["rt_sum","press_correct"],
    ).sort_index(axis="index").sort_index(axis="columns"
)

df_["rt"] = df_["rt"].cumsum()


n_participants = df["participant_id"].nunique()


RESPONSE_MARKERS = {
    "space": "s",
    "arrowdown": "v",
    "arrowright": "o",
}

RESPONSE_SIZES = {
    "space": 10,
    "arrowright": 30,
    "arrowdown": 2,
}

ACC_PALETTE = {
    "correct" : "forestgreen",
    "incorrect" : "indianred",
    "space" : "gray",
}

ALPHA = .7

# open plot
_, ax = plt.subplots(figsize=(6.5,.5*n_participants),
    gridspec_kw=dict(top=.7, bottom=.25, left=.1, right=.9))

for i, (pp, pdf) in enumerate(df.groupby("participant_id")):
    pdf["cumrt"] = pdf["rt"].cumsum()
    for (resp, correct), _pdf in pdf.groupby(["response", "press_correct"]):
        marker = RESPONSE_MARKERS[resp]
        size = RESPONSE_SIZES[resp]
        if resp == "space":
            color = ACC_PALETTE[resp]
        else:
            color = ACC_PALETTE["correct"] if correct else ACC_PALETTE["incorrect"]
        xvals = _pdf["cumrt"].values
        yvals = np.repeat(i+1, xvals.size)
        ax.scatter(xvals, yvals,
            s=size, marker=marker, c=color,
            alpha=ALPHA, linewidths=0)

EXP_LENGTH = 10 # minutes
def sec2min_formatter(x, pos=None):
    assert x/60 == x//60
    return int(x/60)
ax.set_xlim(0, EXP_LENGTH*60)
ax.xaxis.set(major_locator=plt.MultipleLocator(60),
    major_formatter=sec2min_formatter)
# ax.yaxis.set(major_locator=plt.MultipleLocator(1))
ax.set_yticks(range(1, n_participants+1))
ax.set_yticklabels(df["participant_id"].unique())
ax.set_xlabel("Experiment time (minutes)", fontsize=10)
ax.set_ylabel("Participant", fontsize=10)
ax.set_ylim(.5, n_participants+.5)
ax.invert_yaxis()

## need 2 legends, one for the button press type and one for accuracy

LEGENDS_ARGS = {
    "fontsize" : 8,
    "frameon" : False,
    # "borderaxespad" : -.5,
    "labelspacing" : .2, # rowspacing, vertical space bewteen legend entries
    # "handletextpad" : -.2 # space between legend marker and label
    # # "columnspacing"=.5,
}


button_legend_elements = [ plt.matplotlib.lines.Line2D([0], [0],
        label=x, marker=m, markersize=6, color="white",
        markerfacecolor="white", markeredgecolor="black")
    for x, m in RESPONSE_MARKERS.items() ]
legend1 = ax.legend(handles=button_legend_elements,
    loc="lower left", bbox_to_anchor=(0, 1),
    title="button press", **LEGENDS_ARGS)

accuracy_legend_elements = [ plt.matplotlib.patches.Patch(
        label= "correct" if x=="correct" else "incorrect",
        facecolor=c, edgecolor="white")
    for x, c in ACC_PALETTE.items() ]
legend2 = ax.legend(handles=accuracy_legend_elements,
    loc="lower left", bbox_to_anchor=(.2, 1),
    title="accuracy", **LEGENDS_ARGS)

ax.add_artist(legend1)
ax.add_artist(legend2)


plt.savefig(export_fname2)
plt.close()
