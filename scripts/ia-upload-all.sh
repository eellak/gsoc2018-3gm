#!/bin/bash
#
# Upload to the Internet Archive all files that aren't there
#
# Diomidis Spinellis, July 2018
#

# Directory where the PDFs are stored
PDFDIR=/home/repos/GGG/pdf

# Find the local PDFs
find $PDFDIR -type f -name '*.pdf' |
fgrep -v -f <(
  # Get items available on the IA
  ia search 'collection:greekgovernmentgazette' |
  # Obtain the identifier
  jq -r .identifier |
  # Convert output to file name
  sed 's/GreekGovernmentGazette-//;s/$/.pdf/') |
# Upload each file
xargs -n 1 ./upload.sh
