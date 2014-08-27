# coding: utf-8

import os
from json import loads

class EventCheckerBase:
    def __init__(self):
        objname = self.__str__()
        endidx = objname.find(' object at ')
        startidx = objname.rfind('.', 0, endidx) + 1
        self.eventchecker_name = objname[startidx:endidx].lower()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.homedir = os.path.join(current_dir, '../../')
        self.datadir = os.path.join(self.homedir, 'data', 'eventchecker', self.eventchecker_name)
        if not os.path.exists(self.datadir):
            os.makedirs(os.path.abspath(self.datadir))

        self.setting = {}
        conf = None
        common_conf = os.path.join(self.homedir, 'conf/common/%s.json' % self.eventchecker_name)
        checker_conf = os.path.join(self.homedir, 'conf/eventchecker/%s.json' % self.eventchecker_name)
        conf = checker_conf if os.path.isfile(checker_conf) else common_conf
        with open(conf, encoding='utf-8') as f:
            self.setting = loads(f.read())
        
    def check(self):
        return (False, 'Nothing happened', [])

    def reset(self):
        pass
