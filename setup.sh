#!/bin/bash

HRHOME=`dirname $0`
PYTHON="/usr/bin/python3"
DEPENDANCIES="webcam lame python3-pip libjpeg8-dev"
PIP_DEPENDANCIES="Pillow requests"

for pkg in ${DEPENDANCIES}; do
  dpkg -l ${pkg} > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    sudo apt-get install -y ${pkg}
  fi
done

# for arm linux
if [ ! -f /usr/lib/libjpeg.so ] && [ -f /usr/lib/arm-linux-gnueabihf/libjpeg.so ]; then
  sudo ln -s /usr/lib/arm-linux-gnueabihf/libjpeg.so /usr/lib/
fi

if [ -n "$(which pip3)" ]; then
  python3pip=pip3
else
  python_ver=`${PYTHON} -V 2>&1 | cut -d" " -f2 | cut -d"." -f1,2`
  python3pip=pip-${python_ver}
fi
sudo ${python3pip} install ${PIP_DEPENDANCIES}

echo
echo "setup finished."
