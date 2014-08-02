# coding: utf-8

import os
from json import loads
from threading import Thread
from time import sleep, time

class RecorderThread:
    def __init__(self):
        objname = self.__str__()
        endidx = objname.find(' object at ')
        startidx = objname.rfind('.', 0, endidx) + 1
        self.recorder_name = objname[startidx:endidx].lower()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.homedir = os.path.join(current_dir, '../../')
        self.datadir = os.path.join(self.homedir, 'data', 'recorder', self.recorder_name)
        if not os.path.exists(self.datadir):
            os.makedirs(os.path.abspath(self.datadir))

        common_conf = os.path.join(self.homedir, 'conf/common/%s.json' % self.recorder_name)
        recorder_conf = os.path.join(self.homedir, 'conf/recorder/%s.json' % self.recorder_name)
        conf = common_conf if os.path.isfile(common_conf) else recorder_conf
        with open(conf, encoding='utf-8') as f:
            self.setting = loads(f.read())
        
    def start_recording(self, eventid, duration):
        self.recorder_thread = Thread(target=self.record, args=(eventid, duration))
        self.recorder_thread.start()

    def join(self):
        self.recorder_thread.join()

    def record(self, eventid, duration):
        finishtime = time() + duration

        while time() < finishtime:
            next = time() + self.setting['interval']

            self.snapshot(eventid)

            if next <= finishtime:
                now = time()
                if next - now > 0:
                    sleep(next - now)
            else:
                break

    def snapshot(self, eventid):
        pass
