# coding: utf-8

import os
import shlex
import subprocess
from copy import deepcopy

DEFAULT_CONF = {
    'device': '/dev/video0',
    'text': 'webcam 0',
    'fg_red': '255',
    'fg_green': '255',
    'fg_blue': '255',
    'width': '640',
    'height': '480',
    'delay': '0',
    'wait': '0',
    'rotate': '0',
    'top': '0',
    'left': '0',
    'bottom': '-1',
    'right': '-1',
    'quality': '90',
    'trigger': '0',
    'once': '1',
    'archive': '/tmp/webcam.jpg'
}

def avail_cameras():
    devices = []
    for dev in os.listdir('/dev/'):
        if dev.startswith('video'):
            devices.append('/dev/' + dev)
    return devices

def capture(conf_file):
    command = shlex.split('webcam ' + conf_file)
    with open('/dev/null', 'w') as devnull:
        subprocess.call(command, stdout=devnull, stderr=devnull)

def write_webcam_config(override_conf, conf_file='/tmp/webcam.conf'):
    conf = deepcopy(DEFAULT_CONF)
    conf.update(override_conf)
    with open(conf_file, mode='w', encoding='utf-8') as f:
        f.write('[grab]\n')
        f.write('\n'.join([p + ' = ' + str(v) for p, v in conf.items()]))
