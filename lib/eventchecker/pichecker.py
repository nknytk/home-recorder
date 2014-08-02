# coding: utf-8

from RPi import GPIO
from .eventcheckerbase import EventCheckerBase

class PiChecker(EventCheckerBase):
    pinno = 13

    def __init__(self):
        EventCheckerBase.__init__(self)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pinno, GPIO.IN)

    def shoud_check(self):
        if GPIO.input(self.pinno) == GPIO.HIGH:
            return True
        else:
            return False
