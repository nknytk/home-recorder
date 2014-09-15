# coding: utf-8

import os
import sys
from json import dumps

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../util'))
from webcam import avail_cameras
from lamearecord import avail_mikes

ALL_FEATURES = {
    'camera': 'View camera images',
    'mike': 'Listen to mike sound',
    'gpio': 'View GPIO pins\' values',
    'gcm': 'Receive notification with GCM'
}


def available(env):
    available_features = []
    if avail_cameras():
        available_features.append(('camer', ALL_FEATURES['camera']))
    if avail_mikes():
        available_features.append(('mike', ALL_FEATURES['mike']))
    try:
        import RPi.GPIO
        available_features.append(('gpio', ALL_FEATURES['gpio']))
    except:
        pass
    available_features.append(('gcm', ALL_FEATURES['gcm']))

    res = bytes(dumps(available_features), 'utf-8')
    header = [('Content-Type', 'application/json'),
              ('Content-Length', str(len(res)))]
    return header, res
