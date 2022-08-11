###############################
############################### BCT 1st half vs second half
###############################

import os
import numpy as np
import pandas as pd
import pingouin as pg

import matplotlib.pyplot as plt
import utils

utils.load_matplotlib_settings()
subj_palette = utils.load_subject_palette()


import_fname = os.path.join(utils.Config.data_directory, "derivatives", "bct-data_cycles.csv")
export_fname = os.path.join(utils.Config.data_directory, "results", "bct-halves.png")


df = pd.read_csv(import_fname)


####### Wrangle data into a dataframe with
####### first and second half performance for each subject.

# Make a new accuracy column that lumps all incorrects together.
df["correct"] = df["accuracy"].eq("correct")

### See plot-respirationrate.py script for details
### but here I'm creating a new table that bins
### presses into specific time chunks (here, two 5-min segments).
df["tdelta"] = pd.to_timedelta(df["final_breath_rt_sum"], unit="milliseconds")
fivemins_index = pd.timedelta_range(start="0 seconds", end="10 minutes", freq="5min")
cuts = pd.cut(df["tdelta"], bins=fivemins_index, labels=False)
cuts = cuts.add(1).mul(5) # so it's minutes 1-10 rather than 0-9
df["tbinned"] = pd.to_timedelta(cuts, unit="minutes")

bct_acc_timetable = df.groupby(["participant_id", "tbinned"]
    )["correct"].mean(
    ).unstack("tbinned").reindex(columns=fivemins_index[1:])

bct_acc_timetable.columns = ["firstFive", "secondFive"]


# Get group-level descriptives (across subjects).
group_desc = bct_acc_timetable.agg(["mean", "sem"]).T



######### Plot.

FIGSIZE = (2, 2)
BAR_KWARGS = dict(color="white", edgecolor="black",
    linewidth=1, width=.6)
ERRORBAR_KWARGS = dict(capsize=0, ecolor="black", elinewidth=1)
PLOT_KWARGS = dict(alpha=1, linewidth=.5, markersize=4,
    markeredgewidth=.5, markeredgecolor="white", clip_on=False)
TEXT_KWARGS = dict(ha="right", va="bottom", linespacing=1)
HLINE_KWARGS = dict(linewidth=1, capstyle="round")
SUBJ_JITTER = .05
XVALS = np.arange(2)
YMAX = 1.3
XLIM_EDGEBUFFER = .5
SIG_YLOC = 1.1 # where to place the significance bar and text


fig, ax = plt.subplots(figsize=FIGSIZE)

# Draw bars for the group.
bars = ax.bar(XVALS, "mean", yerr="sem", data=group_desc,
    error_kw=ERRORBAR_KWARGS, **BAR_KWARGS)
bars.errorbar.lines[2][0].set_capstyle("round")

# Draw individual subjects.
np.random.seed(1)
for subj, subj_row in bct_acc_timetable.iterrows():
    c = subj_palette[subj] if subj in subj_palette else "white"
    jittered_xvals = XVALS + np.random.normal(loc=0, scale=SUBJ_JITTER)
    ax.plot(jittered_xvals, subj_row.values, "-o", color=c, **PLOT_KWARGS)


######## Run and draw stats.

a, b = bct_acc_timetable.dropna().T.values
results = pg.wilcoxon(a, b, correction=False).squeeze()
pval, effval = results.loc[["p-val","CLES"]]
p_txt = r"$p<0.001$" if pval < .001 else fr"$p={pval:.2f}$"
eff_txt = fr"$CLES={effval:.2f}$"
p_txt = p_txt.replace("0", "", 1)
if 0 < abs(effval) < 1:
    eff_txt = eff_txt.replace("0", "", 1)

sig_chars = "*" * sum([ pval < x for x in (.05, .01, .001) ])
p_txt = sig_chars + p_txt

sig_txt = "\n".join([p_txt, eff_txt])
sig_color = "black" if pval < .1 else "gainsboro"

ax.text(XVALS[-1], SIG_YLOC, sig_txt, color=sig_color, **TEXT_KWARGS)
ax.hlines(y=SIG_YLOC, xmin=XVALS[0], xmax=XVALS[-1],
    color=sig_color, **HLINE_KWARGS)



###### Aesthetics.

xmin = XVALS[0] - BAR_KWARGS["width"]/2 - XLIM_EDGEBUFFER
xmax = XVALS[-1] + BAR_KWARGS["width"]/2 + XLIM_EDGEBUFFER
ax.set_xlim(xmin, xmax)
ax.set_xticks(XVALS)
ax.set_xticklabels([r"$1^{\mathrm{st}}$ half", r"$2^{\mathrm{nd}}$ half"])
ax.set_ylabel("Breath counting accuracy")
ax.set_ybound(upper=YMAX)
ax.tick_params(top=False, bottom=False)
ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
    minor_locator=plt.MultipleLocator(.1),
    major_formatter=plt.matplotlib.ticker.PercentFormatter(xmax=1))





plt.savefig(export_fname)
utils.save_hires_copies(export_fname)
plt.close()