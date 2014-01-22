#! /usr/bin/env python

import fileinput
import json
import sys

# load the file

# For each tuple..
for line in fileinput.input():
  '''
  From: mention theta join entity
  To: candidate_link(id, eid, mid, is_correct)
  '''

  sys.stderr.write(line + '\n')

  row = json.loads(line)

  mid = row["mention.id"]
  eid = row["entity.eid"]

  # Dummy extractor that basically just outputs the line (all the work is done by our query)
  if mid is not None and eid is not None:
    print json.dumps({"eid": eid, "mid": int(mid)})
