#! /bin/bash

cd "$(dirname $0)/../..";
ROOT_PATH=`pwd`

# run the KBP-provided evaluation script against the generated output
perl ../helper_scripts/kbpenteval.pl ../evaluation/output/... ../evaluation/output/...