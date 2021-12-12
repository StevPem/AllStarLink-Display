from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106

import subprocess
import shlex
import re
import csv
import time

import string
from datetime import datetime
from vcgencmd import Vcgencmd
vcgm = Vcgencmd()

# substitute spi(device=0, port=0) below if using that interface
serial = spi(device=0, port=0)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = sh1106(serial)

from PIL import Image
logo = Image.open("/home/repeater/oled/ASL-logo-dark-128x64.png")

import socket
hostname = socket.gethostname()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def disp_logo():
    device.display(logo.convert(device.mode))
    time.sleep(5)

def disp_hostinfo():
    # Get local time
    now = datetime.now()
    local_time = now.strftime("%H:%M")
    # Get CPU temperature
    cpu_temp = vcgm.measure_temp()
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((10, 10), hostname, fill="white")
        draw.text((10, 20), get_ip(), fill="white")
        draw.text((10, 40), local_time, fill="white")
        draw.text((60, 40), str(cpu_temp), fill="white")
    time.sleep(5)

def disp_connected_nodes():
    nodes = subprocess.check_output(shlex.split("/usr/sbin/asterisk -rx \"rpt lstats 50605\""))
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        #draw.text((10, 10), "Connected nodes:", fill="white")
        ypos = 5
        for row in nodes.splitlines():
            column = row.split()
            #print (column[0], " ", column[3])
            draw.text((10, ypos), column[0], fill="white")
            draw.text((60, ypos), column[3], fill="white")
            ypos = ypos + 10
    time.sleep(5)

# Loop the menu forever
while True:
    disp_logo()
    disp_hostinfo()
    disp_connected_nodes()

#iax2 show channels (shows info on connected nodes)
#iax2 show registry (show node registration status)
#rpt lstats <node> (show statistics on a node)
#rpt stats <node> (show settings on a node)
#rpt nodes <node> (list ALL connected nodes)

