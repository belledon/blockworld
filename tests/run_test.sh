#!/bin/bash

. /etc/os-release
OS=$NAME

ROOT="$( git rev-parse --show-toplevel )"
if [ "$OS" = "CentOS Linux" ]; then
    ROOT="$( echo ${ROOT#/net/storage001.ib.cluster})"
    module add openmind/singularity
fi

BASE="$(echo "$ROOT" | cut -d "/" -f2)"
export PYTHONPATH=$ROOT
PREFIX="$( git rev-parse --show-prefix )"
SCRIPT="${ROOT}/${PREFIX}/$1"
shift

CONT="${ROOT}/singularity/env.simg"

singularity exec -B "/$BASE:/$BASE" $CONT python3 $SCRIPT "$@"


