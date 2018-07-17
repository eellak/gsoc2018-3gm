#!/usr/bin/env python3
# Simple Exporter
# usage: exporter.py --markdown < issue.txt > output.md
import sys
sys.path.insert(0, '../')
import parser

export_type = sys.argv[1].strip('--')
print(export_type)
issue = parser.IssueParser(None, stdin=True)
laws = issue.detect_new_laws()
for i, l in issue.new_laws.items():
    try:
        result = l.export_law(export_type)
        sys.stdout.write(result)
    except:
        sys.stderr.write('Error in exporting')
sys.stdout.flush()
