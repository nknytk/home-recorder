#!/bin/bash

HRHOME=`dirname $0`

PID=$(ps aux | grep "${HRHOME}/app/home-recorder.py" | grep -v grep | awk '{print $2}')
if [ -n "${PID}" ]; then
  sudo kill ${PID}
else
  exit 0
fi

sleep 1

if [ -n "$(ps -p ${PID} | grep -v "PID")" ]; then
  sudo kill -KILL ${PID}
fi
