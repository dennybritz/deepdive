#! /bin/bash

cd "$(dirname $0)/../..";
ROOT_PATH=`pwd`

# prepare the database: create and load tables
$ROOT_PATH/examples/kbp/prepare_data.sh

cd $ROOT_PATH/examples/kbp
insert_examples_into_candidate_table.sh
cd $ROOT_PATH

env SBT_OPTS="-Xmx4g" sbt "run -c examples/kbp/application.conf"