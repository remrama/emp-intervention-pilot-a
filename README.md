# tmr-empathy


### Selecting subset of videos from SEND for the current study


### Analysis

```shell
# The raw output from jsPsych is messy so first
# just convert the raw output to a few csv files.
python clean-empathy.py     # ==> DATA_DIR/derivatives/empathy.csv
python clean-bct.py         # ==> DATA_DIR/derivatives/bct.csv

# Run empathy task correlations and export csv with r values
python analyze-empathy.py   # ==> DATA_DIR/derivatives/empathy-correlations.csv

# Plot empathy task results.
python plot-empathy_all.py  # ==> DATA_DIR/results/empathy-all.png
python plot-empathy.py      # ==> DATA_DIR/results/empathy.png
```