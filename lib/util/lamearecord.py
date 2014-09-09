# coding: utf-8

import os
import re
import shlex
from subprocess import Popen, PIPE


def available_devices():
    devices =[]

    os.environ['LANG'] = 'C'
    command = 'arecord -l'
    arecord_l = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE)
    arecord_l.wait()

    if arecord_l.returncode != 0:
        print(arecord_l.stderr.read())
        return devices

    for line in arecord_l.stdout.readlines():
        m = re.match('^card ([0-9]): .*, device ([0-9]): .*$', line.decode('utf-8'))
        if not m:
            continue

        card = m.group(1)
        device = m.group(2)
        if card and device:
            devices.append('hw:%s,%s' % (card, device))

    return devices

def record_wav(hw_id, duration, filename):
    command = 'arecord -D %s -f S16_LE -d %d %s' % (hw_id, duration, filename)
    call(shlex.split(command))
