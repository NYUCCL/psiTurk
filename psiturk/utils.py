from __future__ import generator_stop
from urllib.request import urlopen
import json


def get_my_ip():
    """
        Asks and external server what your ip appears to be (useful is
        running from behind a NAT/wifi router).  Of course, incoming port
        to the router must be forwarded correctly.
    """
    my_ip = json.load(urlopen(
        'http://httpbin.org/ip'
    ))['origin'].split(',')[0]
    return my_ip


def colorize(target, color, use_escape=True):
    """ Colorize target string. Set use_escape to false when text will not be
    interpreted by readline, such as in intro message."""
    def escape(code):
        """ Escape character """
        return '\001%s\002' % code
    if color == 'purple':
        color_code = '\033[95m'
    elif color == 'cyan':
        color_code = '\033[96m'
    elif color == 'darkcyan':
        color_code = '\033[36m'
    elif color == 'blue':
        color_code = '\033[93m'
    elif color == 'green':
        color_code = '\033[92m'
    elif color == 'yellow':
        color_code = '\033[93m'
    elif color == 'red':
        color_code = '\033[91m'
    elif color == 'white':
        color_code = '\033[37m'
    elif color == 'bold':
        color_code = '\033[1m'
    elif color == 'underline':
        color_code = '\033[4m'
    else:
        color_code = ''
    if use_escape:
        return escape(color_code) + target + escape('\033[0m')
    else:
        return color_code + target + '\033[m'
