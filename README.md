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
python clean-empathy.py     # ==> data/derivatives/empathy-data.csv
python clean-bct.py         # ==> data/derivatives/bct-data_presses.csv
                            # ==> data/derivatives/bct-data_cycles.csv

# Run empathy task correlations and export csv with r values.
python analyze-empathy.py   # ==> data/derivatives/empathy-correlations.csv

# Plot empathy task results.
python plot-empathy_all.py  # ==> data/results/empathy-all.png
python plot-empathy.py      # ==> data/results/empathy-correlation_stats.csv
                            # ==> data/results/empathy-correlation_plot.png

# Plot some breath counting task results.
python analyze-bct_cycles.py    # ==> data/results/bct-respiration.png
python analyze-bct_presses.py   # ==> data/results/bct-allpresses.png
                                # ==> data/results/bct-rtXpress.png
```