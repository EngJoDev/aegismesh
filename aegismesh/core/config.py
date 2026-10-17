"""
AegisMesh - Configuration Engine & Threat Rulesets.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List

DEFAULT_CONFIG: Dict[str, Any] = {
    "server": {
        "host": "0.0.0.0",
        "port": 8088,
        "workers": 4,
        "max_body_size_mb": 10
    },
    "upstream": {
        "default_target": "https://httpbin.org",
        "timeout_seconds": 15,
        "retry_count": 2
    },
    "security": {
        "waf_enabled": True,
        "prompt_injection_guard": True,
        "pii_masking": True,
        "blocked_ips": [],
        "secret_token": "aegis-secret-key-2026"
    },
    "rate_limiting": {
        "enabled": True,
        "algorithm": "token_bucket",  # token_bucket | sliding_window
        "requests_per_minute": 60,
        "burst_capacity": 10
    },
    "cache": {
        "enabled": True,
        "ttl_seconds": 300,
        "max_entries": 1000
    }
}

class Config:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_path = Path(config_file)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
                    merged = DEFAULT_CONFIG.copy()
                    for k, v in loaded.items():
                        if isinstance(v, dict) and k in merged:
                            merged[k].update(v)
                        else:
                            merged[k] = v
                    return merged
            except Exception:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.data.get(section, {}).get(key, default)

    def save(self, target_path: str = "config.yaml") -> None:
        with open(target_path, "w", encoding="utf-8") as f:
            yaml.dump(self.data, f, default_flow_style=False)
