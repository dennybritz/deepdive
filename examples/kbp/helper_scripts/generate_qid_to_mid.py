#! /usr/bin/env python

from bs4 import BeautifulSoup

'''
Produces a global mapping between query id's and mention id's for both evaluation and training
data.

Takes as input:
    ../data/evaluation/evaluation_entity_linking_queries.xml - qid, text_contents, docid
    ../data/training/training_entity_linking_queries.xml - qid, text_contents, docid, entity
    ../data/mention/mentions.csv - document id, sentence id, text contents of mention, type

Produces as output:
    ../data/qid_to_mid.csv - stores mapping between query id and generated mention id
        (qid mid text_contents type docid)
    
Processes both files and stores:
    all queries for each document in a dictionary
    all mentions for each document in a dictionary

Go through the queries files and populate the queries dictionary.
Go through the mentions file and populate the mentions dictionary.
Then, for each docid in mentions, for each text_contents, find the qid corresponding to the
docid, text_contents matching in the queries table and for this qid, print to the output file
all mid's.

For example, if for a given qid the name occurs several times in the document, each of those
occurrences will be assigned a unique mention id and thus multiple (qid, mid) entries will be
produced.
'''

eval_queries = '../data/evaluation/evaluation_entity_linking_queries.xml'
train_queries = '../data/training/training_entity_linking_queries.xml'
mention_file = '../data/mention/mentions.csv'
output_file = '../data/qid_to_mid.csv'

delim = '\t'

mention_id = 1

# docid -> {text_contents1: qid1, text_contents2: qid2, ...}
queries = {}

# docid -> {text_contents1: [(mid1, type), (mid2, type), ...], text_contents2: ...}
mentions = {}

# Go through the queries files to extract the query id's and doc id's.
# Input: filename (string) - the filename of the query XML file
def process_queries_file(filename):
    global queries

    f = open(filename, 'r')

    # parse the XML file
    contents = f.read()
    s = BeautifulSoup(contents)

    # for each query, get the query id, doc id, and contents and store them
    for query_node in s.findAll('query'):
        qid = str(query_node.get('id'))
        docid = str(query_node.find('docid').text)
        text_contents = str(query_node.find('name').text)

        if docid in queries:
            queries[docid][text_contents] = qid
        else:
            queries[docid] = {text_contents : qid}

    f.close()

# Go through the mentions file to get the doc id's and generate mention id's.
# Input: filename (string) - the filename of the mention CSV file
def process_mentions_file(filename):
    global mention_id
    global mentions

    f = open(filename, 'r')
    for line in f:
        vals = line.split(delim)

        docid = vals[0].strip()
        sentid = vals[1].strip()
        text_contents = vals[2].strip()
        m_type = vals[3].strip()
    
        if docid in mentions:
            if text_contents in mentions[docid]:
                mentions[docid][text_contents].append((mention_id, m_type))
            else:
                mentions[docid][text_contents] = [(mention_id, m_type)]
        else:
            mentions[docid] = {text_contents : [(mention_id, m_type)]}

        mention_id += 1

    f.close()

# Using the populated mentions and queries dictionaries, write the qid -> mid mapping to file.
def generate_qid_mid_mapping():
    out = open(output_file, 'w')

    for docid in mentions:
        for text_contents in mentions[docid]:
            if docid in queries and text_contents in queries[qid]:
                qid = queries[docid][text_contents]

                # list of (mid, type)
                mid_list = mentions[docid][text_contents]

                for (mid, m_type) in mid_list:
                    # qid mid text_contents type docid
                    out.write(delim.join([qid, mid, m_type, docid]) + '\n')
    out.close()


if __name__ == "__main__":
    # extract query id's and doc id's
    process_queries_file(train_queries)
    process_queries_file(eval_queries)

    # extract mentions and doc id's and generate mid's
    process_mentions_file(mention_file)

    # write the qid to mid mapping to our output file
    generate_qid_mid_mapping()

