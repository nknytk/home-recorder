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

def recordhome(setting):
    eventcheckers = load_components(setting, 'eventchecker')
    notifiers = load_components(setting, 'notifier')
    recorders = load_components(setting, 'recorder')

    if setting['test_on_start']:
        for checker in eventcheckers:
            checker.check()
        for notifier in notifiers:
            notifier.notify('test', 'Test notification from home-recorder')
        for recorder in recorders:
            recorder.start_recording('test', 5)
        for recorder in recorders:
            recorder.join()

    eventcheck_enabled = False
    now = time()
    while True:
        begin = time()

        # If the owner's client is in LAN, disable event check, notification and recording.
        server_token, client_digest = presence.token_pair(setting)
        if server_token:
            try:
                print('Check if owner is at home.')
                max_retry = setting.get('presence_check_max_retry', 10) if eventcheck_enabled else 1
                for i in range(max_retry):
                    presence.send(byte_msg=server_token)
                    owner_is_in_lan = presence.receive(expected_data=client_digest,
                                                       timeout=setting.get('presence_check_timeout', 0.5))
                    if owner_is_in_lan:
                        break
                    elif i < max_retry - 1:
                        print('Timed out. Retry.')

                if eventcheck_enabled:
                    if owner_is_in_lan:
                        print('Owner is at home. Event check is kept disabled.')
                    else:
                        print('Owner is NOT at home. Event check is enabled.')
                        eventcheck_enabled = False
                        for ec in eventcheckers:
                            ec.reset()

                else:
                    if owner_is_in_lan:
                        print('Owner is at home. Disable event check.')
                        eventcheck_enabled = True
                    else:
                        print('Owner is NOT at home. Event check is kept enablsed.')

                if eventcheck_enabled:
                    now = time()
                    remaining_wait = begin + setting.get('presence_check_interval', 10) - now
                    if remaining_wait > 0:
                        print('Wait ' + str(remaining_wait) + ' sec for next check')
                        sleep(remaining_wait)
                    continue

            except:
                trc = traceback.format_exc()
                for notifier in notifiers:
                    notifier.notify('Error in presence check', trc)

        now = time()
        remaining_wait = begin + setting.get('check_interval', 1) - now
        if remaining_wait > 0:
            sleep(remaining_wait)

        # Check events
        event_msgs = []
        event_files = []
        try:
            for checker in eventcheckers:
                chk_res = checker.check()
                if chk_res[0]:
                    event_msgs.append(chk_res[1])
                    event_files += chk_res[2]
        except:
            trc = traceback.format_exc()
            for notifier in notifiers:
                notifier.notify('Error in eventchecker', trc)
            if setting['continue_on_error']:
                continue
            else:
                sys.exit(1)

        if not event_msgs:
            continue
        print('Event detected: ' + ' '.join(event_msgs))

        # If event is detected, notify
        evid = strftime('%Y-%m-%d_%H:%M:%S', localtime())
        print('Start notification and recording. Event iD: ' + evid)
        for notifier in notifiers:
            notifier.notify(evid, '\n'.join(event_msgs), event_files)

        # Record after notification
        try:
            for recorder in recorders:
                recorder.start_recording(evid, setting['recording_duration'])

        except:
            trc = traceback.format_exc()
            for notifier in notifiers:
                notifier.notify('Error in recorder', trc)
            if setting['continue_on_error']:
                continue
            else:
                sys.exit(1)

        finally:
            for recorder in recorders:
                recorder.join()

if __name__ == '__main__':
    conffile = os.path.join(homedir, 'conf/common/home-recorder.json')
    with open(conffile, encoding='utf-8') as f:
        SETTING = loads(f.read())
    recordhome(SETTING)
