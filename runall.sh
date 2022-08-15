
set -e # set script to exit if any command fails
 
python setup-directories.py

python send-description.py
python send-select_vids.py

python clean-empathy.py
python clean-bct.py

python analyze-empathy.py
python plot-empathy_tcourse.py
python plot-empathy.py
python plot-randomization.py
python plot-empathy_videos.py

python plot-bct_respiration.py
python plot-bct_presses.py
python plot-bct_cycles.py
python plot-bct_halves.py
python plot-bct_rt2rr.py
python plot-bct_correlations.py
