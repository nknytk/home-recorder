# coding: utf-8

import os
import re
import shlex
from subprocess import Popen, PIPE, call, check_output


def avail_mikes():
    devices =[]

    os.environ['LANG'] = 'C'
    command = 'arecord -l'
    arecord_l = Popen(shlex.split(command), stdout=PIPE)
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
    if not filename.endswith('.wav'):
        filename += '.wav'
    command = 'arecord -D plug%s -f S16_LE -d %d %s' % (hw_id, duration, filename)
    call(shlex.split(command))

def record_mp3(hw_id, duration, filename):
    if not filename.endswith('.mp3'):
        filename += '.mp3'
    arecord_comm = 'arecord -D plug%s -f S16_LE -d %d -' % (hw_id, duration)
    lame_comm = 'lame -V2 - ' + filename

    check_output('%s | %s' % (arecord_comm, lame_comm), shell=True)
