"""
utils/config — Configuration loader with validation.
Reads from config.json + environment variable overrides (USM_*).
"""

import os
import json

DEFAULTS = {
    'host':                '0.0.0.0',
    'port':                8765,
    'api_port':            8766,
    'storage_path':        '/tmp/usm_storage',
    'max_frames_per_day':  10000,
    'retention_days':      7,
    'heartbeat_timeout':   30.0,
    'pair_timeout':        2.0,
    'log_level':           'INFO',
    'verbose':             False,
    'enable_api':          True,
}

REQUIRED = {'host', 'port', 'storage_path'}

def load(config_path: str = None) -> dict:
    cfg = dict(DEFAULTS)

    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            overrides = json.load(f)
        cfg.update(overrides)

    for k, default_val in DEFAULTS.items():
        env_key = f"USM_{k.upper()}"
        if env_key in os.environ:
            raw = os.environ[env_key]
            if isinstance(default_val, bool):
                cfg[k] = raw.lower() in ('1', 'true', 'yes')
            elif isinstance(default_val, float):
                cfg[k] = float(raw)
            elif isinstance(default_val, int):
                cfg[k] = int(raw)
            else:
                cfg[k] = raw

    _validate(cfg)
    return cfg

def _validate(cfg: dict):
    for key in REQUIRED:
        if not cfg.get(key):
            raise ValueError(f"[USM config] Required key missing: {key}")
    if not (1 <= int(cfg['port']) <= 65535):
        raise ValueError(f"[USM config] Invalid port: {cfg['port']}")
