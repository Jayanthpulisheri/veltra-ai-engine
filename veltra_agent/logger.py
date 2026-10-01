import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

def log_event(
    command: str,
    status: str,
    reason: Optional[str] = None,
    log_file: str = "veltra_audit.log"
) -> None:
    log_path = Path(log_file)
    
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "status": status,
        "reason": reason or ("Allowed by policy" if status == "ALLOWED" else "Blocked by policy"),
        "platform": sys.platform,
        "pid": os.getpid()
    }
    
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"[veltra] Warning: Failed to write to audit log: {e}", file=sys.stderr)
