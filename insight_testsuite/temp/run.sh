

[ -e ./output/repeat_donors.txt ] && rm ./output/repeat_donors.txt
python ./src/donation-analytics.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt