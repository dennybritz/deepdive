#! /usr/bin/env python

import fileinput
import json
import sys

# load the file

# For each tuple..
for line in fileinput.input():
  '''
  From: SELECT * FROM mention INNER JOIN entity ON
          (lower(mention.text_contents) = lower(entity.text_contents) OR
          levenshtein(lower(mention.text_contents), lower(entity.text_contents)) < 3 OR
          similarity(lower(mention.text_contents), lower(entity.text_contents)) >= 0.75) OR
          position(lower(mention.text_contents), lower(entity.text_contents)) >= 0 OR
          position(lower(entity.text_contents), lower(mention.text_contents))
  
  To: candidate_link(id, eid, mid, is_correct)
  '''

  row = json.loads(line)

  mid = row["mention.id"]
  eid = row["entity.eid"]

  # Dummy extractor that basically just outputs the line (all the work is done by our query)
  if mid is not None and eid is not None:
    print json.dumps({"eid": eid, "mid": int(mid)})
