"""Going from Reaction Time (between presses) to Respiration Rate.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import utils

utils.load_matplotlib_settings()
subj_palette = utils.load_subject_palette()


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "bct-data_presses.csv")
export_fname = os.path.join(utils.Config.data_directory, "results", "bct-rt2rr.png")


df = pd.read_csv(import_fname)


# Flip data for easier access while plotting.
table = df.pivot(index="pc", columns="participant_id", values="rt")
table = table.div(1000) # convert RTs to seconds

# Plotting parameters.
FIGSIZE = (3, 4)
PLOT_KWARGS = dict(linewidth=.5, alpha=1)

# The ylabels will be used to decide what data to plot.
AXIS_PARAMS = [
    {
        "ylabel": "Reaction time\n(seconds)",
        "ymax": 30,
        "ymajorloc": 5,
    },
    {
        "ylabel": "smoothed\n" + "Reaction time\n(seconds)",
        "ymax": 10,
        "ymajorloc": 2,
    },
    {
        "ylabel": "smoothed\n" + r"$\mathrm{Respiration\ rate,\ }f_{R}$" + "\n(breaths per minute)",
        "ymax": 80,
        "ymajorloc": 20,
    },
]


colors = [ subj_palette[s] if s in subj_palette else "gray" for s in table.columns ]
xvals = table.index.values

fig, axes = plt.subplots(nrows=3, figsize=FIGSIZE, sharex=True)

for ax, axdict in zip(axes, AXIS_PARAMS):
    ax.set_prop_cycle(plt.cycler("color", colors))

    if "Respiration" in axdict["ylabel"]:
        data = table.rolling(10).mean().rdiv(60).values
    elif "smoothed" in axdict["ylabel"]:
        data = table.rolling(10).mean().values
    else:
        data = table.values

    ax.plot(xvals, data, **PLOT_KWARGS)
    ax.set_ylabel(axdict["ylabel"])
    ax.set_ylim(0, axdict["ymax"])
    ax.yaxis.set(major_locator=plt.MultipleLocator(axdict["ymajorloc"]))

    ax.tick_params(which="both", top=False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_position(("outward", 5))
    ax.spines["right"].set_position(("outward", 5))
    ax.spines["bottom"].set_position(("outward", 5))
    ax.grid(axis="y", clip_on=False)

ax.set_xbound(lower=0)
ax.set_xlabel("Press count")
ax.xaxis.set(major_locator=plt.MultipleLocator(100),
    minor_locator=plt.MultipleLocator(20))

fig.align_ylabels(axes)


plt.savefig(export_fname)
utils.save_hires_copies(export_fname)
plt.close()
