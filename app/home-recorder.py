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

def get_eventid():
    now = time()
    return 

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

    server_token = None

    while True:
        now = time()
        if not server_token:
            server_token, client_digest = presence.token_pair(setting)

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
                sleep(time() + setting['check_interval'] - now)
                continue
            else:
                sys.exit(1)

        if not event_msgs:
            sleep(time() + setting['check_interval'] - now)
            continue
        print('Event detected: ' + ' '.join(event_msgs))

        if server_token:
            try:
                print('Check if owner is at home.')
                presence.send(byte_msg=server_token)
                owner_is_at_home = presence.receive(expected_data=client_digest)
                server_token = None
                if owner_is_at_home:
                    print('Owner is at home. Skip notification.')
                    sleep(time() + setting['check_interval'] - now)
                    continue
                print('Owner is not at home.')
            except:
                trc = traceback.format_exc()
                for notifier in notifiers:
                    notifier.notify('Error in presence check', trc)

        evid = strftime('%Y-%m-%d_%H:%M:%S', localtime())
        print('Start notification and recording. Event iD: ' + evid)
        for notifier in notifiers:
            notifier.notify(evid, '\n'.join(event_msgs), event_files)

        try:
            for recorder in recorders:
                recorder.start_recording(evid, setting['recording_duration'])

        except:
            trc = traceback.format_exc()
            for notifier in notifiers:
                notifier.notify('Error in recorder', trc)
            if setting['continue_on_error']:
                sleep(time() + setting['check_interval'] - now)
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
