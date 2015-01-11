# coding: utf-8

import os
import sys
import requests

from .notifierbase import NotifierBase


class Twillio(NotifierBase):
    base_url = 'https://api.twilio.com/2010-04-01/Accounts/%s/Calls'
    required_items = ['account_sid', 'auth_token', 'caller', 'callee', 'twimlbin_url']

    def __init__(self):
        super().__init__()
        for item in self.required_items:
            if not item in self.setting:
                raise Exception('%s is not set.' % item)

    def notify(self, eventid, message, files=[]):
        url = self.base_url % self.setting['account_sid']
        auth= (self.setting['account_sid'], self.setting['auth_token'])
        data = {
            'Caller': self.setting['caller'],
            'Called': self.setting['callee'],
            'Url': self.setting['twimlbin_url']
        }
        print('Make a call with twillio.')
        r = requests.post(url, data=data, auth=auth)
        print(r.content.decode('utf-8'))
