#! /bin/bash

cd "$(dirname $0)/../..";
ROOT_PATH=`pwd`

# prepare the database: create and load tables
$ROOT_PATH/examples/kbp/prepare_data.sh

env SBT_OPTS="-Xmx4g" sbt "run -c examples/kbp/application.conf"

# produce a calibration plot
#$ROOT_PATH/examples/kbp/helper_scripts/calibrate.sh