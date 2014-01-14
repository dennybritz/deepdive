#! /bin/bash

# Configuration
DB_NAME=deepdive_kbp
DB_USER=
DB_PASSWORD=

cd `dirname $0`
BASE_DIR=`pwd`

dropdb deepdive_kbp
createdb deepdive_kbp

psql -c "drop schema if exists public cascade; create schema public;" $DB_NAME

psql -c "create type valid_feature_type as enum ('PERSON');" $DB_NAME

psql -c "create table mention(id bigserial primary key, doc_id text, sentence_id bigserial, feature_type valid_feature_type, text_contents text);" $DB_NAME
psql -c "create table mention_features(id bigserial primary key references mention(id), word_count integer);" $DB_NAME