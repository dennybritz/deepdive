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

psql -c """CREATE TABLE candidate_link(
	id bigserial primary key,
	eid text references entity(eid),
	mid bigserial references mention(id),
	is_correct boolean);""" $DB_NAME

# the feature type for the entity-mention link
psql -c """CREATE TABLE link_feature(
	id bigserial primary key,
	eid text references entity(eid),
	mid bigserial references mention(id),
	feature_type text);""" $DB_NAME
