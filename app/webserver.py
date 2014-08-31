# coding: utf-8

import os
import sys
import traceback
from wsgiref.simple_server import make_seraver, WSGIRequestHandler

current_dir = os.path.dirname(os.path.abspath(__file__))
homedir = os.path.join(current_dir, '../')
sys.path.insert(0, os.path.join(homedir, 'lib'))

STATUS_DICT = {
   200: '200 OK',
   400: '400 Bad Request',
   401: '401 Unauthorized',
   404: '404 Not Found',
   500: '500 Internal Server Error'
}


def run_server(switch_obj):
    class DetectionSwitchHandler(WSGIRequestHandler):
        def get_environ(self):
            env = WSGIRequestHandler.get_environ(self)
            env['detection_switcher'] = switch_obj
            return env

    svr = make_server('', 8071, routing_app, handler_class=DetectionSwitchHandler)
    svr.serve_forever()

def routing_app(env, start_response):
    switch = env['detection_switcher']
    if not env.get('REMOTE_ADDR', '') in switch.responder_ips:
        full_status_code, header = make_error(401)
        start_response(full_statu_code, header)
        return [full_status_code]

    func = get_func_from_path(env['PATH_INFO'])
    if not func:
        full_status_code, header = make_error(404)
        start_response(full_statu_code, header)
        return [full_status_code]

    try:
        header, content = func(env)
        start_response('200 OK', header)
        return [content]
    except:
        print(traceback.format_exc())
        full_status_code, header = make_error(500)
        start_response(full_statu_code, header)
        return [full_status_code]

def get_func_from_pathi(path_info):
    paths = env['PATH_INFO'].strip('/').split('/')
    if len(paths) >=2:
        resource, method = paths[0:2]
    else:
        return None

    try:
        app = __import__('webapp.' + resource)
        func = app.getattr(method)
    except:
        return None

    return func

def make_error(status_code_int):
    content = STATUS_DICT.get(status_code_int, '404 Not Found')
    header = [('Content-Type', 'text/plain; charset=UTF-8'),
              ('Content-Length', str(len(content)))]
    return (header, content)
