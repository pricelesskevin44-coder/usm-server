"""
storage/rolling — Rolling log rotation + retention policy enforcement.
"""

import os
import glob
import shutil
from datetime import datetime, timedelta

DEFAULT_BASE = os.path.join(os.path.expanduser("~"), "usm_data")

class RollingManager:
    def __init__(
        self,
        base_path:          str = DEFAULT_BASE,
        max_frames_per_day: int = 10000,
        retention_days:     int = 7,
    ):
        self.base           = base_path
        self.max_frames     = max_frames_per_day
        self.retention_days = retention_days

    def enforce_frame_limit(self, namespace: str):
        safe  = namespace.replace('/', '__')
        today = datetime.utcnow().strftime('%Y-%m-%d')
        dir_  = os.path.join(self.base, safe, today)
        if not os.path.isdir(dir_):
            return
        files  = sorted(glob.glob(os.path.join(dir_, '*.json')))
        excess = len(files) - self.max_frames
        for f in files[:max(0, excess)]:
            os.remove(f)
            b = f.replace('.json', '.bin')
            if os.path.exists(b):
                os.remove(b)

    def purge_old_days(self, namespace: str):
        safe   = namespace.replace('/', '__')
        ns_dir = os.path.join(self.base, safe)
        if not os.path.isdir(ns_dir):
            return
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        for day_folder in os.listdir(ns_dir):
            try:
                if datetime.strptime(day_folder, '%Y-%m-%d') < cutoff:
                    shutil.rmtree(os.path.join(ns_dir, day_folder), ignore_errors=True)
            except ValueError:
                pass

    def run_all(self, namespace: str):
        self.enforce_frame_limit(namespace)
        self.purge_old_days(namespace)

rolling = RollingManager()
