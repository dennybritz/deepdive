#! /usr/bin/env python

from bs4 import BeautifulSoup
import nltk, re, pprint, os

'''
This script converts raw mention data and freebase entity data into CSV
format for KBP entity linking.

1. Process raw mentions and perform NER using NLTK. Extract the entities that 
we need (PER, ORG, etc.) and write to CSV file.
2. Process Freebase entity RDF data, extract the entities we need (PER, ORG, etc.),
and write to CSV file.
'''

###
# CONSTANTS
###

# entities
FREEBASE_PREFIX = '<http://rdf.freebase.com/ns/'
FREEBASE_PER = 'people.person>'
FREEBASE_LOC = 'location.location>'
FREEBASE_ORG = 'organization.organization>' 
FREEBASE_LIST = [FREEBASE_PREFIX + FREEBASE_PER, FREEBASE_PREFIX + FREEBASE_LOC]

# mentions
PER = 'PERSON'
ORG = 'ORGANIZATION'
MENTION_LIST = [PER, ORG]

# mentions (newswire text in sgm format)
nw_datadir = 'data/newswire/raw'

# sample freebase entities in RDF format (small 10mb file)
fb_datadir = 'data/freebase/raw'

# output csv files
nw_output_file = 'data/newswire/kbp_mentions_nw.csv'
fb_output_file = 'data/freebase/kbp_entities_fb.csv'

###
# HELPERS
###

# global sentence id (incremented after each new sentence in mentions)
sentence_id = 1

'''
Input: data_file (file object) - handle to input data file to be processed,
       out_file (file object) - handle to output csv file

Find relevant mentions inside the given text (using NLTK).
Write the processed data to the output file.
'''
def process_mention(data_file, out_file):
    global sentence_id

    # doc_id is the filename without the extension
    doc_id = os.path.splitext(data_file.name)[0]

    # use a library to get all the raw text inside the <text> tag
    s = BeautifulSoup(data_file.read())
    text_contents = s.find('text').text

    # POS tagging on sentences
    sentences = nltk.sent_tokenize(text_contents)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]

    # NER on each sentence
    for sent in sentences:
        chunked_sent = nltk.ne_chunk(sent)

        for child in chunked_sent.subtrees():
            if child.node in MENTION_LIST:
                node_value = ' '.join([x[0] for x in child])
                out_file.write(','.join([str(sentence_id), doc_id, node_value, child.node]) + '\n')
        
        sentence_id += 1


'''
Input: data_file (file object) - handle to input data file to be processed,
       out_file (file object) - handle to output csv file

Find the entities we want in the Freebase data.
Write the processed data to the output file.
'''
def process_entity(data_file, out_file):
    for line in data_file:
        vals = line.split('\t')

        if len(vals) == 4:
            if vals[2].strip() in FREEBASE_LIST:
                print "AHA"
                mid = vals[0].replace(FREEBASE_PREFIX).replace('.', '_')

                if vals[2].find(FREEBASE_PER):
                    out_file.write(','.join([PER, mid]) + '\n')
                elif vals[2].find(FREEBASE_ORG):
                    out_file.write(','.join([ORG, mid]) + '\n')
               
                # TODO: add GPE


'''
Input: rootdir (string) - directory containing raw data files
       process_function (function of 1 arg) - function that performs
           processing on a given data file in the directory,
       out_file (string) - handle to output file (will contain processed data)

Recursively traverses the root directory, looking for files, and calls the
given function on each file such that the result will be written to the
output file.
'''
def process_all_files(rootdir, process_function, out_file):
    for root, subfolders, files in os.walk(rootdir):
        for folder in subfolders:
            process_all_files(os.path.join(root, folder), process_function, out_file)
        for filename in files:
            with open(os.path.join(root, filename), 'r') as data_file:
                process_function(data_file, out_file)

###
# MAIN
###

if  __name__ == '__main__':
    print "Processing mentions..."

    # process the mentions
    #outputfile = open(nw_output_file, 'w')
    #process_all_files(nw_datadir, process_mention, outputfile)
    #outputfile.close()  

    print "Processing entities..."

    # process the entities
    outputfile = open(fb_output_file, 'w')
    process_all_files(fb_datadir, process_entity, outputfile)
    outputfile.close()

    print "Done."