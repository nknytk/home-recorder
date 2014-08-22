#!/bin/bash

HRHOME=`dirname $0`

PID=$(ps aux | grep "${HRHOME}/app/home-recorder.py" | grep -v grep | awk '{print $2}')
sudo kill -KILL ${PID}
