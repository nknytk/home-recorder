# coding: utf-8

import os
import re
import shlex
from time import sleep
from subprocess import Popen, PIPE, call, check_output
from threading import Timer


def avail_mikes():
    devices =[]

    os.environ['LANG'] = 'C'
    command = 'arecord -l'
    arecord_l = Popen(shlex.split(command), stdout=PIPE)
    arecord_l.wait()

    if arecord_l.returncode != 0:
        print(arecord_l.stderr.read())
        return devices

    for line in arecord_l.stdout.readlines():
        m = re.match('^card ([0-9]): .*, device ([0-9]): .*$', line.decode('utf-8'))
        if not m:
            continue

        card = m.group(1)
        device = m.group(2)
        if card and device:
            devices.append('hw:%s,%s' % (card, device))

    return devices

def record_wav(hw_id, duration, filename):
    if not filename.endswith('.wav'):
        filename += '.wav'
    command = 'arecord -D plug%s -f S16_LE -d %d %s' % (hw_id, duration, filename)
    call(shlex.split(command))

def record_mp3(hw_id, duration, filename):
    if not filename.endswith('.mp3'):
        filename += '.mp3'
    arecord_comm = 'arecord -D plug%s -f S16_LE -d %d -' % (hw_id, duration)
    lame_comm = 'lame -V2 - ' + filename

    check_output('%s | %s' % (arecord_comm, lame_comm), shell=True)

class WaveGenerator:
    def __init__(self, buf_size=1024, poll_interval=0.1):
        self.procs = {}
        self.buf_size = buf_size
        self.poll_interval = poll_interval

    def listen(self, hw_id, duration=10):
        buf = b''
        if self.procs.get(hw_id) and self.procs[hw_id].poll() == None:
            print('existing ' + str(self.procs[hw_id]))
            return

        comm = shlex.split('arecord -d plug%s -f S16_LE -d %d -' % (hw_id, duration))
        rec_proc = Popen(comm, stdout=PIPE)
        Timer(duration + 1, self.stop, args=(hw_id, rec_proc)).start()
        self.procs[hw_id] = rec_proc

        while True:
            proc = self.procs.get(hw_id)
            if not proc:
                break
            if proc.poll() != None:
                buf = proc.stdout.read()
                if buf:
                    yield buf
                break

            buf += proc.stdout.read(self.buf_size)
            if len(buf) < self.buf_size:
                sleep(self.poll_interval)
                continue

            yield buf
            buf = b''

    def stop(self, hw_id, rec_proc=None):
        proc = self.procs.get(hw_id)
        if proc and proc.poll() == None and (proc == rec_proc or rec_proc == None):
            proc.kill()
            print('stopped')
            del(self.procs[hw_id])
