#!/bin/sh
#
# Upload the specified Greek Government Gazette file to the Internet Archive
# greekgovernmentgazette collection.
# The file should be named as [path/]YYYYPPNNNNN.pdf
# where YYYY is the issuea year, PP is the part (01 is part A), and NNNNN is
# the number.
# The uploaded must have admin access to the collection
#
# Diomidis Spinellis, July 2018
#

# Parse file name into its constituent parts
id=$(basename "$1" .pdf)
year=$(expr substr $id 1 4)
part=$(expr substr $id 5 2)
part=$(expr $part : '0*\(.*\)')
number=$(expr substr $id 7 5)
number=$(expr $number : '0*\(.*\)')

# Invoke the Internet Archive CLI script to upload file and specify
# its metadata.  See https://github.com/jjjake/internetarchive and
# https://archive.org/services/docs/api/internetarchive/.
ia upload GreekGovernmentGazette-$id "$1" \
  --retries=20 --sleep=60 \
  -m collection:greekgovernmentgazette \
  -m contributor:'Diomidis Spinellis' \
  -m creator:'The Government of the Hellenic Republic' \
  -m date:$year \
  -m language:gre \
  -m licenseurl:http://www.et.gr/index.php/oroi-xrisis \
  -m mediatype:texts \
  -m publisher:'Greek National Printing House' \
  -m rights:'According to Greek laws 3469/2006 and 4305/2014, Greek Government Gazette issues can be used for any lawful purpose, apart from the reproduction or distribution for profit, which is prohibited.' \
  -m subject:'Greek Government Gazette' \
  -m subject:'Greece' \
  -m subject:'official journal' \
  -m subject:"Part $part" \
  -m subject:'FEK' \
  -m subject:'ΦΕK' \
  -m subject:'Εφημερίδα της Κυβερνήσεως' \
  -m title:"Greek Government Gazette: Part $part, $year no. $number" \
  -m sponsor:"Greek Open Technologies Alliance through Google Summer of Code"
