# coding: utf-8

import os
import sys
import shutil
from time import sleep, time
from threading import Thread

from .recorderthread import  RecorderThread
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from lamearecord import avail_mikes, record_mp3


class Mike(RecorderThread):
    def record(self, eventid, duration):
        storage = os.path.join(self.datadir, eventid)
        if os.path.exists(storage):
            shutil.rmtree(storage)
        os.makedirs(storage)
        self.storage = storage

        mike_threads = []
        devices = self.setting['devices'] if self.setting.get('devices') else avail_mikes()
        for dev in devices:
            th = Thread(target=self.rec_sound, args=(duration, dev))
            th.start()
            mike_threads.append(th)

        for th in mike_threads:
            th.join()

    def rec_sound(self, duration, devicename):
        tmpfile = os.path.join(self.storage, '.' + devicename + '.mp3')
        soundfile = os.path.join(self.storage, devicename + '.mp3')
        record_mp3(devicename, duration, tmpfile)
        if os.path.exists(tmpfile):
            os.rename(tmpfile, soundfile)
