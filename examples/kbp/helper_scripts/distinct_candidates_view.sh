#! /bin/bash

# Configuration
DB_NAME=deepdive_kbp
DB_USER=
DB_PASSWORD=

cd `dirname $0`
BASE_DIR=`pwd`

psql -c """CREATE VIEW candidate_link_distinct AS
		   SELECT DISTINCT (eid, mid) FROM candidate_link;""" $DB_NAME