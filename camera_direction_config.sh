#!/bin/bash

HRHOME=`dirname $0`
PYTHON="/usr/bin/python3"
PORT="8071"

get_ipaddr(){
  is_public_addr=0
  ip -f inet addr | while read line; do
    if [[ ${is_public_ipaddr} -eq 1 || -n "$(echo ${line} | egrep " eth0| wlan0| em0")" ]]; then
      is_public_addr=1
    else
      continue
    fi
    if [ -n "$(echo ${line} | egrep "^inet ")" ]; then
      ipaddr=$(echo ${line} | sed "s/^inet \([^ \/]*\)\/.*$/\1/")
      echo ${ipaddr}
      return
    fi
  done
}

PID=$(ps aux | grep "${HRHOME}/app/home-recorder.py" | grep -v grep | awk '{print $2}')
if [ -n "${PID}" ]; then
  echo "You need to stop home-recorder before camera direction adjustment."
  exit 1
fi

IPADDR=`get_ipaddr`
${PYTHON} ${HRHOME}/app/htmlcamera.py ${PORT} > /dev/null 2>&1 & disown
PID=$(echo $!)

echo "Started web camera server. Access"
echo "    http://${IPADDR}:${PORT}"
echo "with your browser, and adjust camera direction."
echo
echo "Press Enter to finish web camera server."
read
kill ${PID}
echo "Finish."
