# coding: utf-8

import os
import sys
from threading import Thread
from PIL import Image

from .eventcheckerbase import EventCheckerBase
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../util'))
from webcam import avail_cameras, capture, write_webcam_config

class SimpleMotion(EventCheckerBase):
    def __init__(self):
        EventCheckerBase.__init__(self)

        self.devices = self.setting['devices'] if self.setting.get('devices') else avail_cameras()
        self.width = int(self.setting.get('width', 320))
        self.height = int(self.setting.get('height', 240))
        self.target_pixels = []
        divnum = self.setting['num_of_points'] + 1
        for i in range(1, divnum):
            for j in range(1, divnum):
                self.target_pixels.append((int(i * self.width/divnum), int(j * self.height/divnum)))

        self.reset()

    def reset(self):
        self.filenames = {}
        self.pxls = {}
        for dev in self.devices:
            devname = dev.split('/')[-1]
            self.filenames[devname] = {
                'newest': os.path.join(self.setting.get('tmpdir', '/run/shm'), devname + '.jpg'),
                'previous': os.path.join(self.setting.get('tmpdir', '/run/shm'), devname + '_prev.jpg'), 
            }
            self.pxls[devname] = []
            self.update_pixels(devname)
            self.pxls[devname].append(self.pxls[devname][0])

    def check(self):
        event_occurred = False
        event_devices = []
        files = []

        camera_threads = {}
        devnames = [dev.split('/')[-1] for dev in self.devices]
        for devname in devnames:
            th = Thread(target=self.update_pixels, args=(devname, ))
            th.start()
            camera_threads[devname] = th

        for devname in devnames:
            camera_threads[devname].join()
            if self.diffsize(self.pxls[devname][0], self.pxls[devname][1]) > self.setting['diff_threshold'] \
               and self.diffsize(self.pxls[devname][0], self.pxls[devname][2]) > self.setting['diff_threshold']:
               event_occurred = True
               event_devices.append(devname)
               files.append(self.filenames[devname]['previous'])
               files.append(self.filenames[devname]['newest'])

        if event_devices:
            msg = '%s detected motion event. See attached images.' % ','.join(event_devices)
        else:
            msg = 'No motion event.'
        return (event_occurred, msg, files)

    def update_pixels(self, devname):
        if len(self.pxls[devname]) > 2:
            del(self.pxls[devname][2])
            os.rename(self.filenames[devname]['newest'], self.filenames[devname]['previous'])

        conffile = os.path.join(self.setting.get('tmpdir', '/run/shm'), devname + '.conf')
        conf = {
            'width': self.width,
            'height': self.height,
            'device': '/dev/' + devname,
            'archive': self.filenames[devname]['newest']
        }
        write_webcam_config(conf, conffile)
        capture(conffile)

        img = Image.open(self.filenames[devname]['newest'])
        pxs = [img.getpixel(cood) for cood in self.target_pixels]
        img.close()
        self.pxls[devname].insert(0, pxs)

    def diffsize(self, pxs1, pxs2):
        ds = 0
        for v1, v2 in zip(pxs1, pxs2):
            ds += abs(v1[0] - v2[0]) + abs(v1[1] - v2[1]) + abs(v1[2] - v2[2])
        return ds * 100 / (255 * 3 * len(pxs1))


if __name__ == '__main__':
    from time import sleep
    C = SimpleMotion()
    while True:
        C.check()
        sleep(1)
