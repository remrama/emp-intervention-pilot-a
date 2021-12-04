# tmr-empathy


### Selecting subset of videos from SEND for the current study

```shell
# Export a csv and some plots of the SEND dataset.
python send-description.py  # ==> DATA_DIR/derivatives/SEND-video_stats.csv
                            # ==> DATA_DIR/derivatives/SEND-correlations.png
                            # ==> DATA_DIR/derivatives/SEND-crowd_variability.png
                            # ==> DATA_DIR/derivatives/SEND-embeddings.png
                            # ==> DATA_DIR/derivatives/SEND-facial_expressions.png
                            # ==> DATA_DIR/derivatives/SEND-language.png
                            # ==> DATA_DIR/derivatives/SEND-sample_tcourses.png

# Select a subset of videos to use in the current experiment.
python send-select_vids.py  # ==> DATA_DIR/results/final_videos.png
```

### Analysis

```shell
# The raw output from jsPsych is messy so first
# just convert the raw output to a few csv files.
python clean-empathy.py     # ==> DATA_DIR/derivatives/empathy.csv
python clean-bct.py         # ==> DATA_DIR/derivatives/bct-presses.csv
                            # ==> DATA_DIR/derivatives/bct-cycles.csv

# Run empathy task correlations and export csv with r values.
python analyze-empathy.py   # ==> DATA_DIR/derivatives/empathy-correlations.csv

# Plot empathy task results.
python plot-empathy_all.py  # ==> DATA_DIR/results/empathy-all.png
python plot-empathy.py      # ==> DATA_DIR/results/empathy.csv
                            # ==> DATA_DIR/results/empathy.png

# Plot some breath counting task results.
python plot-bct-cycles.py   # ==> DATA_DIR/results/bct-respiration.png
python plot-bct-presses.py  # ==> DATA_DIR/results/bct-allpresses.png
                            # ==> DATA_DIR/results/bct-rtXpress.png
```