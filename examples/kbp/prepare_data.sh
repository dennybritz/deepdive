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

psql -c """CREATE TABLE mention(
	id bigserial primary key,
	doc_id text,
	sentence_id bigserial,
	text_contents text,
	type text);""" $DB_NAME

psql -c """COPY mention(doc_id, sentence_id, text_contents, type) FROM
	'$BASE_DIR/data/mention/mentions.csv' DELIMITER E'\t' CSV;""" $DB_NAME

psql -c """CREATE TABLE entity(
	id bigserial primary key,
	eid text not null unique,
	text_contents text,
	type text);""" $DB_NAME

# load the entity table
psql -f $BASE_DIR/data/entity/entity.sql $DB_NAME

# mapping between entity id given by KBP and freebase id used in entity() table
psql -c """CREATE TABLE eid_to_fid(
	fid text primary key,
	eid text not null unique references entity(eid),
	text_contents text,
	types text);""" $DB_NAME

# mapping between query id and mention id
psql -c """CREATE TABLE qid_to_mid(
	
	);""" $DB_NAME

psql -c """COPY eid_to_fid FROM '$BASE_DIR/data/entity/eid_to_fid.tsv'
	DELIMITER E'\t' CSV;""" $DB_NAME

# stores not necessarily unique (e, m) pairs that could be linked
# based on our predicates
psql -c """CREATE TABLE candidate_link(
	id bigserial primary key,
	eid text references entity(id),
	mid bigserial references mention(id));""" $DB_NAME

# whether or not the entity and mention are linked, and the feature type for that link
psql -c """CREATE TABLE link_feature(
	id bigserial primary key,
	eid text references entity(id),
	mid bigserial references mention(id),
	feature_type text,
	is_correct boolean);""" $DB_NAME
