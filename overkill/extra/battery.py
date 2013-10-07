import logging, os
import fnmatch
from overkill.sinks import TimerSink
from overkill.sources import Source

logger = logging.getLogger("bar:sources:battery")

BASE_PATH = "/sys/class/power_supply/"

def read_file(self, path):
    with open(path) as f:
        return "\n".join(f.readlines())

class Battery:
    def __init__(self, name):
        self.path = BASE_PATH+name+"/"
        self._status_path = self.path+"status"
        if os.exists(self.path+"capacity"):
            self._cap_path = self.path+"capacity"
            self.get_charge = self._get_charge_capacity
        elif os.exists(self.path+"energy_now"):
            self._now_path = self.path+"energy_now"
            self._full_path = self.path+"energy_full"
            self.get_charge = self._get_charge_calc
        elif os.exists(self.path+"charge_now"):
            self._now_path = self.path+"charge_now"
            self._full_path = self.path+"charge_full"
            self.get_charge = self._get_charge_calc

    def get(self, key):
        if key == "battery_charge":
            return self.get_charge()
        else:
            return self.get_status()

    def get_charge(self):
        return None

    def get_status(self):
        return float(read_file(self._status_path))

    def _get_charge_calc(self):
        now = float(read_file(self._now_path))
        full = float(read_file(self._full_path))
        return now/full*100

    def _get_charge_capacity(self):
        return float(self.read_file(self._cap_path))

class BatterySource(Source, TimerSink):
    INTERVAL = 10
    keys = {"battery_charge", "battery_status"}

    def __init__(self):
        self.batteries = {bat: Battery(bat) for bat in fnmatch.filter(os.listdir(BASE_PATH), "BAT*")}
        self.default_battery = self.batteries[sorted(self.batteries.keys())[0]]

    def is_publishing(self, sub):
        if isinstance(sub, tuple) and len(sub) == 2:
            return sub[0] in self.keys and sub[1] in self.batteries
        elif isinstance(sub, str):
            return sub in self.keys
        else:
            return False

    def tick(self):
        try:
            updates = {}
            for sub in self.subscribers:
                if isinstance(sub, tuple):
                    key, bat = sub
                    bat = self.batteries[bat]
                else:
                    key = sub
                    bat = self.default_battery
                if (key, bat) in updates:
                    continue
                stat = bat.get(key)
                updates[sub] = stat
                if isinstance(sub, str):
                    updates[(key, bat)] = stat

            if updates:
                self.push_updates(updates)
        except Exception as e:
            logger.error(e)

