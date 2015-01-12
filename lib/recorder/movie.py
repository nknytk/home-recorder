# coding: utf-8

import os
import sys
import shutil
import shlex
from subprocess import call
from threading import Thread

from .recorderthread import  RecorderThread
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from webcam import avail_cameras


class Movie(RecorderThread):
    base_command = 'avconv -f video4linux2 -timelimit %d -s %s -r %d -i %s %s'

    def record(self, eventid, duration):
        storage = os.path.join(self.datadir, eventid)
        if os.path.exists(storage):
            shutil.rmtree(storage)
        os.makedirs(storage)
        self.storage = storage

        movie_threads = []
        devices = self.setting['devices'] if self.setting.get('devices') else avail_cameras()
        for dev in devices:
            th = Thread(target=self.rec_video, args=(duration, dev))
            th.start()
            movie_threads.append(th)

        for th in movie_threads:
            th.join()

    def rec_video(self, duration, device):
        if device.startswith('/dev/'):
            devicename = device.split('/')[-1]
            devicepath = device
        else:
            devicename = device
            devicepath = os.path.join('/dev', device)
        tmpfile = os.path.join(self.storage, '.' + devicename + '.avi')
        videofile = os.path.join(self.storage, devicename + '.avi')

        if self.setting.get('width') and self.setting.get('height'):
            size = '%dx%d' % (self.setting['width'], self.setting['height'])
        else:
            size = '640x480'
        fps = self.setting.get('frame_rate', 10)

        comm = self.base_command % (duration, size, fps, devicepath, tmpfile)
        call(shlex.split(comm))
        if os.path.exists(tmpfile):
            os.rename(tmpfile, videofile)
