# coding: utf-8

import os
import sys
from threading import Thread
from time import sleep, strftime, time

current_dir = os.path.dirname(os.path.abspath(__file__))
homedir = os.path.join(current_dir, '../')
sys.path.insert(0, os.path.join(homedir, 'lib'))
from util import presence
from webserver import get_server

from time import time

class ResourceController:
    def __init__(self, setting):
        self.status = {}
        self.responder_ips = set()
        self.max_retry = setting.get('presence_check_max_retry', 10)
        self.timeout = setting.get('presence_check_timeout', 0.5)
        self.interval = setting.get('presence_check_interval', 10)
        self.maxqps = setting.get('max_qps', 10)
            
        self.s_token = setting.get('server_side_token')
        self.c_token = setting.get('client_side_token')
        self.repetition = setting.get('repetition', 300)
        if self.s_token and self.c_token and isinstance(self.repetition, int):
            self.status['enabled'] = True

        self.webserver = None
        
    def start_webserver(self):
        if not self.webserver:
            self.webserver = get_server(self)
            self.webserver_thread = Thread(target=self.webserver.serve_forever)
            self.webserver_thread.start()

    def stop_webserver(self):
        if self.webserver:
            self.webserver.shutdown()
            self.webserver = None
            self.webserver_thread.join()

    def start_auto_switch(self):
        if self.status['enabled']:
            self._update_status()
            self.t = Thread(target=self._auto_switch)
            self.t.start()

    def _auto_switch(self):
        while True:
            if self.status.get('stop'):
                break
            start_time = time()
            self._update_status()
            intvl = 1 if self.status['enabled'] else self.interval
            remainig_interval = start_time + intvl - time()
            if remainig_interval > 0:
                sleep(remainig_interval)

    def _update_status(self):
        current_responders = set()
        for i in range(self.max_retry):
            server_token, client_digest = presence.token_pair(self.s_token, self.c_token, self.repetition)
            presence.send(byte_msg=server_token)
            current_responders.update(presence.receive(expected_data=client_digest, timeout=self.timeout))
            if not self.responder_ips - current_responders:
                break
        self.responder_ips = current_responders

        # if registered clients are in LAN, disable event check and start web server
        if self.responder_ips:
            self.status['enabled'] = False
            self.start_webserver()

        # if no registered clients are in LAN, enable event check and stop web server
        else:
            self.stop_webserver()
            self.status['enabled'] = True

    def stop_auto_switch(self):
        self.status['stop'] = True
        self.t.join()
