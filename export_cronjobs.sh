#!/bin/bash
crontab -l > tempcron
echo "30 $1 * * * $(3GM_SCRIPTS)/fetch_daily.sh $2 && python3 $(3GM_SCRIPTS)/converter.py -input_dir $2 -output_dir $3 -pdf2txt pdf2txt --recursive"
crontab tempcron
rm tempcron
