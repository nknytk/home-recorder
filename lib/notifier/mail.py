#!/usr/bin/python3
# coding: utf-8

import os
import smtplib
import mimetypes
from email.mime.text import MIMEText
from email.utils import formatdate
from time import sleep, time

from .notifierbase import NotifierBase


class Mail(NotifierBase):
    def notify(self, eventid, message):
        mail = self.create_mail(eventid, message)
        self.send(mail)

    def create_mail(self, eventid, message):
        mail = MIMEText(message)
        mail['From'] = self.setting['mail_from']
        mail['To'] = ','.join(self.setting['mail_to'])
        mail['Subject'] = self.setting['subject'] + ' EventID: ' + eventid
        mail['Date'] = formatdate()
        return mail

    def send(self, mailcontent):
        mailer = smtplib.SMTP(self.setting['server'], self.setting['port'])
        try:
            mailer.ehlo()
            mailer.starttls()
            mailer.ehlo()
            mailer.login(self.setting['mail_from'], self.setting['password'])
            mailer.sendmail(self.setting['mail_from'],
                            self.setting['mail_to'],
                            mailcontent.as_string())
        finally:
            mailer.close()
            print('mail send at ' + str(time()))


if __name__ == '__main__':
    mailer = Mail()
    #mailer.notify('test', 'This is test mail')
