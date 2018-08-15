#!/bin/bash

# Fetch daily script
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
TODAY=`date +%d.%m.%Y` &&
YESTERDAY=`date +%d.%m.%Y -d "-2 days"` &&
./fetcher.py -date_from $YESTERDAY -date_to $TODAY -output_dir $1 --type Α --upload
./fetcher.py -date_from $YESTERDAY -date_to $TODAY -output_dir $1 --type Β --upload