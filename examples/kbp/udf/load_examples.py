#! /usr/bin/env python

import fileinput
import json
import sys

'''
Load the positive and negative examples and store in memory.
'''

pos_ex_file = "../data/training/positive_examples.csv"
neg_ex_file = "../data/training/negative_examples.csv"

delim = '\t'

# store positive examples in memory

# text_contents -> eid
positive_ex = {}
negative_ex = {}

# loads the examples from the filename into the provided dict
def load_examples(examples, filename):
  # examples: doc_id  sent_id text_contents type  entity_id
  f = open(filename, 'r')
  for line in f:
    vals = line.split(delim)
    text_contents = vals[2].strip()
    eid = vals[4].strip()

    # we are identifying an entity by its text contents; reasonable to assume that
    # a mention whose text exactly matches the text of some entity will be linked to that entity
    examples[text_contents] = eid
  f.close()

  return examples

# LOAD POSITIVE AND NEGATIVE EXAMPLES
positive_ex = load_examples(positive_ex, pos_ex_file)
negative_ex = load_examples(negative_ex, neg_ex_file)

'''
Process tuples from the candidate_link relation.
'''
for line in fileinput.input():
  '''
  From: SELECT c.id AS "link_id", c.mid AS "mid", c.eid AS "eid",
        m.text_contents AS "text_contents" FROM candidate_link AS c INNER JOIN mention AS m
        ON (c.mid = m.mid)

  To: evidence(link_id, is_correct)
  '''
  
  row = json.loads(line)

  mid = row["mid"]
  text_contents = row["text_contents"]
  link_id = row["link_id"]

  if mid is not None and text_contents is not None and link_id is not None:
    # if this text exactly matches the text of some entity-mention pair that is a positive example
    # (we are also assuming that both text_contents for that entity and that mention will be
    # identical)
    if text_contents in positive_ex:
      eid = positive_ex[key]
      print json.dumps({"link_id": int(link_id), "is_correct": True})

    else:
      print json.dumps({"link_id": int(link_id)})
