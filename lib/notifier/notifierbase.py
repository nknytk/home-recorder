# coding: utf-8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from pluginbase import PluginBase


class NotifierBase(PluginBase):
    def __init__(self):
        self.modtype = 'notifier'
        super().__init__()

    def notify(self, event_id,  message, datapaths):
        """
        notify() is called by home-recorder for notifing events and errors.
        Override this method in your notifier.
        Arguments are:
          - event_id: Unique id of the event.
          - message: message string to be notified.
          - datapaths: A list of abs paths.
        """

        pass
