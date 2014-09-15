# coding: utf-8

import os
import sys
import traceback
from urllib.parse import parse_qsl

sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))
from lamearecord import avail_mikes, WaveGenerator

wav_generator = WaveGenerator()

HTML_TEMPLATE="""<html>
<head><title>listen to mike</title></head>
<body>

<form>
Select mike id:&nbsp;<select id="device">%s</select>
</form>

<div id="audiodiv">
</div>

<script>
function restart () {
    var device = document.getElementById("device").value;
    var new_audio_elem = document.createElement("audio");
    new_audio_elem.src = "/mike/sound?device=" + device;
    new_audio_elem.id = "audio";
    new_audio_elem.play();
    new_audio_elem.controls = true;
    new_audio_elem.addEventListener('ended', restart);
    var adiv = document.getElementById("audiodiv");
    while (adiv.childNodes.length != 0) adiv.removeChild(adiv.childNodes.item(0));
    adiv.appendChild(new_audio_elem);
}

function stop_listening () {
    var device = document.getElementById("device").value;
    dummy_img = document.createElement('image');
    dummy_img.src = "/mike/stop?device=" + device;
    document.body.appendChild(dummy_img);
}

restart();
</script>
<element onunload="stop_listening()">

</body>
</html>"""


def devicelist(env):
    devices = '##########'.join(avail_mikes())
    content = bytes(devices, 'utf-8')
    header = [('Content-Type', 'text/plain'), ('Content-Lentgh', str(len(content)))]
    return header, content

def sound(env):
    qdic =  dict(parse_qsl(env.get('QUERY_STRING', '')))
    devname = qdic.get('device')
    if not devname:
        return [('Content-Type', 'audio/wav'), ('Content-Lentgh', '0')], b''
    duration = int(qdic.get('duration', 10))

    data = wav_generator.listen(devname, duration)
    if data:
        header = [('Content-Type', 'audio/wav')]
    else:
        header = [('Content-Type', 'audio/wav'), ('Content-Length', '0')]
    return header, data

def stop(env):
    devname = dict(parse_qsl(env.get('QUERY_STRING', ''))).get('device')
    if devname:
        wav_generator.stop(devname)
    return [('Content-Type', 'Image/jpeg'), ('Content-Lentgh', '0')], b''

def html(env):
    option_elems = ''
    for mike in avail_mikes():
        option_elems += '<option value="%s">%s</option>' % (mike, mike)
    html = bytes(HTML_TEMPLATE % option_elems, encoding='utf-8')
    header = [('Content-Type', 'text/html'), ('Content-Lentgh', str(len(html)))]
    return header, html
