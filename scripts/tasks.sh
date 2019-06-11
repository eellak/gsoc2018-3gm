#!/bin/bash

# this is a sample bash script that demonstrates how we can use
# the new fetching script fetch by issue to mine several issues of the 
# GGG. 

for (( i=1; i<=800; i=i+200 ))
do
end=$(($i+199))
python3 fetch_by_issue.py -issue_from $i -issue_to $end -year 1984 -output_dir ./issues \
--chromedriver chromedriver --type  Δ
sleep 5
done




