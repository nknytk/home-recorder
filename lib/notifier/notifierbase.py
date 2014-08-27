# coding: utf-8

import os
from json import loads

class NotifierBase:
    def __init__(self):
        objname = self.__str__()
        endidx = objname.find(' object at ')
        startidx = objname.rfind('.', 0, endidx) + 1
        self.notifier_name = objname[startidx:endidx].lower()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.homedir = os.path.join(current_dir, '../../')

        self.setting = {}
        conf = None
        common_conf = os.path.join(self.homedir, 'conf/common/%s.json' % self.notifier_name)
        notifier_conf = os.path.join(self.homedir, 'conf/notifier/%s.json' % self.notifier_name)
        conf = notifier_conf if os.path.isfile(notifier_conf) else common_conf
        with open(conf, encoding='utf-8') as f:
            self.setting = loads(f.read())
        
    def notify(self, eventid, duration):
        pass
