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

# the mention data + features
psql -c """CREATE TABLE mention(
	id bigserial primary key,
	doc_id text,
	sentence_id bigserial,
	text_contents text,
	type text);""" $DB_NAME

psql -c """CREATE TABLE mention_features(
	id bigserial primary key,
	mid bigserial references mention(id),
	text_lc text);""" $DB_NAME

# the entity data + features
psql -c """CREATE TABLE entity(
	id text primary key,
	type text,
	text_contents text);""" $DB_NAME

psql -c """CREATE TABLE entity_features(
	id bigserial primary key,
	eid text references entity(id),
	text_lc text);""" $DB_NAME

# stores not necessarily unique (e, m) pairs that could be linked
# based on our string matching feature
psql -c """CREATE TABLE candidate_link_exact_match(
	id bigserial primary key,
	eid text references entity(id),
	mid bigserial references mention(id),
	feature_type text);""" $DB_NAME

# whether or not the entity and mention are linked
psql -c """CREATE TABLE link(
	id bigserial primary key,
	eid text references entity(id),
	mid bigserial references mention(id),
	is_correct boolean);""" $DB_NAME

psql -c """COPY mention(doc_id, sentence_id, text_contents, type) FROM
	'$BASE_DIR/data/newswire/kbp_mentions_nw.csv' DELIMITER E'\t' CSV;""" $DB_NAME

psql -c """COPY entity(id, type, text_contents) FROM
	'$BASE_DIR/data/freebase/kbp_entities_fb.csv' DELIMITER E'\t' CSV;""" $DB_NAME