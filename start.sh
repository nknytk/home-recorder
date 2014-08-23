#!/bin/bash

HRHOME=`dirname $0`
PYTHON="/usr/bin/python3"

sudo ${PYTHON} ${HRHOME}/app/home-recorder.py >> ${HRHOME}/log.log 2>&1 & disown
