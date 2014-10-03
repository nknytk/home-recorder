# coding: utf-8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from pluginbase import PluginBase


class NotifierBase(PluginBase):
    def __init__(self):
        self.modtype = 'notifier'
        super().__init__()

    def notify(self, eventid, duration):
        pass
