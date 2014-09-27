# coding: utf-8

import os
import sys
import json
from urllib.parse import parse_qsl

sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from webcam import avail_cameras, capture, write_webcam_config

CAMERA_STATUS = {}
CONF_TMPL = '/run/shm/home-recorder/tmp_%s_conf'
IMGPATH_TMPL = '/run/shm/home-recorder/tmp_%s.jpg'

HTML_TEMPLATE="""<html>
<head><title>camera direction</title></head>
<body>

<form>Select camera id:&nbsp;<select id="device">%s</select></form>
<div id="imgdiv"><span>Now loading..</span></div>

<script>
function keep_updating_img(){
var imgdiv = document.getElementById("imgdiv");
if (imgdiv.childNodes.length > 1) {
    imgdiv.removeChild(imgdiv.childNodes.item(0));
    imgdiv.childNodes.item(0).style.visibility = "visible";
}

var device = document.getElementById("device").value;
var newimg = document.createElement("img");
newimg.src = "/camera/image?device=" + device + "&random=" + Math.random();
newimg.style.visibility ="hidden";
imgdiv.appendChild(newimg);

setTimeout("keep_updating_img()", 1200);
}

keep_updating_img();
</script>

</body>
</html>"""


def devicelist(env):
    devices = json.dumps([cam.split('/')[-1] for cam in avail_cameras()])
    content = bytes(devices, 'utf-8')
    header = [('Content-Type', 'application/json'),
              ('Content-Lentgh', str(len(content)))]
    return header, content

def image(env):
    devname = dict(parse_qsl(env.get('QUERY_STRING', ''))).get('device')
    if not devname:
        return [('Content-Type', 'Image/jpeg'), ('Content-Lentgh', '0')], b''

    device_status = CAMERA_STATUS.get(devname, {})
    if device_status.get('in_use', False):
        data = device_status.get('data', b'')

    else:
        device_status['in_use'] =True
        CAMERA_STATUS[devname] = device_status
    
        imgpath = IMGPATH_TMPL % devname
        confpath = CONF_TMPL % devname
        conf = {'device': '/dev/' + devname, 'archive': imgpath, 'text': devname}
        write_webcam_config(conf, confpath)
        capture(confpath)
        with open(imgpath, mode='rb') as f:
            data = f.read()

        device_status['data'] = data
        device_status['in_use'] = False

    header = [('Content-Type', 'Image/jpeg'), ('Content-Length', str(len(data)))]
    return header, data

def html(env):
    option_elems = ''
    for dev in avail_cameras():
        cam = dev.split('/')[-1]
        option_elems += '<option value="%s">%s</option>' % (cam, cam)

    html = bytes(HTML_TEMPLATE % option_elems, 'utf-8')
    header = [('Content-Type', 'text/html'), ('Content-Lentgh', str(len(html)))]
    return header, html
