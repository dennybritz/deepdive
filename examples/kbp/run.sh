#! /bin/bash

cd "$(dirname $0)/../..";
ROOT_PATH=`pwd`

# generate the qid_to_mid mapping
cd $ROOT_PATH/examples/kbp/helper_scripts
python generate_qid_to_mid.py
cd $ROOT_PATH

# prepare the database: create and load tables
$ROOT_PATH/examples/kbp/prepare_data.sh

# load the training data and evaluation queries
$ROOT_PATH/examples/kbp/helper_scripts/load_training_data.sh
$ROOT_PATH/examples/kbp/helper_scripts/load_eval_queries.sh

env SBT_OPTS="-Xmx4g" sbt "run -c examples/kbp/application.conf"

# run the evaluation script
$ROOT_PATH/examples/kbp/helper_scripts/evaluate_system.sh