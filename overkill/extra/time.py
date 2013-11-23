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

class TimeSource(Source, TimerSink):
    publishes = ["time"]

    MIN_INTERVAL = 50
    MAX_INTERVAL = 60

    def tick(self):
        self.push_updates({"time": time.localtime()})
