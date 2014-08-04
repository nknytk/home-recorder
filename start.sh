#!/bin/bash

PYTHON="/usr/bin/python3"
DEPENDANCIES="webcam python3-pip"

for pkg in ${DEPENDANCIES}; do
  dpkg -l ${pkg} > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    sudo apt-get install ${pkg}
  fi
done

${PYTHON} -c "import PIL"
if [ $? -ne 0 ]; then
  python_ver=`${PYTHON} -V 2>&1 | cut -d" " -f2 | cut -d"." -f1,2`
  sudo pip-${python_ver} install Pillow
fi

HRHOME=`dirname $0`

sudo ${PYTHON} ${HRHOME}/app/home-recorder.py
#> ${HRHOME}/log.log 2>&1
