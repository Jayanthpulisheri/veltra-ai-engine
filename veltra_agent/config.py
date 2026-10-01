import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "version": "0.1.1",
    "guardrails": {
        "blocked_commands": [
            "rm -rf /",
            "mkfs",
            "dd",
            "> /dev/sda"
        ],
        "allowed_outbound_ports": [80, 443],
        "enforce_read_only_root": True,
        "max_subprocess_timeout_seconds": 300
    },
    "logging": {
        "enabled": True,
        "log_file": "veltra_audit.log",
        "format": "json"
    }
}

def init_config(force: bool = False) -> str:
    config_path = Path("veltra.config.json")
    
    if config_path.exists() and not force:
        return "[veltra] Configuration file 'veltra.config.json' already exists. Use '--force' or '-f' to overwrite."
        
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
        
    return f"[veltra] Initialized default configuration at '{config_path.resolve()}'"
