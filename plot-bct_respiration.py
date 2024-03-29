"""Main respiration rate plot
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.pyplot as plt
import utils

utils.load_matplotlib_settings()
subj_palette = utils.load_subject_palette()


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "bct-data_presses.csv")
export_plot_fname = os.path.join(utils.Config.data_directory, "results", "bct-respiration.png")
export_table_fname = export_plot_fname.replace(".png", ".csv")


df = pd.read_csv(import_fname)


###### Wrangle a table that has respiration rate over time.
######
###### First get a table that is binned by seconds.
###### It should have a cell for each subject and second
###### and a count of how many presses occured that second.
###### (It should really always be 1 or NA, except sometimes
###### a subject will speed-press so there might be 2 in a second.)
######
###### Then convert the press rate to respiration rate and smooth it.

# Convert cumulative press time to timedeltas.
df["rt_sum_td"] = pd.to_timedelta(df["rt_sum"], unit="milliseconds")

# Create a timedelta index that nicely bins time into single seconds
# and use it to bin the cumulative press data into timedeltas.
seconds_index = pd.timedelta_range(start="0 seconds", end="10 minutes", freq="1S")
cuts = pd.cut(df["rt_sum_td"], bins=seconds_index, labels=False)
df["rt_sum_tdbin"] = pd.to_timedelta(cuts, unit="seconds")

# Pivot to a table storing number of pressed per second in each cell.
press_table = df.groupby(["participant_id", "rt_sum_tdbin"]).size(
    ).unstack("rt_sum_tdbin").reindex(columns=seconds_index)

# Can't fillna because I want the LAST press to have NAs after it.
# But I want earlier NAs to be zeros because it makes rolling a 60
# second window better because then I can require 60 valid timepoints.
# Instead I'll just cut off the first/last 60 seconds.
# (Would like to solve this, see issue in comments below.)

# Calculate a smoothed respiration rate within a sliding 1-minute window.
rr_table = press_table.rolling(window="60S", axis=1,
        center=True, min_periods=1, closed="both", win_type=None,
    ).sum()
    # ).dropna(axis=1 # to drop the column tails without enough data'
    #     # could interpolate or fillna them instead
    # ).astype(int)

# Cut off the tails because they aren't valid without 60 timepoints.
# Respiration rate is calculated as a sum over the minute, so early
# and late timepoints are summing across less than a minute.
# There's a solution using fillna but I can't get it so this works.
# (Although it is NOT okay for subjects that stop early, as they'll
# have a trailing off summation when they start to stop in the middle.)
rr_table = rr_table.iloc[:, 60:-60].copy()

# Gaussian smoothing over respiration rate.
rr_table = rr_table.rolling(60, axis=1,
        # center=True, min_periods=1, win_type="gaussian", closed="both",
        center=True, min_periods=1, closed="both",
    # ).mean(std=3)
    ).mean()


## That's the individual subject data.

## Now get the summary stats for the group.

# Averaging across timepoints to get respiration rate
# descriptive stats for each *participant*.
rr_subj_descriptives = rr_table.T.describe().T.round(3)

# Add a slope that looks at constant change in RR over time.
rr_subj_descriptives["slope"] = rr_table.apply(lambda s:
        stats.linregress(range(s.dropna().values.size), s.dropna().values)[0],
    axis=1).round(6)



# Export this
rr_subj_descriptives.to_csv(export_table_fname, index=True)



# Averaging across participants to get respiration rate
# descriptive stats for each *timepoint*.
# Spend some extra time here to get proper
# bootstrapped confidence intervals.
mean = rr_table.mean(axis=0).to_frame("mean")
ci = rr_table.apply(lambda s:
        stats.bootstrap((s.values,), np.nanmean,
            n_resamples=10000, method="BCa"
        ).confidence_interval
    ).rename(index={0:"cilo", 1:"cihi"}).T
rr_time_descriptives = mean.join(ci)

# Gaussian smoothing over *group* respiration rate.
rr_time_descriptives = rr_time_descriptives.rolling(60,
        win_type="gaussian", center=True, min_periods=1, closed="both",
    ).mean(std=3)



############## Plot.

FIGSIZE = (3, 2)
PLOT_KWARGS = dict(linewidth=.5, alpha=1)
FILL_BETWEEN_KWARGS = dict(color="silver", linewidth=0, alpha=1)
TEXT_KWARGS = dict(color="gainsboro", ha="left", va="bottom", zorder=0)

# Set xvalues in minutes.
xvals = [ x.seconds/60 for x in rr_table.columns.to_pytimedelta() ]
colors = [ subj_palette[s] if s in subj_palette else "gray" for s in rr_table.index ]

fig, axes = plt.subplots(nrows=2, figsize=FIGSIZE,
    sharex=True, gridspec_kw=dict(height_ratios=[1, 2]))

for i, ax in enumerate(axes):

    if i == 0: # group data
        ax.plot(xvals, "mean", data=rr_time_descriptives,
            color="black", **PLOT_KWARGS)
        ax.fill_between(xvals, "cilo", "cihi", data=rr_time_descriptives,
            **FILL_BETWEEN_KWARGS)
        ylabel = r"$\bar{f_{R}}$"
        ymax = 40
        ymajorloc = 20

    else: # individual subject data
        yvals = rr_table.T.values
        ax.set_prop_cycle(plt.cycler("color", colors))
        ax.plot(xvals, yvals, **PLOT_KWARGS)
        ylabel = r"$\mathrm{Respiration\ rate,\ }f_{R}$"
        ymax = 80
        ymajorloc = 20

    ax.set_ylabel(ylabel)
    ax.set_ylim(0, ymax)
    ax.yaxis.set(major_locator=plt.MultipleLocator(ymajorloc))

    # ax.grid(axis="y", clip_on=False)
    # for side, spine in ax.spines.items():
    #     spine.set_position(("outward", 5))

ax.xaxis.set(major_locator=plt.MultipleLocator(1))
ax.set_xlabel("Time during Breath Counting Task\n(minutes)")
ax.set_xlim(0, 10)

# Mark respiration rate norms.
ax.axhspan(12, 20, color=TEXT_KWARGS["color"])
ax.text(.1, 20, "Rest", **TEXT_KWARGS)
ax.text(.1, 40, "Low exercise", **TEXT_KWARGS)
ax.text(.1, 60, "High exercise", **TEXT_KWARGS)
# ax = ax.secondary_yaxis("right")
# ax.set_yticks([15, 40, 60])
# ax.set_yticklabels(["Resting", "Low exercise", "High exercise"])
# ax.tick_params(color="gainsboro", labelcolor="gainsboro")

fig.align_ylabels(axes)



plt.savefig(export_plot_fname)
utils.save_hires_copies(export_plot_fname)
plt.close()