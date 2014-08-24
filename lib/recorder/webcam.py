# coding: utf-8

import os
import sys
import shutil

from .recorderthread import  RecorderThread
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from webcam import avail_cameras, capture, write_webcam_config


class Webcam(RecorderThread):
    def record(self, eventid, duration):
        storage = os.path.join(self.datadir, eventid)
        if os.path.exists(storage):
            shutil.rmtree(storage)

        self.confs = []
        devices = self.setting['devices'] if self.setting.get('devices') else avail_cameras()
        for dev in devices:
            devname = dev.split('/')[-1]
            conf = {
                'device': dev,
                'text': '%Y-%m-%d %H:%M:%S ' + devname,
                'archive': os.path.join(storage, devname + '_%H:%M:%S.jpg')
            }
            if self.setting.get('width'):
                conf['width'] = self.setting['width']
            if self.setting.get('height'):
                conf['height'] = self.setting['height']

            conf_file = os.path.join(self.datadir, devname + '.conf')
            write_webcam_config(conf, conf_file)
            self.confs.append(conf_file)

        RecorderThread.record(self, eventid, duration)

    def snapshot(self, eventid):
        for conf in self.confs:
            capture(conf)
        print('Captured image.')


if __name__ == '__main__':
    w = Webcam()
    w.start_recording('test', 10)
    w.join()
