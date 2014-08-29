# coding: utf-8

import os
import sys
import traceback
from json import loads
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

def check_owner_is_in_lan(setting, eventcheck_enabled):
    server_token, client_digest = presence.token_pair(setting)
    if not server_token:
        return False

    max_retry = 1 if eventcheck_enabled else setting.get('presence_check_max_retry', 10)
    for i in range(max_retry):
        presence.send(byte_msg=server_token)
        owner_is_in_lan = presence.receive(expected_data=client_digest,
                                           timeout=setting.get('presence_check_timeout', 0.5))
        if owner_is_in_lan:
            break

    return owner_is_in_lan

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

    eventcheck_enabled = True
    now = time()
    while True:
        begin = time()

        # If the owner's client is in LAN, disable event check, notification and recording.
        try:
            print('Check if owner is at home.')
            owner_is_in_lan = check_owner_is_in_lan(setting, eventcheck_enabled)

            if eventcheck_enabled:
                if owner_is_in_lan:
                    print('Owner is at home. Disable event check.')
                    eventcheck_enabled = False
                else:
                    print('Owner is NOT at home. Event check is kept enablsed.')

            else:
                if owner_is_in_lan:
                    print('Owner is at home. Event check is kept disabled.')
                else:
                    print('Owner is NOT at home. Enable event check.')
                    eventcheck_enabled = True
                    for ec in eventcheckers:
                        ec.reset()

            if not eventcheck_enabled:
                now = time()
                remaining_wait = begin + setting.get('presence_check_interval', 10) - now
                if remaining_wait > 0:
                    print('Wait ' + str(remaining_wait) + ' sec for next check')
                    sleep(remaining_wait)
                continue

        except:
            error_handler.handle('presence check', traceback.format_exc())

        now = time()
        remaining_wait = begin + setting.get('check_interval', 1) - now
        if remaining_wait > 0:
            sleep(remaining_wait)

        # Check events
        print('Start event detection.')
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
            print('No event detected.')
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

if __name__ == '__main__':
    conffile = os.path.join(homedir, 'conf/common/home-recorder.json')
    with open(conffile, encoding='utf-8') as f:
        SETTING = loads(f.read())

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        testrun(SETTING)
    else:
        recordhome(SETTING)
