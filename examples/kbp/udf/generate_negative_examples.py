#! /usr/bin/env python

import fileinput
import json
import sys

for line in fileinput.input():
  '''
  From: SELECT c.id AS "link_id" FROM negative_example AS n INNER JOIN mention AS m
  		ON (n.text_contents == m.text_contents AND n.doc_id == m.doc_id)
        INNER JOIN candidate_link AS c ON m.id == c.mid AND n.eid == c.eid

  To: evidence(link_id, is_correct)
  '''
  
  sys.stderr.write(line + "\n")
  
  row = json.loads(line)
  link_id = row["link_id"]
    
  if link_id is not None:
      print json.dumps({"link_id": int(link_id), "is_correct": False})