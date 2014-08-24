# coding: utf-8

import os
import sys
import time
from urllib.parse import parse_qsl

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/util'))
from webcam import avail_cameras, capture, write_webcam_config

TMP_WEBCAM_CONF = '/tmp/tmp_webcam_config'
TMP_IMG = '/tmp/webcam_tmp_img.jpg'

HTML_TEMPLATE="""<html>
<head><title>camera direction</title></head>
<body>

<form>Select camera id:&nbsp;<select id="device">%s</select></input></form>
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
newimg.src = "?device=" + device + "&random=" + Math.random();
newimg.style.visibility ="hidden";
imgdiv.appendChild(newimg);

setTimeout("keep_updating_img()", 1200);
}

keep_updating_img();
</script>

</body>
</html>"""


def get_image(device):
    conf = {'device': '/dev/' + device, 'archive': TMP_IMG, 'text': device}
    write_webcam_config(conf, TMP_WEBCAM_CONF)
    capture(TMP_WEBCAM_CONF)
    with open(TMP_IMG, mode='rb') as f:
        data = f.read()
    header = [('Content-Type', 'Image/jpeg'), ('Content-Length', str(len(data)))]

    return header, data

def get_html():
    option_elems = ''
    for dev in avail_cameras():
        cam = dev.split('/')[-1]
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
