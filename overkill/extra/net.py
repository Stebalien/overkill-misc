##
#    This file is part of Overkill-misc.
#
#    Overkill-misc is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Overkill-misc is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Overkill-misc.  If not, see <http://www.gnu.org/licenses/>.
##

from overkill.sinks import TimerSink
from overkill.sources import Source
import time
import os

BASE_PATH = "/sys/class/net/"
UP_TMPL = "/sys/class/net/%s/statistics/tx_bytes"
DOWN_TMPL = "/sys/class/net/%s/statistics/rx_bytes"

def read_file(self, path):
    with open(path) as f:
        return "\n".join(f.readlines())


class Iface:
    def __init__(self, iface):
        self.transfer = {}
        self.path = {"up": UP_TMPL % iface, "down": DOWN_TMPL % iface}
        self.iface = iface
    
    def get_speed(self, direction):
        xfer = read_file(self.path[direction])
        ts = time.now()
        if direction in self.transfer:
            speed = 0
        else:
            last_xfer, last_ts = self.transfer[direction]
            speed = float(xfer - last_xfer)/(ts - last_ts)
        self.transfer[direction] = (xfer, ts)
        return speed

    def get_upspeed(self):
        return self.get_speed("up")

    def get_downspeed(self):
        return self.get_speed("down")


class NetSource(Source, TimerSink):
    INTERVAL = 3
    interfaces = ("sys.netspeed",)
    keys = {"up", "down"}

    def __init__(self):
        self.ifaces = {iface: Iface(iface) for iface in os.listdir(BASE_PATH)}

    def is_publishing(self, sub):
        if isinstance(sub, tuple) and len(sub) == 2:
            return sub[0] in self.keys and sub[1] in self.ifaces
        elif isinstance(sub, str):
            return sub in self.keys
        elif sub == True:
            return True
        else:
            return False

    def tick(self):
        updates = {}

        for d in ("up", "down"):
            if True in self.subscribers or d in self.subscribers:
                total = 0
                for name, iface in self.ifaces.items():
                    speed = iface.get_speed(d)
                    updates[(d, name)] = speed
                    total += speed
                    updates[d] = total

        for sub in self.subscribers:
            if isinstance(sub, str):
                continue
            key, iface = sub
            iface = self.ifaces[iface]
            if key in self.subscribers:
                continue
            updates[sub] = iface.get_speed(key)

        if updates:
            self.push_updates(updates)

