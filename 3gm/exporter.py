#!/usr/bin/env python3
# Simple Exporter
# usage: exporter.py --markdown < issue.txt > output.md
import sys, parser

export_type = sys.argv[1].strip('--')
issue = parser.IssueParser(None, stdin=True)
laws = issue.detect_new_laws()
for l in issue.new_laws:
    try:
        result = l.export_law(export_type)
        sys.stdout.write(result)
    except:
        sys.stderr.write('Error in exporting')
sys.stdout.flush()
