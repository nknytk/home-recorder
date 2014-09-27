# coding: utf-8

from json import dumps
from RPi import GPIO

PINs = [11, 13, 15, 16, 18, 22]

GPIO.setmode(GPIO.BOARD)
for pin in PINs:
   GPIO.setup(pin, GPIO.IN)


def pinstatus(env):
    status = {}
    for pin in PINs:
        if GPIO.input(pin) == GPIO.HIGH:
            status[pin] = 'HIGH'
        else:
            status[pin] = 'LOW'

    res = bytes(dumps(status), 'utf-8')
    header = [('Content-Type', 'application/json'),
              ('Content-Length', str(len(res)))]
    return header, res
