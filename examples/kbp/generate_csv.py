#! /usr/bin/env python

from bs4 import BeautifulSoup
import nltk, re, pprint, os

'''
This script converts raw mention data and freebase entity data into CSV
format for KBP entity linking.

Input entity file: <subject>\t<predicate>\t<object>\t.
Output entity CSV file: <entity id>,<entity type>,<entity name>

Input mention file: sgm (like XML), with relevant text inside
the <text> tag: <text>relevant text</text>
Output mention CSV file:
    <mention id>,<doc id>,<sentence id>,<mention type>,<mention text>

1. Process raw mentions and perform NER using NLTK. Extract the 
appropriately-tagged mentions (PER, ORG, etc.) and write to CSV file. 
In this example we will only care about the PER mentions for illustrative
purposes.

2. Process Freebase entity RDF data, extract the entities we need (PER, ORG, etc.),
and write to CSV file. In this example we will only care about the PER entities
for illustrative purposes.
'''

###
# CONSTANTS
###

FB_PREFIX = '<http://rdf.freebase.com/ns/'
OBJ_TYPE = '<http://rdf.freebase.com/ns/type.object.type>'
OBJ_NAME = '<http://rdf.freebase.com/ns/type.object.name>'

# entities (only care about PER)
FB_PER = '<http://rdf.freebase.com/ns/people.person>'

# mentions (only care about PER)
PER = 'PERSON'

# mentions data directory (newswire text in sgm format)
nw_datadir = 'data/newswire/raw'

# data directory for sample freebase entities in RDF format
fb_datadir = 'data/freebase/raw'

# output csv files
nw_output_file = 'data/newswire/kbp_mentions_nw.csv'
fb_output_file = 'data/freebase/kbp_entities_fb.csv'

###
# HELPERS
###

# unique id for each sentence (incremented after each new sentence in mentions)
sentence_id = 1

# unique id for each mention
mention_id = 1

'''
Input: data_file (file object) - handle to input data file to be processed,
       out_file (file object) - handle to output csv file

Find relevant mentions inside the given text (using NLTK).
Write the processed data to the output file.
'''
def process_mention(data_file, out_file):
    global sentence_id
    global mention_id

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
            if child.node == PER:
                node_value = ' '.join([x[0] for x in child])
                out_file.write(','.join([str(mention_id), data_file.name.split('/')[-1], \
                    str(sentence_id), node_value, child.node]) + '\n')
                mention_id += 1
        
        sentence_id += 1


'''
Input: data_file (file object) - handle to input data file to be processed,
       out_file (file object) - handle to output csv file

Find the PERSON entities in the Freebase data file and for each entity
extract the entity name.
Write the processed data to the output file.
'''
def process_entity(data_file, out_file):
    # RDF file is of the following scheme
    # (entries referring to same subject are contiguous):
    #   subj1 pred1 obj1
    #   subj1 pred3 obj3
    #   subj2 pred4 obj4
    #   subj2 pred5 obj5
    #   ...

    # each subject has many predicates
    # for each subject, maintain a dict of pred -> list of objects
    # here, since we extract only PER entities, only store the names
    curr_subj_dict = {}

    # used to check when we reach a new subject
    prev_subject = ''

    for line in data_file:
        vals = line.split('\t')

        subject = vals[0].strip() # the subjects we care about are entity id's
        predicate = vals[1].strip() # e.g., type.object.type or type.object.name
        obj = vals[2].strip() # e.g., people.person

        # new subject (skips first line when prev_subject is '')
        if subject != prev_subject and prev_subject != '':
            # do stuff to this entity if it is a person
            if FB_PER in curr_subj_dict[OBJ_TYPE]:
                # get the entity id
                eid = prev_subject.replace(FB_PREFIX, '').replace('.', '_').replace('>', '')

                # check if this person has a name, though this should never be false
                if OBJ_NAME in curr_subj_dict:
                    names = curr_subj_dict[OBJ_NAME]
                    name = ''

                    # find the english name
                    for n in names:
                        if n.find('@en') > 0:
                            name = n.replace('\"', '').replace('@en', '')
                            break

                    # couldn't find an english name, so take the first one
                    if name == '':
                        name = names[0]

                    # write to output file
                    out_file.write(','.join([eid, PER, name]) + '\n')

            # clear the temporary storage
            curr_subj_dict.clear()

        # for each line we see, save the contents into our dict

        # if we haven't seen this predicate yet
        if predicate not in curr_subj_dict:
            curr_subj_dict[predicate] = []

        # if we have a name or object type, save it
        if predicate == OBJ_NAME or predicate == OBJ_TYPE:
            curr_subj_dict[predicate].append(obj)

        # moving on to the next line so remember the current subject
        prev_subject = subject
         

'''
Input: rootdir (string) - directory containing raw data files
       process_function (function of 1 arg) - function that performs
           processing on a given data file in the directory,
       out_file (string) - handle to output file (will contain processed data),
       mode (string) - the mode with which to open the file

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
    outputfile = open(nw_output_file, 'w')
    process_all_files(nw_datadir, process_mention, outputfile)
    outputfile.close()  

    print "Processing entities..."

    # process the entities
    outputfile = open(fb_output_file, 'w')
    process_all_files(fb_datadir, process_entity, outputfile)
    outputfile.close()

    print "Done."
