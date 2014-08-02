#!/usr/bin/python3
# coding: utf-8

import os
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.utils import formatdate
from time import sleep, time

from .recorderthread import RecorderThread


class Mail(RecorderThread):
    def record(self, eventid, duration):
        eventdir = os.path.join(self.homedir,
                                'data',
                                'recorder',
                                self.setting['datasource'],
                                eventid)
        processed_files = set()

        finishtime = time() + duration
        while True:
            now = time()
            if now > finishtime:
                break

            new_files = self.get_newfiles(eventdir, processed_files)
            if not new_files:
                sleep(now + self.setting['interval'] - time())
                continue

            mail = self.create_mail(eventid)
            self.attach2mail(mail, new_files)
            print(new_files)
            self.send(mail)
            processed_files.update(new_files)

            now = time()
            next = now + self.setting['interval']
            if next > finishtime:
                break
            else:
                if next > now:
                    sleep(next - now)

    def get_newfiles(self, dir_name, processed):
        try:
            files = os.listdir(dir_name)
        except OSError:
            return None

        current_files = []
        for f in files:
            f = os.path.join(dir_name, f)
            if os.path.isfile(f):
                current_files.append(f)
        newfiles =  set(current_files).difference(processed)
        return sorted(list(newfiles))
        

    def create_mail(self, eventid):
        mail = MIMEMultipart()
        mail['From'] = self.setting['mail_from']
        mail['To'] = ','.join(self.setting['mail_to'])
        mail['Subject'] = self.setting['subject'] + ' EventID: ' + eventid
        mail['Date'] = formatdate()
        return mail

    def attach2mail(self, mail, filenames):
        for fname in filenames:
            with open(fname, 'rb') as f:
                content = f.read()
            fname = fname.split('/')[-1]

            conttype, ignored = mimetypes.guess_type(fname)
            if conttype is None:
                conttype = 'application/octet-stream'
            maintype, subtype = conttype.split('/')

            if maintype == 'image':
                attachment = MIMEImage(content, subtype, filename=fname)
            elif maintype == 'text':
                attachment = MIMEText(content, subtype, 'utf-8')
            elif maintype == 'audio':
                attachment = MIMEAudioe(content, subtype, filename=fname)
            else:
                attachment = MIMEApplicatione(content, subtype, filename=fname)

            attachment.add_header('Content-Disposition', 'attachment', filename=fname)
            mail.attach(attachment)

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
    mailer.start_recording('test', 20)
    mailer.join()
