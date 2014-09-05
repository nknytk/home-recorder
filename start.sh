#!/bin/bash

HRHOME=`dirname $0`
PYTHON="/usr/bin/python3"

PID=$(ps aux | grep "${HRHOME}/app/home-recorder.py" | grep -v grep | awk '{print $2}')
if [ -n "${PID}" ]; then
  echo "home-recorder is already running."
  exit 1
fi

if [ "$1" == "test" ]; then
  sudo ${PYTHON} ${HRHOME}/app/home-recorder.py test
else
  sudo ${PYTHON} -u ${HRHOME}/app/home-recorder.py >> ${HRHOME}/log.log 2>&1 & disown
fi
