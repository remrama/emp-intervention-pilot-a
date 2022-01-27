
set -e # set script to exit if any command fails
 
python setup-data_directories.py

python clean-empathy.py
python clean-bct.py

python analyze-empathy.py
python analyze-bct_cycles.py
python analyze-bct_presses.py

python plot-empathy.py
python plot-empathy_all.py
