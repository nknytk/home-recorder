# coding: utf-8

import os
import shlex
import shutil
import subprocess
from copy import deepcopy

from .recorderthread import  RecorderThread

class Webcam(RecorderThread):
    default_webcam_conf = {
        "fg_red": "255",
        "fg_green": "255",
        "fg_blue": "255",
        "width": "640",
        "height": "480",
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

    def record(self, eventid, duration):
        storage = os.path.join(self.datadir, eventid)
        if os.path.exists(storage):
            shutil.rmtree(storage)
        self.confs = []

        for i in range(self.setting['num_of_camera']):
            self.confs.append(self.write_webcam_config(eventid, i))

        self.devnull = open('/dev/null', mode='w')
        RecorderThread.record(self, eventid, duration)
        self.devnull.close()

    def snapshot(self, eventid):
        for conf in self.confs:
            command = shlex.split('webcam ' + conf)
            print('Recorded picture with webcam')
            subprocess.call(command, stdout=self.devnull, stderr=self.devnull)

    def write_webcam_config(self, eventid, device_num):
        conf = deepcopy(self.default_webcam_conf)
        conf['device'] = '/dev/video%d' % device_num
        conf['text']  = '%Y-%m-%d %H:%M:%S webcam' + str(device_num)
        conf['archive'] = os.path.join(self.datadir, eventid,
                                       '%H:%M:%S_' + str(device_num) + '.jpg')

        for conf_key in self.setting:
            if conf_key in conf:
                conf[conf_key] = self.setting[conf_key]

        filename = os.path.join(self.datadir, 'webcam%d.conf' % device_num)
        with open(filename, mode='w', encoding='utf-8') as f:
            f.write('[grab]\n')
            f.write('\n'.join([p + ' = ' + str(v) for p, v in conf.items()]))

        return filename

if __name__ == '__main__':
    w = Webcam()
    w.start_recording('test', 10)
    w.join()
