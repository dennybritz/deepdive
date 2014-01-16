#! /usr/bin/env python

import fileinput
import json

# For each tuple..
for line in fileinput.input():
  # From: mention(id, doc_id, sentence_id, text_contents, type)
  # To: mention_features(id, mid, text_lc)
  row = json.loads(line)
  # We are converting each mention row's text_contents into lowercase
  if row["mention.text_contents"] is not None:
  	text_lc = row["mention.text_contents"].lower()
  	print json.dumps({"mid": int(row["mention.id"]), "text_lc": text_lc})
