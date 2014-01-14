#! /usr/bin/env python

import fileinput
import json

# For each tuple..
for line in fileinput.input():
  # From: <mention id>,<doc id>,<sentence id>,<mention type>,<mention text>
  # To: mention_features(id, word_count)
  row = json.loads(line)
  # We are emitting one variable and one factor for each word.
  if row["mention.text_contents"] is not None:
  	num_words = len(row["mention.text_contents"].split(" "))
  	print json.dumps({"id": int(row["mention.id"]), "word_count": num_words})
