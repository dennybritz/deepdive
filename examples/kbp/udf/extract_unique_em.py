#! /usr/bin/env python

import fileinput
import json

# For each tuple..
for line in fileinput.input():
  # From: SELECT DISTINCT (eid, mid) FROM candidate_link_exact_match
  # To: link(id, eid, mid, is_correct)
  row = json.loads(line)

  # Just pass the tuples through; need this extractor to get the unique (e, m)'s
  if row["eid"] is not None and row["mid"] is not None:
  	print json.dumps({"mid": int(row["mid"]), "eid": eid})
