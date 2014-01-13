#! /usr/bin/env python

from bs4 import BeautifulSoup
import nltk, re, pprint, os

'''
This script converts raw mention data into CSV format for KBP entity linking.
The entity data is in CSV format and can be directly loaded into the database.
'''

# the raw data 
nw_datadir = 'data/newswire/raw'

# the CSV file DeepDive needs
nw_output_file = 'data/newswire/kbp_mentions_nw.csv'

# global sentence id
sentence_id = 1

# Find things that are PER, ORG, or LOC.
def entity_resolution(text_contents):
	global sentence_id

	sentences = nltk.sent_tokenize(text_contents)
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences]

	c = nltk.ne_chunk(sentences[0])

	print c

	for child in c.subtrees():
		if child.node == "PERSON":
			print ' '.join([x[0] for x in child])

	print "============="


# look at all the files in our data directory
def process_all_files(rootdir):
	for root, subfolders, files in os.walk(rootdir):
		for folder in subfolders:
			process_all_files(os.path.join(root, folder))

		for filename in files:
			with open(os.path.join(root, filename), 'r') as data_file:
				s = BeautifulSoup(data_file.read())

		        # get all the raw text inside the <text> tag
		        text_contents = s.find('text').text

		        # figure out which things in the text are PER, LOC, ORG
		        entity_resolution(text_contents)
	        
		        # TODO write to CSV file
		        doc_id, fext = os.path.splitext(filename)


outputfile = open(nw_output_file, 'w')
process_all_files(nw_datadir)
outputfile.close()	