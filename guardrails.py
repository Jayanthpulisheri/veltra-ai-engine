import re
import datetime

# Forbidden patterns: Chained commands, destructive flags, & obfuscation
FORBIDDEN_PATTERNS = [
    r";",                     # Command chaining with semicolon
    r"&&",                    # Command chaining with AND
    r"\|\|",                  # Command chaining with OR
    r"\|",                    # Piping outputs
    r"rm\s+-rf",              # Recursive force deletion
    r"mkfs",                  # Disk formatting
    r"dd\s+if=",              # Raw disk writes
    r"base64\s+-d",           # Obfuscated payload execution
    r">+/dev/null"            # Hiding execution outputs
]

def is_command_safe(command: str) -> tuple[bool, str]:
    """
    Evaluates a CLI command locally before execution.
    Returns (True, "OK") if safe, or (False, reason) if blocked.
    """
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, command):
            reason = f"Blocked by Veltra Guardrail: Matches forbidden pattern '{pattern}'"
            log_audit_event(command, status="BLOCKED", reason=reason)
            return False, reason
            
    log_audit_event(command, status="ALLOWED", reason="Passed deterministic check")
    return True, "OK"

def log_audit_event(command: str, status: str, reason: str):
    """
    Appends execution metrics to veltra_audit.log for SecOps compliance.
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    log_entry = f"[{timestamp}] STATUS={status} | CMD='{command}' | REASON='{reason}'\n"
    
    with open("veltra_audit.log", "a") as f:
        f.write(log_entry)
