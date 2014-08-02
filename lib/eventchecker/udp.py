# coding: utf-8

import socket
from random import random
from threading import Timer
from time import time


def send(ip='<broadcast>', port=5050, msg=''):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(msg, (ip, port))
    sock.close()
    del(sock)
    return

def receive(ip='', port=5050, timeout=1):
    stopmsg = b'stoplistening' + bytes(str(random), 'utf-8')
    terminator = Timer(timeout, send, ('127.0.0.1', port, stopmsg))
    terminator.start()

    res = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    while True:
        data, addr = sock.recvfrom(1024)
        if addr[0] == '127.0.0.1' and data == stopmsg:
            break
        res.append({'addr': addr, 'data': data, 'time': time()})
    sock.close()
    del(sock)

    return res
