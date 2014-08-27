# coding: utf-8

import os
import sys
import shutil
from time import sleep, time
from threading import Thread

from .recorderthread import  RecorderThread
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from webcam import avail_cameras, capture, write_webcam_config


class Camera(RecorderThread):
    def record(self, eventid, duration):
        storage = os.path.join(self.datadir, eventid)
        if os.path.exists(storage):
            shutil.rmtree(storage)

        self.confs = {}
        camera_threads = []
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
            self.confs[devname] = conf_file

            camera_threads.append(Thread(target=self.run_camera, args=(devname, duration)))

        for th in camera_threads:
            th.start()
        for th in camera_threads:
            th.join()

    def run_camera(self, devname, duration):
        finishtime = time() + duration

        while time() < finishtime:
            next = time() + self.setting.get('interval', 1)

            capture(self.confs[devname])
            print('Captured image with ' + devname)

            if next <= finishtime:
                now = time()
                if next - now > 0:
                    sleep(next - now)
            else:
                break


if __name__ == '__main__':
    w = Camera()
    w.start_recording('test', 10)
    w.join()
