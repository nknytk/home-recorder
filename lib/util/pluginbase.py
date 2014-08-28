# ccoding: utf-8

import os
from json import loads


class PluginBase:
    def __init__(self):
        self.modname = self.__module__.split('.')[-1]
        self.setup_dirs()

        confpath_tmpl = os.path.join(self.homedir, 'conf/%s/%s.json')
        mod_conf = confpath_tmpl % (self.modtype, self.modname)
        common_conf = confpath_tmpl % ('common', self.modname)
        self.conf_files = {'mod': (mod_conf, 0), 'common': (common_conf, 0)}
        self.setting = {}
        self.load_conf()

    def setup_dirs(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.homedir = os.path.join(current_dir, '../../')
        self.datadir = os.path.join(self.homedir, 'data', self.modtype, self.modname)
        if not os.path.exists(self.datadir):
            os.makedirs(os.path.abspath(self.datadir))

    def load_conf(self):
        conf_updated = False
        for key in ('common', 'mod'):
            filename, last_mtime = self.conf_files[key]
            if os.path.isfile(filename) and os.path.getmtime(filename) > last_mtime:
                conf_updated = True
            elif last_mtime != 0 and not os.path.isfile(filename):
                conf_updated = True
        if not conf_updated:
            return

        self.setting = {}
        for key in ('common', 'mod'):
            filename, last_mtime = self.conf_files[key]
            if os.path.isfile(filename):
                with open(filename, encoding='utf-8') as f:
                    self.setting.update(loads(f.read()))
                self.conf_files[key] = (filename, os.path.getmtime(filename))
