# coding: utf-8

import os
import sys
import traceback
from json import loads
from threading import Thread
from time import localtime, sleep, strftime, time

current_dir = os.path.dirname(os.path.abspath(__file__))
homedir = os.path.join(current_dir, '../')
sys.path.insert(0, os.path.join(homedir, 'lib'))
from util import presence

def load_components(setting, component_name):
    components = []
    for mod_name in setting[component_name]:
        mod = __import__(component_name + '.' + mod_name, fromlist=[mod_name])
        for attr in dir(mod):
            if attr.lower() == mod_name:
                components.append(getattr(mod, attr)())

    return components

def testrun(setting):
    print('Start test run.')

    print('Initialize eventcheckers.')
    eventcheckers = load_components(setting, 'eventchecker')
    print('OK\n')
    print('Initialize notifiers.')
    notifiers = load_components(setting, 'notifier')
    print('OK\n')
    print('Initialize recorders.')
    recorders = load_components(setting, 'recorder')
    print('OK\n')
    print('Initialize error handler.')
    err_handler = ErrorHandler(setting, notifiers)
    print('OK\n')

    print('Check if owner is at home.')
    owner_is_in_lan = check_owner_is_in_lan(setting, False)
    print(owner_is_in_lan)
    print('OK\n')

    print('Run event checks.')
    for checker in eventcheckers:
        checker.check()
    print('OK\n')
    print('Run notifications.')
    for notifier in notifiers:
        notifier.notify('test', 'Test notification from home-recorder')
    print('OK\n')
    print('Run recorders.')
    for recorder in recorders:
        recorder.start_recording('test', 5)
    for recorder in recorders:
        recorder.join()
    print('OK\n')

    print('Run error notification for 2 times.')
    err_handler.handle('test', 'Test notification from home-recorder')
    err_handler.handle('test', 'Test notification from home-recorder')
    print('OK\n')

    print('All components are OK.')

def recordhome(setting):
    eventcheckers = load_components(setting, 'eventchecker')
    notifiers = load_components(setting, 'notifier')
    recorders = load_components(setting, 'recorder')
    error_handler = ErrorHandler(setting, notifiers)

    detection_switcher = AutoEventCheckSwitcher(setting)

    skipped_last = False
    next_loop = 0
    while True:
        remaining_wait = next_loop - time()
        if remaining_wait > 0:
            sleep(remaining_wait)
        next_loop = time() + setting.get('check_interval', 1)

        if not detection_switcher.eventcheck_enabled():
            if not skipped_last:
                print('Disable Event check.')
            skipped_last = True
            continue

        if skipped_last:
            print('Enable Event check.')
        skipped_last = False

        # Check events
        event_msgs = []
        event_files = []
        try:
            for checker in eventcheckers:
                checker.load_conf()
                chk_res = checker.check()
                if chk_res[0]:
                    event_msgs.append(chk_res[1])
                    event_files += chk_res[2]
        except:
            error_handler.handle('event check', traceback.format_exc())

        if not event_msgs:
            #print('No event detected.')
            continue
        print('Event detected: ' + ' '.join(event_msgs))

        # If event is detected, notify
        evid = strftime('%Y-%m-%d_%H:%M:%S', localtime())
        print('Start notification and recording. Event iD: ' + evid)
        for notifier in notifiers:
            try:
                notifier.load_conf()
                notifier.notify(evid, '\n'.join(event_msgs), event_files)
            except:
                print(traceback.format_exc())

        # Record after notification
        try:
            for recorder in recorders:
                recorder.load_conf()
                recorder.start_recording(evid, setting['recording_duration'])

        except:
            error_handler.handle('recorder', traceback.format_exc())

        finally:
            for recorder in recorders:
                recorder.join()

class ErrorHandler:
    def __init__(self, setting, notifiers):
        self.errors = {}
        self.suppress_interval = setting.get('error_suppression_interval')
        self.notifiers = notifiers

    def handle(self, error_point, message):
        now = time()
        past_errors = self.errors.get(error_point, {})
        last_error_time = past_errors.get(message, 0)
        should_suppress = True
        if not self.suppress_interval:
            should_suppress = False
        elif now > last_error_time + self.suppress_interval:
            should_suppress = False
        past_errors[message] = now
        self.errors[error_point] = past_errors
        print(message)

        if should_suppress:
            print('Suppress notification of the error above.')
            return

        try:
            for notifier in self.notifiers:
                notifier.load_conf()
                notifier.notify('Error in ' + error_point, message)
        except:
            print(traceback.format_exc())

class AutoEventCheckSwitcher:
    def __init__(self, setting):
        self.status = {}
        self.responder_ips = set()
        self.max_retry = setting.get('presence_check_max_retry', 10)
        self.timeout = setting.get('presence_check_timeout', 0.5)
        self.interval = setting.get('presence_check_interval', 10)

        self.s_token = setting.get('server_side_token')
        self.c_token = setting.get('client_side_token')
        self.repetition = setting.get('repetition', 300)

        if self.s_token and self.c_token and isinstance(self.repetition, int):
            self.update_status()
            t = Thread(target=self.auto_switch)
            t.start()

    def auto_switch(self):
        while True:
            start_time = time()
            self.update_status()
            intvl = 1 if self.status['enabled'] else self.interval
            remainig_interval = start_time + intvl - time()
            if remainig_interval > 0:
                sleep(remainig_interval)

    def update_status(self):
        current_responders = set()
        for i in range(self.max_retry):
            server_token, client_digest = presence.token_pair(self.s_token, self.c_token, self.repetition)
            presence.send(byte_msg=server_token)
            current_responders.update(presence.receive(expected_data=client_digest, timeout=self.timeout))
            if not self.responder_ips - current_responders:
                break
        self.responder_ips = current_responders

        # if registered clients are in LAN, disable event check
        self.status['enabled'] = False if self.responder_ips else True

    def eventcheck_enabled(self):
        return self.status['enabled']


if __name__ == '__main__':
    conffile = os.path.join(homedir, 'conf/common/home-recorder.json')
    with open(conffile, encoding='utf-8') as f:
        SETTING = loads(f.read())

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        testrun(SETTING)
    else:
        recordhome(SETTING)
