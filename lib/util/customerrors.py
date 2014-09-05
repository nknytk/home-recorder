# coding: utf-8

class BadRequest(Exception):
    def __init__(self, msg):
        self.msg = msg
