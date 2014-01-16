#! /usr/bin/env python

import fileinput
import json
import sys

EXTRACTOR_NAME = "exact_match"

# For each tuple..
for line in fileinput.input():
  # From: SELECT * FROM mention_features INNER JOIN entity_features ON mention_features.text_lc = entity_features.text_lc
  # To: candidate_link(id, eid, mid, extractor_type)
  row = json.loads(line)

  eid = row["entity_features.eid"]
  mid = row["mention_features.mid"]

  if eid is not None and mid is not None:
  	print json.dumps({"eid": eid, "mid": int(mid), "extractor_type": EXTRACTOR_NAME})
