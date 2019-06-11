#!/bin/bash
# Upload daily script

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
find $1 -mtime -2 -name "*.pdf" | xargs -n 1 ./ia-upload.sh
