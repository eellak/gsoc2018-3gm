#!/bin/bash

TODAY=`date +%d.%m.%Y` &&
./fetcher.py -date_from $TODAY -date_to $TODAY -output_dir $1
