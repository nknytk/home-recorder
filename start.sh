#!/bin/bash

PYTHON="/usr/bin/python3"

WEBCAM_PKG="`dpkg -l | grep webcam | awk '{if($2=="webcam"){print $0}}'`"
if [ -z "${WEBCAM_PKG}" ]; then
    sudo apt-get install webcam
fi

HRHOME=`dirname $0`

sudo ${PYTHON} ${HRHOME}/app/home-recorder.py
#> ${HRHOME}/log.log 2>&1
