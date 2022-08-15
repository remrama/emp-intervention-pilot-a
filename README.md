# tmr-empathy

This repo has display and analysis code for a behavioral pilot (online) study. We were testing if a brief mindfulness intervention could increase empathy.


## Code

* Display code for the jsPsych online deployment is in the `display` directory.
* Use `runall.sh` to run all the analysis at once.
* A few things, notably directories, are specified in the `config.json` configuration file.
* Source data should be in `data/source` and is archived as Empathy Intervention Pilot A on [this OSF page](https://osf.io/upa7t/).
* Stimuli should be in `<stim_directory>/SENDv1/`, with subdirectories for `features/`, `ratings/`, and `videos/`. Those subdirectories were pulled from the [Stanford Emotional Narratives Dataset (SEND)](https://github.com/StanfordSocialNeuroscienceLab/SEND). Unzip the main two zip files (`SENDv1_featuresRatings_pw.zip` and `SENDv1_videos_pw.zip`) and then merge each `test`/`train`/`valid` groups into one.



### Setup.

```shell
# Generate output directories.
python setup-directories.py     # => data/derivatives/
                                # => data/results/
                                # => data/results/hires/
```

### Selecting subset of videos from SEND for the current study

```shell
# Export a csv and some plots of the SEND dataset.
python send-description.py      # => data/derivatives/SEND-video_stats.csv
                                # => data/results/SEND-correlations.png
                                # => data/results/SEND-crowd_variability.png
                                # => data/results/SEND-embeddings.png
                                # => data/results/SEND-facial_expressions.png
                                # => data/results/SEND-language.png
                                # => data/results/SEND-sample_tcourses.png

# Select a subset of videos to use in the current experiment.
python send-select_vids.py      # => data/results/SEND-final_videos.png
```

### Analysis

```shell
# The raw output from jsPsych is messy so first just convert the raw output to a few csv files.
python clean-empathy.py         # => data/derivatives/empathy-data.csv
python clean-bct.py             # => data/derivatives/bct-data_presses.csv
                                # => data/derivatives/bct-data_cycles.csv

# Run empathy task correlations and export csv with r values.
python analyze-empathy.py       # => data/derivatives/empathy-correlations.csv

# Plot the task video randomization across participants.
python plot-randomization.py    # => data/results/empathy-videosets.png

# Plot empathy task results.
python plot-empathy_tcourse.py  # => data/results/empathy-correlation_tcourse.png
python plot-empathy.py          # => data/results/empathy-correlation_stats.csv
                                # => data/results/empathy-correlation_plot.png

# Visualize video EAT variability.
python plot-empathy_videos.py   # => data/results/empathy-video_variability.png
# Plot some breath counting task results.
python plot-bct_respiration.py  # => data/results/bct-respiration.csv
                                # => data/results/bct-respiration.png
python plot-bct_presses.py      # => data/results/bct-allpresses.png
python plot-bct_cycles.py       # => data/results/bct-rtXpress.png
python plot-bct_halves.py       # => data/results/bct-halves.png
python plot-bct_rt2rr.py        # => data/results/bct-rt2rr.png
python plot-bct_correlations.py # => data/results/bct-correlations.png
```