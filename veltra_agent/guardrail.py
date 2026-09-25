import datetime
import json
import os
import re

DEFAULT_FORBIDDEN = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r"mkfs",
    r"dd\s+if=",
    r":\(\)\{\s*:\|\:&\s*\};:",
    r">\s*/dev/sd",
    r"base64\s+-d"
]

DEFAULT_CHAINED = [
    r"&&",
    r"\|\|",
    r";"
]

def load_config():
    """Loads workspace veltra.config.json or defaults."""
    config_file = "veltra.config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
                return data.get("forbidden_patterns", DEFAULT_FORBIDDEN), data.get("chained_patterns", DEFAULT_CHAINED)
        except Exception:
            pass
    return DEFAULT_FORBIDDEN, DEFAULT_CHAINED

def log_audit_event(command: str, status: str, reason: str, log_file: str = "veltra_audit.log"):
    """Logs security events with UTC timestamps."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    log_entry = f"[{timestamp}] STATUS={status} | CMD='{command}' | REASON='{reason}'\n"
    with open(log_file, "a") as f:
        f.write(log_entry)

def is_command_safe(command: str) -> tuple[bool, str]:
    """Evaluates terminal commands against active workspace policy rules."""
    forbidden_patterns, chained_patterns = load_config()

    # Check 1: Forbidden destructive patterns
    for pattern in forbidden_patterns:
        if re.search(pattern, command):
            reason = f"Blocked by Veltra Guardrail: Matches forbidden pattern '{pattern}'"
            log_audit_event(command, status="BLOCKED", reason=reason)
            return False, reason

    # Check 2: Chained injection attacks
    for pattern in chained_patterns:
        if pattern in command and ("rm -rf" in command or "sudo" in command):
            reason = f"Blocked by Veltra Guardrail: Matches unsafe command chain containing '{pattern}'"
            log_audit_event(command, status="BLOCKED", reason=reason)
            return False, reason

    # Safe Command Passed
    log_audit_event(command, status="ALLOWED", reason="Passed deterministic check")
    return True, "Passed deterministic check"
