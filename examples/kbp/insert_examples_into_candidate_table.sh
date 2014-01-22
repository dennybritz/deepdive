#! /bin/bash

cd "$(dirname $0)/../..";
ROOT_PATH=`pwd`

# Configuration
DB_NAME=deepdive_kbp

# takes the evidence values and inserts them into the candidate_link table
psql -c """UPDATE candidate_link SET is_correct = 
	(SELECT evidence.is_correct FROM evidence
		WHERE evidence.link_id = candidate_link.id);""" $DB_NAME
