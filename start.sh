#!/bin/bash

HRHOME=`dirname $0`
PYTHON="/usr/bin/python3"
DEPENDANCIES="webcam python3-pip libjpeg8-dev"

for pkg in ${DEPENDANCIES}; do
  dpkg -l ${pkg} > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    sudo apt-get install ${pkg}
  fi
done

if [ ! -f /usr/lib/libjpeg.so ]; then
  sudo ln -s /usr/lib/arm-linux-gnueabihf/libjpeg.so /usr/lib/
fi

${PYTHON} -c "import PIL"
if [ $? -ne 0 ]; then
  python_ver=`${PYTHON} -V 2>&1 | cut -d" " -f2 | cut -d"." -f1,2`
  sudo pip-${python_ver} install Pillow
fi

sudo ${PYTHON} ${HRHOME}/app/home-recorder.py >> ${HRHOME}/log.log 2>&1 & disown
