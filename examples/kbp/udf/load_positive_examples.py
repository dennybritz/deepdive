#! /usr/bin/env python

import fileinput
import json
import sys

for line in fileinput.input():
  '''
  From: SELECT c.id AS "link_id" FROM positive_example AS p INNER JOIN mention AS m ON
        (p.text_contents == m.text_contents AND p.doc_id == m.doc_id)
        INNER JOIN candidate_link AS c ON m.id == c.mid AND p.eid == c.eid

  To: evidence(link_id, is_correct)
  '''
  
  sys.stderr.write(line + "\n")
  
  row = json.loads(line)
  link_id = row["link_id"]
    
  if link_id is not None:
      print json.dumps({"link_id": int(link_id), "is_correct": True})