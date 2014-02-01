#! /bin/bash

# Configuration
DB_NAME=deepdive_kbp
DB_USER=
DB_PASSWORD=

cd `dirname $0`
BASE_DIR=`pwd`

dropdb deepdive_kbp
createdb deepdive_kbp

psql -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;" $DB_NAME

psql -c "CREATE EXTENSION fuzzystrmatch;" $DB_NAME

# stores the raw text documents
psql -c """CREATE TABLE document(
	id text primary key,
	raw_text text);""" $DB_NAME

# populated by extract_mentions.py
psql -c """CREATE TABLE mention(
	id bigserial primary key,
	doc_id text not null references document(id),
	text_contents text not null,
	type text);""" $DB_NAME

# populated from entity/entity.sql
psql -c """CREATE TABLE entity(
	id text primary key,
	text_contents text not null,
	type text);""" $DB_NAME

# populated from data/training/training.tab
psql -c """CREATE TABLE positive_example(
	doc_id text,
	text_contents text,
	eid text,
	primary key (doc_id, text_contents));""" $DB_NAME

# (entity, mention) pairs that could potentially be linked
psql -c """CREATE TABLE candidate_link(
	id bigserial primary key,
	eid text not null references entity(id),
	mid bigserial not null references mention(id),
	is_correct boolean);""" $DB_NAME

# this table is populated from positive_example and from negative_example using extractors
psql -c """CREATE TABLE evidence(
	link_id bigserial primary key references candidate_link(id),
	is_correct boolean);""" $DB_NAME

# the feature type for the entity-mention link
psql -c """CREATE TABLE link_feature(
	link_id bigserial primary key references candidate_link(id),
	feature text);""" $DB_NAME

# a negative example (e2, m1): given a positive example (e1, m1), generate all
# pairs (e2, m1) such that e2 != e1 (for al the other entities, mark that mention as false)
psql -c """CREATE VIEW negative_example AS
	SELECT c2.mid AS \"mid\", c2.eid AS \"eid\" FROM (candidate_link AS c INNER JOIN mention AS m ON m.id = c.mid) AS c1,
	candidate_link AS c2, positive_example AS p
	WHERE c1.c.eid = p.eid AND c1.c.eid <> c2.eid AND c1.cmid = c2.mid AND p.doc_id = c1.m.doc_id
	AND p.text_contents = c1.m.text_contents;""" $DB_NAME


# populate the document table:
# load each file's contents as a row in the document table;
# use tr to replace newlines in STDIN with blanks so that each row's raw text
# is a string without newlines
# (if copy with newlines will get separate rows for each line)
cd $BASE_DIR/data/text
i=0
num=$(ls -1 | wc -l)
for f in $BASE_DIR/data/text/dir_001/* # TODO: change to dir_001 to ** before releasing!
do
	# docid is the filename
	docid=`basename $f`
	docid="${docid/.txt/}" # get rid of the .txt extension

	# print to stdin: docid<tab>raw_text
	tr '\n' ' ' < $f | tr '\t' ' ' | awk -v id=$docid '{ line=id"\t"$0 } END { print line }' \
	| psql -c "COPY document(id, raw_text) FROM STDIN DELIMITER AS E'\t';" $DB_NAME

	if [ $(( i % 1000 )) -eq 0 ]
		then echo "Processed $i out of about $(( num * 200 )) text files"
	fi
	let i++
done
cd $BASE_DIR

# populate the entity table
psql -f $BASE_DIR/data/entity/entity.sql $DB_NAME

# populate the positive_example table
psql -c """COPY positive_example(doc_id, text_contents, eid) FROM '$BASE_DIR/data/training/training.tsv'
	WITH NULL AS 'NIL' DELIMITER AS E'\t';""" $DB_NAME

