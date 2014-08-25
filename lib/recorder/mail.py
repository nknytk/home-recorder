#!/usr/bin/python3
# coding: utf-8

import os
import sys
from time import sleep, time

sys.path.append(os.path.join(__file__, '../util'))
from .recorderthread import RecorderThread
from util.mailutil import create_mail, send_mail


class Mail(RecorderThread):
    def record(self, eventid, duration):
        eventdir = os.path.join(self.homedir,
                                'data',
                                'recorder',
                                self.setting['datasource'],
                                eventid)
        processed_files = set()

        sleep(0.1)
        finishtime = time() + duration
        is_last = False

        while True:
            now = time()
            next = now + self.setting['interval']
            if now > finishtime:
               is_last = True 

            new_files = self.get_newfiles(eventdir, processed_files)
            if not new_files:
                sleep(now + self.setting['interval'] - time())
                continue

            mail = create_mail(mfrom=self.setting['mail_from'],
                               mto=self.setting['mail_to'],
                               subject=self.setting['subject'] + ' Event ID: ' + eventid,
                               attachment_paths=new_files)
            send_mail(mfrom=self.setting['mail_from'],
                      mpassword=self.setting['password'],
                      mto=self.setting['mail_to'],
                      mserver=self.setting['server'],
                      mport=self.setting['port'],
                      mailcontent=mail)
            processed_files.update(new_files)

            now = time()
            if is_last or now > finishtime:
                break
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
        

if __name__ == '__main__':
    pass
#    mailer = Mail()
#    mailer.start_recording('test', 20)
#    mailer.join()
