# coding: utf-8

import os
import shlex
import subprocess
from copy import deepcopy
from PIL import Image

from .eventcheckerbase import EventCheckerBase

class SimpleMotion(EventCheckerBase):
    default_webcam_conf = {
        "fg_red": "255",
        "fg_green": "255",
        "fg_blue": "255",
        "width": "320",
        "height": "240",
        "delay": "0",
        "wait": "0",
        "rotate": "0",
        "top": "0",
        "left": "0",
        "bottom": "-1",
        "right": "-1",
        "quality": "90",
        "trigger": "0",
        "once": "1"
    }

    def __init__(self):
        EventCheckerBase.__init__(self)

        self.confs = [self.write_webcam_config(i) for i in range(self.setting['num_of_camera'])]
        divnum = self.setting['num_of_points'] + 1
        width = int(self.setting.get('width', self.default_webcam_conf['width']))
        height = int(self.setting.get('height', self.default_webcam_conf['height']))
        self.target_pixels = []
        for i in range(1, divnum):
            for j in range(1, divnum):
                self.target_pixels.append((int(i * width/divnum), int(j * height/divnum)))

        self.filenames = []
        self.prev_pxls = []
        for i in range(self.setting['num_of_camera']):
            self.filenames.append({
                'newest': os.path.join(self.setting['tmpdir'], str(i) + '.jpg'),
                'previous': os.path.join(self.setting['tmpdir'], str(i) + '_prev.jpg'), 
            })
            pxs = self.getpixels(i)
            self.prev_pxls.append([pxs, pxs])

    def check(self):
        event_occurred = False
        event_devices = []
        files = []

        for i in range(self.setting['num_of_camera']):
            os.rename(self.filenames[i]['newest'], self.filenames[i]['previous'])
            new_pxls = self.getpixels(i)
            if self.diffsize(new_pxls, self.prev_pxls[i][0]) > self.setting['diff_threshold'] \
               and self.diffsize(new_pxls, self.prev_pxls[i][1]) > self.setting['diff_threshold']:
               event_occurred = True
               event_devices.append(str(i))
               files.append(self.filenames[i]['previous'])
               files.append(self.filenames[i]['newest'])
            del(self.prev_pxls[i][1])
            self.prev_pxls[i].insert(0, new_pxls)

        if event_devices:
            msg = 'Camera %s detected motion event. See attached images.' % ','.join(event_devices)
        else:
            msg = 'No motion event.'
        return (event_occurred, msg, files)
            

    def getpixels(self, device_num):
        command = shlex.split('webcam ' + self.confs[device_num])
        with open('/dev/null', 'w') as dn:
            subprocess.call(command, stdout=dn, stderr=dn)
        img = Image.open(self.filenames[device_num]['newest'])
        pxs = [img.getpixel(cood) for cood in self.target_pixels]
        img.close()
        return pxs

    def diffsize(self, pxs1, pxs2):
        ds = 0
        for v1, v2 in zip(pxs1, pxs2):
            ds += abs(v1[0] - v2[0]) + abs(v1[1] - v2[1]) + abs(v1[2] - v2[2])
        return ds * 100 / (255 * 3 * len(pxs1))

    def write_webcam_config(self, device_num):
        conf = deepcopy(self.default_webcam_conf)
        conf['device'] = '/dev/video%d' % device_num
        conf['text']  = 'webcam' + str(device_num)
        conf['archive'] = os.path.join(self.setting['tmpdir'], str(device_num) + '.jpg')

        for conf_key in self.setting:
            if conf_key in conf:
                conf[conf_key] = self.setting[conf_key]

        filename = os.path.join(self.datadir, 'webcam%d.conf' % device_num)
        with open(filename, mode='w', encoding='utf-8') as f:
            f.write('[grab]\n')
            f.write('\n'.join([p + ' = ' + str(v) for p, v in conf.items()]))

        return filename

if __name__ == '__main__':
    from time import sleep
    C = SimpleMotion()
    while True:
        C.check()
        sleep(1)
