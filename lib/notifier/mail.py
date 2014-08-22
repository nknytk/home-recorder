# coding: utf-8

import os
import sys
from time import sleep, time

sys.path.append(os.path.join(__file__, '../util'))
from .notifierbase import NotifierBase
from util.mailutil import create_mail, send_mail


class Mail(NotifierBase):
    def notify(self, eventid, message, files=[]):
        mail = create_mail(mfrom=self.setting['mail_from'],
                           mto=self.setting['mail_to'],
                           subject=self.setting['subject'] + ' Event ID: ' + eventid,
                           message=message,
                           attachment_paths=files)
        send_mail(mfrom=self.setting['mail_from'],
                  mpassword=self.setting['password'],
                  mto=self.setting['mail_to'],
                  mserver=self.setting['server'],
                  mport=self.setting['port'],
                  mailcontent=mail)


if __name__ == '__main__':
    mailer = Mail()
    #mailer.notify('test', 'This is test mail')
