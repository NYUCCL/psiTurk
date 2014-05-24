import subprocess
import os
import stat
import signal
import uuid
import struct
from sys import platform as _platform
from psiturk_config import PsiturkConfig

config = PsiturkConfig()
config.load_config()


class Tunnel():
    ''' Allow psiTurk to puncture firewalls using reverse tunnelling.'''

    def __init__(self):
        self.check_os()
        self.unique_id = str(uuid.uuid4())
        self.port = config.getint('Server Parameters', 'port')
        self.tunnel_host = 'jaymartin.org'  # Eventually port this to tunnel.psiturk.org
        self.tunnel_server = os.path.join(os.path.dirname(__file__), "tunnel/ngrok")
        st = os.stat(self.tunnel_server)
        os.chmod(self.tunnel_server, st.st_mode | stat.S_IEXEC)  # Ensure ngrok is executable
        self.tunnel_config = os.path.join(os.path.dirname(__file__), "tunnel/ngrok-config")

    def check_os(self):
        is_64bit = struct.calcsize('P')*8 == 64

        if _platform == "linux" or _platform == "linux2" or "win32" or not is_64bit:
            Exception('Your OS is currently unsupported.')

    def open(self):
        cmd = '%s -subdomain=%s -config=%s -log=stdout %s 2>&1 > server.log &' %(self.tunnel_server, self.unique_id, self.tunnel_config, self.port)
        self.tunnel = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
        self.url = 'http://%s.%s:8000' %(self.unique_id, self.tunnel_host)

    def close(self):
        os.killpg(self.tunnel.pid, signal.SIGTERM)

