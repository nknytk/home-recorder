# coding: utf-8

import os
import sys
from threading import Thread

sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from pluginbase import PluginBase


class NotifierBase(PluginBase):
    def __init__(self):
        self.modtype = 'notifier'
        super().__init__()

    def start_notification(self, event_id, message, datapaths=[]):
        """this method is diretry called by home-recorder"""
        self.notifier_thread = Thread(target=self.notify, args=(event_id, message, datapaths))
        self.notifier_thread.start()

    def join(self, timeout=None):
        self.notifier_thread.join(timeout)

    def notify(self, event_id, message, datapaths):
        """
        notify() is called indirectly by home-recorder for notifing events and errors.
        Override this method in your notifier.
        Arguments are:
          - event_id: Unique id of the event.
          - message: message string to be notified.
          - datapaths: A list of abs paths.
        """

        pass
