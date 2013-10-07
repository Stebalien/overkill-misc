from overkill.sinks import PipeSink, Sink
from overkill.sources import Source

__all__ = ["XPropSource"]

class XPropWorkerSource(Source, PipeSink):
    def __init__(self, id, props = []):
        pass


class XPropSource(Source, Sink):
    pass
