"""Draw a big descriptive plot
showing *every press* from every participant.

and another descriptive plot showing timecourse (for troubleshooting mostly)
"""
import os
import numpy as np
import pandas as pd
import pingouin as pg
from scipy import stats

import colorcet as cc
import seaborn as sea
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import utils

utils.load_matplotlib_settings()


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "bct-data_presses.csv")



df = pd.read_csv(import_fname)

# convert RTs to seconds
df["rt"] /= 1000


print("still unclear about handling nan cycles from repeated presses")
# assert not df.isnull().values.any()
df.dropna(inplace=True)



"""========================================================
plot the timecourse of all presses all subjects
"""

colormap = cc.cm.CET_R3.copy()

ALPHA = 1
LINEWIDTH = .5

fig, axes = plt.subplots(nrows=4, figsize=(3, 7),
    sharex=False, sharey=False, constrained_layout=True)

table = df.pivot(index="pc", columns="participant_id", values="rt")
xvals = table.index.values

n_lines = table.shape[1]
color_cycler = plt.cycler("color", colormap(np.linspace(0, 1, n_lines)))
for ax in axes:
    ax.tick_params(axis="both", which="both", direction="in",
        top=True, right=True)
    # ax.set_axisbelow(True)
    ax.set_prop_cycle(color_cycler)
    ax.grid(visible=True, axis="y", which="both",
        linewidth=1, alpha=1, color="gainsboro")

####
ax = axes[0]
yvals = table.values
ax.plot(xvals, yvals, alpha=ALPHA, linewidth=LINEWIDTH)
ax.set_ylabel("Time between presses (s)")
ax.set_ybound(upper=30)
ax.yaxis.set(major_locator=plt.MultipleLocator(5))

####
ax = axes[1]
yvals = table.rolling(10).mean().values
ax.plot(xvals, yvals, alpha=ALPHA, linewidth=LINEWIDTH)
ax.set_ylabel("Time between presses (s)")
ax.set_ybound(upper=10)
ax.yaxis.set(major_locator=plt.MultipleLocator(2))

####
ax = axes[2]
yvals = table.rolling(10).mean().values
ax.plot(xvals, 60/yvals, alpha=ALPHA, linewidth=LINEWIDTH)
ax.set_ylabel(r"Respirate rate, $f_{R}$")
ax.set_xlabel("Cumulative press count")
ax.set_ybound(upper=80)
ax.yaxis.set(major_locator=plt.MultipleLocator(20))

####
ax = axes[3]
yvals = table.rolling(10).mean().values
ax.plot(xvals, 60/yvals, alpha=ALPHA, linewidth=LINEWIDTH)
ax.set_ylabel(r"Respiration Rate, $f_{R}$")
ax.set_xlabel("Cumulative press count")
ax.set_ybound(upper=80)
ax.yaxis.set(major_locator=plt.MultipleLocator(20))


for ax in axes:
    ax.xaxis.set(major_locator=plt.MultipleLocator(100),
        minor_locator=plt.MultipleLocator(10))
    ax.set_xbound(lower=0)
    ax.set_ybound(lower=0)
    # ax.spines["bottom"].set_position(("outward", 5))
    # ax.spines["left"].set_position(("outward", 5))
    # ax.spines["top"].set_position(("outward", 5))
    # ax.spines["right"].set_position(("outward", 5))
# s2rr = lambda s: 60/s
# ax2 = ax.twinx()
# ax2.set_ylim(ymin, s2rr(ymax))
# ax2.yaxis.set(major_locator=plt.MultipleLocator(s2rr(5)),
#     minor_locator=plt.MultipleLocator(s2rr(1)))
# # s2rr = lambda s: 60/s # 60 seconds over s seconds to get breaths per minute respiration rate
# # rr2s = lambda f: 60/f # 60 seconds over f breaths per minute to get seconds between presses
# # secax = ax.secondary_yaxis("right", functions=(s2rr, rr2s))




export_fname = os.path.join(utils.Config.data_directory, "results",
    "bct-presscounts.png")
plt.savefig(export_fname)
plt.close()


# # Convert to minutes
# df["m"] = df["rt_sum"].div(60*1000)


# df["r"] = pd.to_timedelta(df["rt_sum"], unit="milliseconds")
# m = df["r"].min()
# # df["r"].max()
# a = df.resample("1S", on="r", offset=-m*2).mean()
# a = a.reindex(index=sec_index)

# # df.set_index("r").asfreq("1S")

# Convert cumulative press time to timedeltas.
df["tdelta"] = pd.to_timedelta(df["rt_sum"], unit="milliseconds")

# Create a timedelta index that nicely bins time.
# Bc of some jerk who fast-pressed with .1074 at one point
# this has to be very small. (it should be in single seconds)
tdelta_index = pd.timedelta_range(start="0 seconds",
    end="10 minutes", freq="1S")#periods=601)

# Bin the cumulative press timedeltas.
cuts = pd.cut(df["tdelta"], bins=tdelta_index, labels=False)
# cuts = cuts.mul(10) # bc of stupid tiny windows
df["tbinned"] = pd.to_timedelta(cuts, unit="seconds")
# df.set_index("rsecs").reindex(index=sec_index)

# Number of presses per second
# (almost always 1 except a rapid presser)
table = df.groupby(["participant_id", "tbinned"]).size(
    ).unstack("tbinned").reindex(columns=tdelta_index)
    # ).fillna(0, method="bfill") # back fillna bc want to know there was NO press when they stop
# resp_rate.rdiv(60)

# 10ms to one minute
# window_size = 60
# find number of seconds in a window to define min periods
# and prevent tails from being calculated with low counts
rrtable = table.rolling(window="60S", axis=1,
        center=True, min_periods=1,
        win_type=None, closed="both",
    ).sum()
    # ).dropna(axis=1 # to drop the column tails without enough data'
    #     # could interpolate or fillna them instead
    # ).astype(int)

# take off first/last 30 seconds which are tails and have little data
# (there should be a way to build this into rolling function??)
rrtable = rrtable.iloc[:,30:-30].copy()

# Smooth
rrtable = rrtable.rolling(60, axis=1,
        center=True, min_periods=1,
        win_type="gaussian", closed="both",
    ).mean(std=3)


fig, ax = plt.subplots(figsize=(3, 2), constrained_layout=True)

xvals = [ x.seconds/60 for x in rrtable.columns.to_pytimedelta() ]
yvals = rrtable.T.values

n_lines = yvals.shape[1]
color_cycler = plt.cycler("color", colormap(np.linspace(0, 1, n_lines)))
ax.tick_params(axis="both", which="both", direction="in",
    top=True, right=True)
# ax.set_axisbelow(True)
ax.set_prop_cycle(color_cycler)
ax.grid(visible=True, axis="y", which="both",
    linewidth=1, alpha=1, color="gainsboro")
ax.plot(xvals, yvals, alpha=ALPHA, linewidth=LINEWIDTH)
ax.set_ylabel(r"Respiration Rate, $f_{R}$")
# ax.set_ybound(upper=30)
ax.xaxis.set(major_locator=plt.MultipleLocator(1))
ax.set_xlim(0, 10)
ax.set_ylim(0, 80)
ax.yaxis.set(major_locator=plt.MultipleLocator(20))
ax.axhspan(12, 20, alpha=1, color="gainsboro")

ax.text(.1, 20, "Resting", color="gainsboro", ha="left", va="bottom", zorder=0)
ax.text(.1, 40, "Low exercise", color="gainsboro", ha="left", va="bottom", zorder=0)
ax.text(.1, 60, "High exercise", color="gainsboro", ha="left", va="bottom", zorder=0)

# ax2 = ax.secondary_yaxis("right")
# ax2.set_yticks([15, 40, 60])
# ax2.set_yticklabels(["Resting", "Low exercise", "High exercise"])
# ax2.tick_params(color="gainsboro", labelcolor="gainsboro")


# averaging across timepoints for each participant
rr_summary1 = rrtable.T.describe().T.round().astype(int)

divider = make_axes_locatable(ax)

data = rr_summary1["mean"].values
ax_histy = divider.append_axes("right", .6, pad=0, sharey=ax)
n, bins, patches = ax_histy.hist(data,
    orientation="horizontal", color="white",
    linewidth=1, edgecolor="black", alpha=1, clip_on=False)
ax_histy.tick_params(left=False, labelleft=False,
    axis="both", which="both", direction="in")
ax_histy.spines["top"].set_visible(False)
ax_histy.spines["right"].set_visible(False)
ax_histy.set_xlabel(r"$n$ participants")
# ax_histy.set_xbound(upper=3.5)
# ax_histy.set_xticks([])


# averaging across participants at each timepoint

# rr_summary2 = rr.describe().T.round(0).astype(int)

# avg RR at each point
mean = rrtable.mean(axis=0).to_frame("mean")
ci = rrtable.apply(lambda s:
        stats.bootstrap((s.values,), np.nanmean,
            n_resamples=10000, method="BCa"
        ).confidence_interval
    ).rename(index={0:"cilo", 1:"cihi"}).T
rr_summary2 = mean.join(ci)

variance = rrtable.std(axis=0).to_frame("variance")
ci = rrtable.apply(lambda s:
        stats.bootstrap((s.values,), np.nanstd,
            n_resamples=10000, method="BCa"
        ).confidence_interval
    ).rename(index={0:"cilo", 1:"cihi"}).T
rr_summary3 = variance.join(ci)

yvals = rr_summary2["mean"].rolling(60, min_periods=1, closed="both", win_type="gaussian").mean(std=3)
errlo = rr_summary2["cilo"].rolling(60, min_periods=1, closed="both", win_type="gaussian").mean(std=3)
errhi = rr_summary2["cihi"].rolling(60, min_periods=1, closed="both", win_type="gaussian").mean(std=3)
axtop = divider.append_axes("top", .4, pad=0, sharex=ax)
axtop.fill_between(xvals, errlo, errhi,
    linewidth=0, color="gainsboro", alpha=1)
axtop.plot(xvals, yvals, color="black", alpha=1, linewidth=.5)
axtop.tick_params(bottom=False, labelbottom=False, right=True,
    axis="both", which="both", direction="in")
axtop.set_ylabel(r"$\bar{f_{R}}$")
axtop.set_ylim(0, 40)
axtop.yaxis.set(major_locator=plt.MultipleLocator(20))
print("move grid params to config file")
axtop.grid(visible=True, axis="y", which="both",
    linewidth=1, alpha=1, color="gainsboro")

## copy/pasted garbage
yvals = rr_summary3["variance"].rolling(60, min_periods=1, closed="both", win_type="gaussian").mean(std=3)
errlo = rr_summary3["cilo"].rolling(60, min_periods=1, closed="both", win_type="gaussian").mean(std=3)
errhi = rr_summary3["cihi"].rolling(60, min_periods=1, closed="both", win_type="gaussian").mean(std=3)
axtop = divider.append_axes("top", .4, pad=0, sharex=ax)
axtop.fill_between(xvals, errlo, errhi,
    linewidth=0, color="gainsboro", alpha=1)
axtop.plot(xvals, yvals, color="black", alpha=1, linewidth=.5)
axtop.tick_params(bottom=False, labelbottom=False, right=True,
    axis="both", which="both", direction="in")
axtop.set_ylabel(r"$\sigma_{\bar{f_{R}}}$")
# axtop.set_ylim(0, 40)
# axtop.yaxis.set(major_locator=plt.MultipleLocator(20))
axtop.grid(visible=True, axis="y", which="both",
    linewidth=1, alpha=1, color="gainsboro")


export_fname = os.path.join(utils.Config.data_directory, "results",
    "bct-respirationrate.png")
plt.savefig(export_fname)
plt.close()



###############################
############################### BCT 1st half vs second half
###############################

## copy/pasted garbage



import_fname = os.path.join(utils.Config.data_directory, "derivatives", "bct-data_cycles.csv")
df4 = pd.read_csv(import_fname)
df4["correct"] = df4["accuracy"]=="correct"
# more copy/pasted garbage
# Convert cumulative press time to timedeltas.
df4["tdelta"] = pd.to_timedelta(df4["final_breath_rt_sum"], unit="milliseconds")

# Create a timedelta index that nicely bins time.
tdelta_index = pd.timedelta_range(start="0 seconds",
    end="10 minutes", freq="5min")#periods=601)

# Bin the cumulative press timedeltas.
cuts = pd.cut(df4["tdelta"], bins=tdelta_index, labels=False)
cuts = cuts.add(1).mul(5) # so it's minutes 1-10 rather than 0-9
# cuts = cuts.mul(10) # bc of stupid tiny windows
df4["tbinned"] = pd.to_timedelta(cuts, unit="minutes")
# df.set_index("rsecs").reindex(index=sec_index)

# Number of presses per second
# (almost always 1 except a rapid presser)
bct_timetable = df4.groupby(["participant_id", "tbinned"]
    )["correct"].mean(
    ).unstack("tbinned").reindex(columns=tdelta_index[1:]
    ).mul(100)
    # ).fillna(0, method="bfill") # back fillna bc want to know there was NO press when they stop
# resp_rate.rdiv(60)

xvals = np.arange(2)
yvals = bct_timetable.mean().values
errvals = bct_timetable.sem().values


color_normvals = [ i/(bct_timetable.index.size-1) for i, x in enumerate(bct_timetable.index) ]
colors = colormap(color_normvals)


fig, ax = plt.subplots(figsize=(2, 2), constrained_layout=True)

# plot mean/err
bars = ax.bar(xvals, yvals, yerr=errvals, color="white",
    edgecolor="black", linewidth=1, width=.6,
    error_kw=dict(capsize=0, ecolor="black", elinewidth=1))

bars.errorbar.lines[2][0].set_capstyle("round")

# plot individual subjects, colored.
color_cycler = plt.cycler("color", colormap(np.linspace(0, 1, n_lines)))
ax.set_prop_cycle(color_cycler)
np.random.seed(1)
JITTER = 0.05
data = bct_timetable.values
for c, row in zip(colors, data):
    jittered_xvals = xvals + np.random.normal(loc=0, scale=JITTER)
    ax.plot(jittered_xvals, row, "-o", color=c, alpha=1,
        markeredgewidth=.5, markeredgecolor="white",
        linewidth=.5, markersize=4, clip_on=False)





ax.set_ylabel("Breath counting accuracy")
ax.tick_params(axis="both", which="both", direction="in",
    bottom=False, right=True)
ax.set_ylim(0, 130)
xlim_buffer = .8
ax.set_xlim(xvals[0]-xlim_buffer, xvals[-1]+xlim_buffer)
ax.yaxis.set(major_locator=plt.MultipleLocator(50),
    minor_locator=plt.MultipleLocator(10),
    major_formatter=plt.matplotlib.ticker.PercentFormatter())
ax.set_xticks(xvals)
ax.set_xticklabels([r"$1^{\mathrm{st}}$ half", r"$2^{\mathrm{nd}}$ half"])
ax.grid(visible=True, axis="y", which="major",
    linewidth=1, alpha=1, color="gainsboro")
ax.set_axisbelow(True)


# stats
a, b = bct_timetable.dropna().T.values
wval, pval = stats.wilcoxon(a, b, zero_method="wilcox", correction=False)
results = pg.wilcoxon(a, b, correction=False).squeeze()
pval = results.loc["p-val"]
effval = results.loc["CLES"]
if pval < .001:
    p_txt = r"$p<0.001$"
else:
    p_txt = fr"$p={pval:.2f}$"
eff_txt = fr"$CLES={effval:.2f}$"

p_txt = p_txt.replace("0", "", 1)
if abs(effval) > 0 and abs(effval) < 1:
    eff_txt = eff_txt.replace("0", "", 1)

p_txt = "*" * sum([ pval < x for x in (.05, .01, .001) ]) + p_txt

stats_txt = "\n".join([p_txt, eff_txt])

sig_y = 110
ax.hlines(y=sig_y, xmin=xvals[0], xmax=xvals[-1],
    linewidth=1, color="black", capstyle="round")

txt_color = "black"# if pval < .1 else "gainsboro"
ax.text(xvals[-1], sig_y, stats_txt, color=txt_color,
    ha="right", va="bottom", linespacing=1)

# ax1.text(xloc, yloc+.01, sigchars, fontsize=10,
#     weight="bold", ha="center", va="center")



export_fname = os.path.join(utils.Config.data_directory, "results",
    "bct-halves.png")
plt.savefig(export_fname)
plt.close()



############################# plot correlation between
############################# respiration rate and number of presses
############################# with marginals
############################# should be near 1 to 1, but this
############################# also shows outliers for both press count and RR

# pairplot with subject
# respiration rate mean
# respiration rate variance
# respiration rate slope
# BCT accuracy
# n presses
# empathy task BEFORE intervention

# y = rrtable.loc[61].values
# x = np.arange(y.size)
# slope, intercept, r, p, stderr = stats.linregress(x, y)

# many ways to get this stuff
n_presses = table.sum(axis=1).rename("n_presses")
rr_avg = rrtable.mean(axis=1).rename("rr_avg")
rr_var = rrtable.std(axis=1).rename("rr_var")
rr_slope = rrtable.apply(lambda s:
        stats.linregress(range(s.dropna().values.size), s.dropna().values)[0],
    axis=1).rename("rr_slope")

import_fname = os.path.join(utils.Config.data_directory, "derivatives", "bct-data_cycles.csv")
df2 = pd.read_csv(import_fname)
df2["correct"] = df2["accuracy"]=="correct"
bct_acc = df2.groupby("participant_id"
    )["correct"].mean().rename("bct_acc")

import_fname  = os.path.join(utils.Config.data_directory, "derivatives", "empathy-correlation_avgs.csv")
df3 = pd.read_csv(import_fname)
empathy_acc = df3.query("task_condition=='bct'"
    ).query("pre_post=='pre'"
    ).set_index("participant_id"
    )["correlation"].rename("empathy_acc")

good = pd.concat([n_presses, rr_avg, rr_var, rr_slope, bct_acc, empathy_acc], axis=1)

var_order = ["n_presses", "rr_avg", "rr_var", "rr_slope",
    "bct_acc", "empathy_acc"]

n_vars = len(var_order)
figsize = (n_vars, n_vars)
fig, axes = plt.subplots(ncols=n_vars, nrows=n_vars, figsize=figsize,
    sharex=False, sharey=False,
    # sharex="col", sharey=False,
    constrained_layout=True)

limits = {
    "n_presses": (0, 510),
    "rr_avg": (0, 60),
    "rr_var": (0, 8),
    "rr_slope": (-.12, .12),
    "bct_acc": (0, 1),
    "empathy_acc": (0, 1),
}

labels = {
    "n_presses": r"$n$ presses",
    "rr_avg": r"$\bar{f_{R}}$",
    "rr_var": r"$\sigma_{\bar{f_{R}}}$",
    "rr_slope": r"$m_{f_{R}}$",
    "bct_acc": "BCT %",
    "empathy_acc": r"Empathy $r$",
}
        


color_normvals = [ i/(good.index.size-1) for i, x in enumerate(good.index) ]
colors = colormap(color_normvals)

SCATTER_KWARGS = {
    "clip_on": False,
    "s": 30,
    "alpha": .75,
    "linewidth": .5,
    "edgecolor": "white",
}

HIST_KWARGS = {
    "density": True,
    "histtype": "stepfilled",
    "color": "white",
    "edgecolor": "black",
    "linewidth": 1,
}

RUG_KWARGS = {
    "ymax": .1,
    "linewidth": 2,
    "alpha": .75,
}

for r in range(n_vars):
    for c in range(n_vars):
        ax = axes[r, c]
        # ax.set_aspect(1)
        yvar = var_order[r]
        xvar = var_order[c]
        ax.tick_params(axis="both", which="both", direction="in")

        if c == r: # xvar == yvar
            # ax.get_shared_y_axes().join(ax, axes[0,0])
            # for x in ax._shared_y_axes:
            #     for xx in x:
            #         ax.get_shared_y_axes().remove(xx)
            data = good[xvar].values
            n, bins, patches = ax.hist(data, **HIST_KWARGS)
            assert np.all(bins >= limits[xvar][0])
            assert np.all(bins <= limits[xvar][1])
            ax.set_xlim(*limits[xvar])
            ax.spines["top"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.tick_params(left=False, labelleft=False)
            if c+1 < n_vars:
                ax.tick_params(bottom=False, labelbottom=False)
            
            # rugplot
            for col, x in zip(colors, data):
                ax.axvline(x, color=col, **RUG_KWARGS)

        elif r < c: # upper triangle
            ax.axis("off")
        elif r > c: # lower triangle
            assert good[xvar].dropna().between(*limits[xvar], inclusive="both").all()
            assert good[yvar].dropna().between(*limits[yvar], inclusive="both").all()
            # ax.get_shared_y_axes().join(ax, axes[r, c-1])
            ax.scatter(xvar, yvar, data=good, color=colors, **SCATTER_KWARGS)
            ax.set_xlim(*limits[xvar])
            ax.set_ylim(*limits[yvar])
            ax.tick_params(which="both", axis="both", direction="in", right=True, top=True)
            if c > 0:
                ax.tick_params(which="both", labelleft=False)

            # run correlation
            x = good.dropna(subset=[xvar, yvar])[xvar].values
            y = good.dropna(subset=[xvar, yvar])[yvar].values
            slope, intercept, rval, pval, stderr = stats.linregress(x, y)
            r_txt = fr"$r={rval:.2f}$"
            if abs(rval) > 0 and abs(rval) < 1:
                r_txt = r_txt.replace("0", "", 1)
            r_txt += "*" * sum([ pval < x for x in (.05, .01, .001) ])
            # if p < .001:
            #     p_txt = r"$p<.001$"
            # else:
            #     p_txt = fr"$p={pval:.2f}$"
            txt_color = "black" if pval < .1 else "gainsboro"
            ax.text(.95, .05, r_txt, color=txt_color,
                transform=ax.transAxes, ha="right", va="bottom")

        if c == 0:
            ax.set_ylabel(labels[yvar], labelpad=1)
        if r+1 == n_vars:
            ax.set_xlabel(labels[xvar], labelpad=1)
        else:
            ax.tick_params(labelbottom=False)

# fig.align_ylabels(axes)
# fig.align_xlabels(axes)
fig.align_labels(axes)



export_fname = os.path.join(utils.Config.data_directory, "results",
    "bct-pairplot.png")
plt.savefig(export_fname)
plt.close()





##################### plot 1st half 2nd half repeated measures
##################### does mean and/or variance change

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
            alpha=ALPHA, linewidths=0, clip_on=False)

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
    "handletextpad" : .2 # space between legend marker and label
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
        label= "reset" if x=="space" else x,
        facecolor=c, edgecolor="white")
    for x, c in ACC_PALETTE.items() ]
legend2 = ax.legend(handles=accuracy_legend_elements,
    loc="lower left", bbox_to_anchor=(.2, 1),
    title="accuracy", **LEGENDS_ARGS)

ax.add_artist(legend1)
ax.add_artist(legend2)

ax.spines["top"].set_position(("outward", 5))
ax.spines["right"].set_position(("outward", 5))
ax.spines["left"].set_position(("outward", 5))
ax.spines["bottom"].set_position(("outward", 5))


export_fname = os.path.join(utils.Config.data_directory, "results",
    "bct-allpresses.png")
plt.savefig(export_fname)
plt.close()
