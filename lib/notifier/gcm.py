# coding: utf-8

import json
from urllib.request import Request, urlopen
from .notifierbase import NotifierBase

GOOGLE_API_URL = 'https://android.googleapis.com/gcm/send'


class GCM(NotifierBase):
    def notify(self, eventid, message, files=[]):
        api_key = self.setting.get('api_key')
        regids = self.setting.get('registration_ids')
        if not api_key or not regids:
            print('You need api key and registration ids to use GCM.')
            return

        req = Request(GOOGLE_API_URL)
        req.add_header('Authorization', 'key=%s' % api_key)
        req.add_header('Content-Type', 'application/json')

        data = {
            'registration_ids': regids,
            'data': {
                'subject': self.setting.get('subject', '') + ' Event ID: ' + eventid,
                'message': message
            }
        }
        data = json.dumps(data).encode('utf-8')
        f = urlopen(req, data=data)
        r = f.read()
        f.close()
        print('GCM notification sent. Result: ' + r)


if __name__ == '__main__':
    gcm = GCM()
    gcm.notify('test', 'This is test notification', 'test')
