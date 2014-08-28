# coding: utf-8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from pluginbase import PluginBase


class EventCheckerBase(PluginBase):
    def __init__(self):
        self.modtype = 'eventchecker'
        PluginBase.__init__(self)
        
    def check(self):
        return (False, 'Nothing happened', [])

    def reset(self):
        pass
