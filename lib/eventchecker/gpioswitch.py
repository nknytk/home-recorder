# coding: utf-8

from time import time
from RPi import GPIO
from .pichecker import EventCheckerBase

class GPIOSwitch(EventCheckerBase):
    def __init__(self):
        EventCheckerBase.__init__(self)

        self.OPEN = GPIO.HIGH
        self.CLOSED = GPIO.LOW
        GPIO.setmode(GPIO.BOARD)
        self.sensor_status = {
            # Resereved for control switches
            #11: 0, # GPIO17
            #13: 0, # R1:GPIO21, R2:GPIO27
            15: 0, # GPIO22
            16: 0, # GPIO23
            18: 0, # GPIO24
            22: 0  # GPIO25
        }
        for pin in self.sensor_status:
            GPIO.setup(pin, GPIO.IN)

        self.update()
        self.INITIALIZED = time()
        self.lastupdate = self.INITIALIZED

    def update(self):
        # Update status of all sensors
        updates = {}
        for pin in self.sensor_status:
            newstatus = GPIO.input(pin)
            if newstatus != self.sensor_status[pin]:
                updates[pin] = newstatus
                self.sensor_status[pin] = GPIO.input(pin)
        self.lastupdate = time()
        return updates

    def cleanup(self):
        GPIO.cleanup()

    def check(self):
        diff = self.update()

        if self.setting['check_open_only']:
            event_pins = []
            for pin, status in diff.items():
                if status == self.OPEN:
                    event_pins.append(pin)

        else:
           event_pins = sorted(diff.keys())

        if not event_pins:
            return (False, 'No change from last check.')

        event_pins = [str(p) for p in event_pins]
        msg = 'Status of pin ' + ', '.join(event_pins) + ' changed.'
        return (True, msg, [])


if __name__ == '__main__':
    from time import sleep
    P = GPIOSwitch()
    while True:
        print(P.check())
        sleep(3)
