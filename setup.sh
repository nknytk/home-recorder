#!/bin/bash

HRHOME=`dirname $0`
PYTHON="/usr/bin/python3"
DEPENDANCIES="webcam lame python3-pip libjpeg8-dev"

for pkg in ${DEPENDANCIES}; do
  dpkg -l ${pkg} > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    sudo apt-get install -y ${pkg}
  fi
done

# for arm linux
if [ ! -f /usr/lib/libjpeg.so ]; then
  sudo ln -s /usr/lib/arm-linux-gnueabihf/libjpeg.so /usr/lib/
fi

${PYTHON} -c "import PIL"
if [ $? -ne 0 ]; then
  if [ -n "$(which pip3)" ]; then
    python3pip=pip3
  else
    python_ver=`${PYTHON} -V 2>&1 | cut -d" " -f2 | cut -d"." -f1,2`
    python3pip=pip-${python_ver}
  fi
  sudo ${python3pip} install Pillow
fi

echo
echo "setup finished."
