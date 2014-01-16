#! /bin/bash

cd "$(dirname $0)/../..";
ROOT_PATH=`pwd`

#cd examples/kbp

# process entity and mention raw data; output csv files
#python generate_csv.py

#cd ../..

$ROOT_PATH/examples/kbp/prepare_data.sh
env SBT_OPTS="-Xmx4g" sbt "run -c examples/kbp/application.conf"
