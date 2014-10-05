# coding: utf-8

import os
import sys
from threading import Thread
from PIL import Image

from .eventcheckerbase import EventCheckerBase
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../util'))
from webcam import avail_cameras, capture, write_webcam_config

class Camera(EventCheckerBase):
    def __init__(self):
        super().__init__()

        self.diff_thresh =  self.setting.get('diff_threshold', 0.2)
        if not 0 < self.diff_thresh < 1:
            raise ValueError('diff_threshold must be between 0 and 1')

        self.devices = self.setting['devices'] if self.setting.get('devices') else avail_cameras()
        self.width = int(self.setting.get('width', 320))
        self.height = int(self.setting.get('height', 240))
        self.max_vector_len = (255**2 * 3)**(1/2)
        self.target_pixels = []
        divnum = self.setting.get('num_of_points', 10) + 1
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
            if os.path.isfile(self.filenames[devname]['newest']):
                os.remove(self.filenames[devname]['newest'])
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
            diffs = sorted(self.diffsizes(devname), reverse=True)
            if diffs[int(len(diffs)*0.1)] < self.diff_thresh:
                continue
            diffs = sorted(self.diffsizes(devname, 1), reverse=True)
            if diffs[int(len(diffs)*0.1)] < self.diff_thresh:
                continue

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

    def diffsizes(self, devname, offset=0):
        diff_sizes = []
        for v1, v2 in zip(self.pxls[devname][offset], self.pxls[devname][offset+1]):
            vector_size = ((v1[0]-v2[0])**2 + (v1[1]-v2[1])**2 + (v1[2]-v2[2])**2)**(1/2)
            relative_size = vector_size / self.max_vector_len
            diff_sizes.append(relative_size)
        return diff_sizes


if __name__ == '__main__':
    from time import sleep
    C = Camera()
    while True:
        C.check()
        sleep(1)
