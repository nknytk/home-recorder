# coding: utf-8

import os
from threading import Thread
from time import sleep, time

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from pluginbase import PluginBase


class RecorderThread(PluginBase):
    def __init__(self):
        self.modtype = 'recorder'
        super().__init__()

    def start_recording(self, eventid, duration):
        self.recorder_thread = Thread(target=self.record, args=(eventid, duration))
        self.recorder_thread.start()

    def join(self):
        self.recorder_thread.join()

    def record(self, eventid, duration):
        finishtime = time() + duration

        while time() < finishtime:
            next = time() + self.setting.get('interval', 1)

            self.snapshot(eventid)

            if next <= finishtime:
                now = time()
                if next - now > 0:
                    sleep(next - now)
            else:
                break

    def snapshot(self, eventid):
        pass
