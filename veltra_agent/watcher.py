import json
import os
import time
from pathlib import Path
from typing import Callable, Dict, Any, Optional

class PolicyHotReloader:
    """
    Monitors veltra.config.json for modification time changes 
    and reloads configuration dynamically in real time.
    """
    def __init__(self, config_path: str = "veltra.config.json", on_reload_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.config_path = Path(config_path)
        self.on_reload_callback = on_reload_callback
        self.last_mtime: float = self._get_mtime()
        self.cached_config: Dict[str, Any] = self.load_config()

    def _get_mtime(self) -> float:
        if self.config_path.exists():
            return os.path.getmtime(self.config_path)
        return 0.0

    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[veltra] HOT-RELOAD ERROR: Failed to parse configuration file: {e}")
        return {}

    def check_for_updates(self) -> bool:
        """Checks if veltra.config.json has changed and updates cached config."""
        current_mtime = self._get_mtime()
        if current_mtime > self.last_mtime:
            self.last_mtime = current_mtime
            new_config = self.load_config()
            self.cached_config = new_config
            print(f"[veltra] HOT-RELOAD DETECTED: Policy updated dynamically from '{self.config_path}'")
            if self.on_reload_callback:
                self.on_reload_callback(new_config)
            return True
        return False
