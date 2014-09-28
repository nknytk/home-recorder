# coding: utf-8

import os
import sys
import traceback
import socket
from socketserver import ThreadingMixIn
from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer

current_dir = os.path.dirname(os.path.abspath(__file__))
homedir = os.path.join(current_dir, '../')
sys.path.insert(0, os.path.join(homedir, 'lib'))
sys.path.append(os.path.join(homedir, 'lib/util'))
from customerrors import BadRequest

STATUS_DICT = {
   200: '200 OK',
   400: '400 Bad Request',
   401: '401 Unauthorized',
   404: '404 Not Found',
   500: '500 Internal Server Error',
   503: '503 Service Tmporary Unavailable'
}
LOCAL_IPs = []
try:
    LOCAL_IPs.append(socket.gethostbyname('localhost'))
    LOCAL_IPs.append(socket.gethostbyname(socket.gethostname()))
    dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dummy_socket.connect(('google.com', 0))
    LOCAL_IPs.append(dummy_socket.getsockname()[0])
    dummy_socket.close()
except:
    print(traceback.format_exc())


class ThreadingServer(ThreadingMixIn, WSGIServer):
    pass

def get_server(controller_obj=None, port=8071):
    class SwitchHandler(WSGIRequestHandler):
        def get_environ(self):
            env = WSGIRequestHandler.get_environ(self)
            env['resource_controller'] = controller_obj
            return env

    svr = make_server('', port, routing_app, ThreadingServer, SwitchHandler)
    return svr

def routing_app(env, start_response):
    controller = env['resource_controller']
    rmip = env.get('REMOTE_ADDR', '')
    if controller and not (rmip in controller.responder_ips or rmip in LOCAL_IPs):
        return _return_error(start_response, 401)

    func = get_func_from_path(env['PATH_INFO'])
    if not func:
        return _return_error(start_response, 404)

    try:
        header, content = func(env)
        start_response('200 OK', header)
        if isinstance(content, bytes):
            return [content]
        else:
            return content
    except BadRequest as e:
        print(e)
        print(traceback.format_exc())
        return _return_error(start_response, 400)
    except:
        print(traceback.format_exc())
        return _return_error(start_response, 500)

def get_func_from_path(path_info):
    paths = path_info.strip('/').split('/')
    if len(paths) >= 2 and not paths[1].startswith('_'):
        resource, method = paths[0:2]
    else:
        return None

    try:
        app = __import__('webapp.' + resource, fromlist=[resource])
        func = getattr(app, method)
    except (AttributeError, ImportError):
        print(traceback.format_exc())
        return None

    return func

def _return_error(start_response, status_code_int):
    status_code = STATUS_DICT.get(status_code_int, '404 Not Found')
    content = bytes(status_code, 'utf-8')
    header = [('Content-Type', 'text/plain; charset=UTF-8'),
              ('Content-Length', str(len(content)))]
    start_response(status_code, header)
    return [content]


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8071
    svr = get_server(port=port)
    svr.serve_forever()
