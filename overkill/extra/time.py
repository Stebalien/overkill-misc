from overkill.sinks import TimerSink
from overkill.sources import Source
import time

class TimeSource(Source, TimerSink):
    publishes = ["time"]

    MIN_INTERVAL = 50
    MAX_INTERVAL = 60

    def tick(self):
        self.push_updates({"time": time.localtime()})
