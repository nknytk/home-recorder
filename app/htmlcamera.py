# coding: utf-8

import os
import sys
import time
import shlex
import subprocess
from urllib.parse import parse_qsl

CONFFILE = '/tmp/camera_test.conf'

HTML_TEMPLATE="""<html>
<head><title>camera direction</title></head>
<body>

<form>Select camera id:&nbsp;<select id="devid">%s</select></input></form>
<div id="imgdiv"><span>Now loading..</span></div>

<script>
function keep_updating_img(){
var imgdiv = document.getElementById("imgdiv");
if (imgdiv.childNodes.length > 1) {
    imgdiv.removeChild(imgdiv.childNodes.item(0));
    imgdiv.childNodes.item(0).style.visibility = "visible";
}

var devid = document.getElementById("devid").value;
var newimg = document.createElement("img");
newimg.src = "?device=" + devid + "&random=" + Math.random();
newimg.style.visibility ="hidden";
imgdiv.appendChild(newimg);

setTimeout("keep_updating_img()", 1500);
}

keep_updating_img();
</script>

</body>
</html>"""

WEBCAM_CONF_TEMPLATE = """[grab]
device = /dev/video%s
text = test
fg_red = 255
fg_green = 255
fg_blue = 255
width = 640
height = 480
delay = 0
wait = 0
rotate = 0
top = 0
left = 0
bottom = -1
right = -1
quality = 90
trigger = 0
once = 1
archive = /tmp/camera_test.jpg"""


def get_image(device_id):
    with open(CONFFILE, mode='w', encoding='utf-8') as f:
        f.write(WEBCAM_CONF_TEMPLATE % device_id)
    command = 'webcam %s' % CONFFILE
    devnull = open('/dev/null', mode='w')
    subprocess.call(shlex.split(command), stdout=devnull, stderr=devnull)
    devnull.close()

    with open('/tmp/camera_test.jpg', mode='rb') as f:
        data = f.read()
    if os.path.isfile('/tmp/camera_test.jpg'):
        os.remove('/tmp/camera_test.jpg')
    header = [('Content-Type', 'Image/jpeg'), ('Content-Length', str(len(data)))]

    return header, data

def avail_cams():
    ids = []
    for f in os.listdir('/dev/'):
        if f.startswith('video'):
            ids.append(f.lstrip('video'))
    return ids

def get_html():
    option_elems = ''
    for cam in avail_cams():
        option_elems += '<option value="%s">%s</option>' % (cam, cam)

    html = bytes(HTML_TEMPLATE % option_elems, 'utf-8')
    header = [('Content-Type', 'text/html'), ('Content-Lentgh', str(len(html)))]
    return header, html

def app(env, sr):
    s = time.time()
    qd = dict(parse_qsl(env.get('QUERY_STRING', '')))
    devid = qd.get('device')
    finish = qd.get('finish');

    if env.get('PATH_INFO', '') == '/favicon.ico':
        data = b''
        header = [('Content-Type', 'text/plain'), ('Content-Length', '0')]
    elif devid:
        header, data = get_image(devid)
    else:
        header, data = get_html()

    sr('200 OK', header)
    print(time.time() - s)
    return [data]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    port = 8071 if len(sys.argv) == 1 else int(sys.argv[1])
    svr = make_server('', port, app)
    svr.serve_forever()
