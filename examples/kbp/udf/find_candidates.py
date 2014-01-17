#! /usr/bin/env python

import fileinput
import json
import sys

# For each tuple..
for line in fileinput.input():
  '''
  From: SELECT * FROM mention INNER JOIN entity ON
        (lower(mention.text_contents) = lower(entity.text_contents) OR
        levenshtein(lower(mention.text_contents), lower(entity.text_contents)) < 3 OR
        similarity(lower(mention.text_contents), lower(entity.text_contents)) >= 0.75)
  
  To: candidate_link(id, eid, mid)
  '''
  
  row = json.loads(line)

  # Dummy extractor that selects eid and mid from each row
  eid = row["eid"]
  mid = row["mid"]

  if eid is not None and mid is not None:
  	print json.dumps({"eid": eid, "mid": int(mid)})
