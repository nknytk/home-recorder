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
        """this method is diretry called by home-recorder"""
        self.recorder_thread = Thread(target=self.record, args=(eventid, duration))
        self.recorder_thread.start()

    def join(self, timeout=None):
        self.recorder_thread.join(timeout)

    def record(self, eventid, duration):
        """
        Call snapshot() for duration in every interval sec.
        This method runs in another thread to enable prallel recording.
        Entirely override record() if you want non-snapshot type recording.
        """
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
        """
        Override this to record to take a snapshot
        e.g. read thermometer for every 1 second.
        """
        pass
