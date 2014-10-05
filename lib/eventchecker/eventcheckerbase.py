# coding: utf-8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from pluginbase import PluginBase


class EventCheckerBase(PluginBase):
    def __init__(self):
        self.modtype = 'eventchecker'
        super().__init__()
        
    def check(self):
        """
        check() is called to check events by home-recoreder without arguments.
        Override this method in your event checker.
        check() should return a tuple with following three values:
          - Whether event occured in booean. If True, home-recorder goes to notification.
          - Message in unicode string. This string will be passed to the notifiers.
          - Data paths in a list. This list will be passed to the notifiers.
        """

        return (False, 'Nothing happened', [])

    def reset(self):
        pass
