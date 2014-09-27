# coding: utf-8

import math
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
    rec_proc = Popen(shlex.split(arecord_comm), stdout=PIPE)
    lame_proc = Popen(shlex.split(lame_comm), stdin=rec_proc.stdout)
    lame_proc.wait()

class WaveGenerator:
    margin = 1

    def __init__(self, buf_size=1024, poll_interval=0.1):
        self.procs = {}
        self.buf_size = buf_size
        self.poll_interval = poll_interval

    def listen(self, hw_id):
        buf = b''
        while True:
            proc_info = self.procs.get(hw_id)
            if not proc_info:
                break

            if proc_info['processes'][-1].poll() != None:
                buf += proc_info['output'].read()
                if buf:
                    yield buf
                break

            buf += proc_info['output'].read(self.buf_size)
            if len(buf) < self.buf_size:
                sleep(self.poll_interval)
                continue

            yield buf
            buf = b''

    def start_proc(self, hw_id, duration=10):
        if self.procs.get(hw_id) and self.procs[hw_id]['processes'][-1].poll() == None:
            raise ResourceBusyException(self.procs[hw_id])

        comm = shlex.split('arecord -d plug%s -f S16_LE -d %d -' % (hw_id, duration))
        rec_proc = Popen(comm, stdout=PIPE)
        # set timer to externally stop rec_proc and release the mike,
        # because prec_proc runs and locks the mike
        # when listener stops reading stream before process internally ends
        Timer(duration + self.margin, self.stop, args=(hw_id, rec_proc)).start()

        # S16_LE: metadata 44byte, 16bit per sample, 8000Hz sampling, monoral
        datasize = 44 + duration * 8000 * 16 / 8
        self.procs[hw_id] = {'processes': [rec_proc],
                             'output': rec_proc.stdout,
                             'size': datasize}
        return datasize

    def get_size(self, hw_id):
        proc_info = self.procs.get(hw_id)
        if not proc_info:
            return 0
        else:
            return proc_info['size']

    def stop(self, hw_id, rec_proc=None):
        proc_info = self.procs.get(hw_id)
        if not proc_info:
            return

        proc_list = proc_info['processes']
        if not proc_list:
            rerturn

        for proc in proc_list:
            if proc.poll() == None and (proc == rec_proc or rec_proc == None):
                proc.kill()
                print('stopped ' + str(proc))
        del(self.procs[hw_id])

class MP3Generator(WaveGenerator):
    margin = 2

    def start_proc(self, hw_id, duration):
        if self.procs.get(hw_id) and self.procs[hw_id]['processes'][-1].poll() == None:
            raise ResourceBusyException(self.procs[hw_id])

        rec_comm = shlex.split('arecord -d plug%s -f S16_LE -d %d -' % (hw_id, duration))
        lame_comm = shlex.split('lame -b64 - -')
        rec_proc = Popen(rec_comm, stdout=PIPE)
        lame_proc = Popen(lame_comm, stdin=rec_proc.stdout, stdout=PIPE)
        Timer(duration + self.margin, self.stop, args=(hw_id, rec_proc)).start()

        # 8064byte per sec (I don't know why not 64000/8)
        datasize = duration * 8064 + (3 - math.ceil((duration + 1) / 9)) * 576
        self.procs[hw_id] = {'processes': [rec_proc, lame_proc],
                             'output': lame_proc.stdout,
                             'size': datasize}
        return datasize


class ResourceBusyException(Exception):
    def __init__self(self, arg):
        self.msg = 'Resource is busy. Already used by ' + str(arg)

    def __str__(self):
        return self.msg
