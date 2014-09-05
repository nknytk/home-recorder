# coding: utf-8

import os
import sys
import json
from urllib.parse import parse_qsl

sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from customerrors import BadRequest

GCM_CONF_JSON = os.path.join(os.path.dirname(__file__), '../../conf/notifier/gcm.json')


def register(env):
    new_id = _get_registration_id(env)
    if not new_id:
        raise BadRequest('No registration_id found')

    current_conf = _get_current_conf()
    new_ids = list(set(current_conf.get('registration_ids', []) + [new_id]))
    current_conf['registration_ids'] = new_ids
    _write_conf(current_conf)

    content = b'registered'
    header = [('Content-Type', 'text/plain'), ('Content-Length', str(len(content)))]
    return header, content

def remove(env):
    id2del = _get_registration_id(env)
    if not id2del:
        raise BadRequest('No registration_id found')

    current_conf = _get_current_conf()
    id_set = set(current_conf.get('registration_ids', []))
    id_set.discard(id2del)
    current_conf['registration_ids'] = list(id_set)
    _write_conf(current_conf)

    content = b'removed'
    header = [('Content-Type', 'text/plain'), ('Content-Length', str(len(content)))]
    return header, content

def _get_current_conf():
    if os.path.isfile(GCM_CONF_JSON):
        with open(GCM_CONF_JSON) as f:
            conf = json.loads(f.read())
        return conf
    else:
        return {}

def _write_conf(conf_dict):
    with open(GCM_CONF_JSON, mode='w', encoding='utf-8') as f:
        f.write(json.dumps(conf_dict, indent=4))

def _get_registration_id(env):
    if env.get('REQUEST_METHOD', '') != 'POST':
        return None
    data = dict(parse_qsl(env['wsgi.input'].read()))
    return data.get('registration_id')
