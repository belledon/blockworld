#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ROOT="$(dirname $DIR)"
export PYTHONPATH=$ROOT
SCRIPT="${ROOT}/tests/$1"
shift

CONT="${ROOT}/singularity/env.simg"

singularity exec $CONT python3 $SCRIPT "$@"


