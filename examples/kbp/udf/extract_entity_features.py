#! /usr/bin/env python

import fileinput
import json

# For each tuple..
for line in fileinput.input():
  # From: entity(id, type, text_contents)
  # To: entity_features(id, eid, text_lc)
  row = json.loads(line)
  # We are converting each entity row's text_contents into lowercase
  if row["entity.text_contents"] is not None:
  	text_lc = row["entity.text_contents"].lower()
  	print json.dumps({"eid": row["entity.id"], "text_lc": text_lc})
