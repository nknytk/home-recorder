# coding: utf-8

import hashlib
import random
import socket
import string
from time import time

SEPERATOR = '\n'
HASH_ALGORITHM = 'sha256'


def send(ip='<broadcast>', port=19201, byte_msg=b''):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(byte_msg, (ip, port))
    sock.close()
    del(sock)
    return

def receive(ip='', port=19201, expected_data=b'',timeout=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    sock.bind((ip, port))

    responder_ips = []
    start_time = time()
    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except Exception as e:
            break

        if data == expected_data:
            responder_ips.append(addr[0])

        remaining_wait = start_time + timeout - time()
        if remaining_wait > 0:
            sock.settimeout(remaining_wait)
        else:
            break

    sock.close()
    del(sock)

    return responder_ips

def token_pair(server_token, client_token, repetition):
    avail_chars = string.ascii_letters + string.digits
    random_token = ''.join([random.choice(avail_chars) for i in range(64)])
    send_token = server_token + SEPERATOR + random_token
    recv_token = client_token + SEPERATOR + random_token

    hasher = getattr(hashlib, HASH_ALGORITHM)
    recv_digest = bytes(recv_token, 'utf-8')
    for i in range(repetition):
        h = hasher()
        h.update(recv_digest)
        recv_digest = h.digest()

    return (bytes(send_token, 'utf-8'), recv_digest)


if __name__ == '__main__':
    from time import sleep
    from json import loads
    from threading import Timer
    with open('../../conf/common/home-recorder.json') as f:
        st = loads(f.read())

    max_failcount = 0
    failcount =0

    while True:
        sd, rv = token_pair(st)
        send(byte_msg=sd)
        res = receive(expected_data=rv, timeout=1)
        print(res)
        if res:
            failcount = 0
        else:
            failcount += 1
            if failcount > max_failcount:
                max_failcount = failcount
                print(max_failcount)
        sleep(1)
