#! /usr/bin/env python

import fileinput
import json
import sys

# Helper to construct a string dictionary key for a given mention
def create_key(docid, sentid, text_contents):
  return "<>".join([docid, sentid, text_contents])
  

'''
Load the positive and negative examples and store in memory.
'''

pos_ex_file = "../data/training/positive_examples.csv"
neg_ex_file = "../data/training/positive_examples.csv"

delim = '\t'

# store negative and positive examples in memory

# key (string concat of docid, sentid, contents) -> eid
positive_ex = {}

# set of keys (string concat of docid, sentid, contents)
negative_ex = set()

# positive examples: doc_id  sent_id text_contents type  entity_id
f = open(pos_ex_file, 'r')
for line in f:
  vals = line.split(delim)

  docid = vals[0].strip()
  sentid = vals[1].strip()
  text_contents = vals[2].strip()
  m_type = vals[3].strip()
  eid = vals[4].strip()

  key = create_key(docid, sentid, text_contents)
  positive_ex[key] = eid
f.close()

# negative examples: doc_id  sent_id text_contents type
neg_f = open(neg_ex_file, 'r')
for line in neg_f:
  vals = line.split(delim)

  docid = vals[0].strip()
  sentid = vals[1].strip()
  text_contents = vals[2].strip()
  m_type = vals[3].strip()

  key = create_key(docid, sentid, text_contents)
  negative_ex.add(key)
neg_f.close()


'''
Process tuples from the candidate_link relation.
'''
for line in fileinput.input():
  '''
  From: SELECT c.mid AS "mid", m.doc_id AS "docid", m.sentence_id AS "sentid",
    m.text_contents AS "text_contents"
      FROM candidate_link AS c INNER JOIN mention AS m ON c.mid = m.id

  To: candidate_link(id, eid, mid, is_correct)
  '''
  
  row = json.loads(line)

  mid = row["mid"]
  docid = row["docid"]
  sentid = row["sentid"]
  text_contents = row["text_contents"]

  if mid is not None and docid is not None and sentid is not None and text_contents is not None:
    key = create_key(docid, sentid, text_contents)

    if key in positive_ex:
      eid = positive_ex[key]
      print json.dumps({"eid": eid, "mid": int(mid), "is_correct": True})
    
    elif key in negative_ex:
      print json.dumps({"eid": None, "mid": int(mid), "is_correct": True})

    else:
      print line
