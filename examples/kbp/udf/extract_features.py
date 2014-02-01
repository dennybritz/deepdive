#! /usr/bin/env python

import fileinput
import json
import nltk.metrics.distance
import ngram

LEVENSHTEIN_DIST_THRESHOLD = 3
SIMILARITY_THRESHOLD = 0.75

'''
Helpers that extract features between a pair of strings.
'''

def is_exact_string_match(str1, str2):
	return str1 == str2

def is_levenshtein_dist_smaller_than_thr(str1, str2):
	return nltk.metrics.distance.edit_distance(str1, str2) < LEVENSHTEIN_DIST_THRESHOLD

def is_similarity_large(str1, str2):
	return ngram.NGram.compare(str1, str2, N=3) >= SIMILARITY_THRESHOLD

def is_either_substr_of_other(str1, str2):
  return (str1.find(str2) >= 0) or (str2.find(str1) >= 0)

# the list of feature-extracting functions we are currently extracting
feature_functions = [is_exact_string_match, is_levenshtein_dist_smaller_than_thr, \
	is_similarity_large, is_either_substr_of_other]

# For each tuple..
for line in fileinput.input():
  '''
  From: SELECT * FROM candidate_link INNER JOIN mention 
        ON (candidate_link.mid = mention.id) INNER JOIN entity 
        ON (candidate_link.eid = entity.id)

  To: link_feature(id, eid, mid, feature_type, is_correct)
  '''

  row = json.loads(line)

  eid = row["entity.eid"]
  mid = row["mention.mid"]
  entity_text = row["entity.text_contents"]
  mention_text = row["mention.text_contents"]
  
  if eid is not None and mid is not None and entity_text is not None and mention_text is not None:
  	# For each feature for this (e, m) pair, output the feature type
  	# (but only if that feature returns true)
  	for func in feature_functions:
  		if func(entity_text.lower(), mention_text.lower()):
		  	print json.dumps({
		  		"eid": eid,
		  		"mid": int(mid),
		  		"feature_type": func.__name__
		  	})
        