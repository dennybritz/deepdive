#! /bin/bash

cd "$(dirname $0)/../..";
ROOT_PATH=`pwd`

# run calibration script and put plot into examples/kbp/output
python $ROOT_PATH/examples/tools/cali.py $ROOT_PATH/target/calibration/link_feature.is_correct.tsv $ROOT_PATH/output/kbp_calibration.png