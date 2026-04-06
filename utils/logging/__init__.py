"""
utils/logging — Structured JSON event logger with debug/verbose modes.
"""

import time
import json
import sys
import os

LEVELS = {'DEBUG': 0, 'INFO': 1, 'WARN': 2, 'ERROR': 3}

class USMLogger:
    def __init__(self, level: str = None, sink=sys.stdout):
        env_level   = os.environ.get('USM_LOG_LEVEL', 'INFO').upper()
        self.level  = LEVELS.get(level or env_level, 1)
        self.sink   = sink
        self.verbose = os.environ.get('USM_VERBOSE', '0') == '1'

    def _emit(self, level: str, event: str, **kw):
        if LEVELS.get(level, 99) < self.level:
            return
        record = {'ts': round(time.time(), 6), 'level': level, 'event': event}
        if self.verbose:
            record.update(kw)
        print(json.dumps(record), file=self.sink, flush=True)

    def debug(self, e, **kw): self._emit('DEBUG', e, **kw)
    def info(self,  e, **kw): self._emit('INFO',  e, **kw)
    def warn(self,  e, **kw): self._emit('WARN',  e, **kw)
    def error(self, e, **kw): self._emit('ERROR', e, **kw)

logger = USMLogger()
