import re
from typing import List, Tuple

RESTRICTED_WRITE_PATHS = [
    "/etc", "/usr", "/bin", "/sbin", "/boot", "/sys", "/proc", "/root"
]

WRITE_OPERATIONS = [
    r">\s*([/\w\.-]+)",
    r">>\s*([/\w\.-]+)",
    r"rm\s+-[rfRF]*\s+([/\w\.-]+)",
    r"cp\s+.*\s+([/\w\.-]+)",
    r"mv\s+.*\s+([/\w\.-]+)",
]

def inspect_filesystem_rules(command_str: str, read_only_root: bool) -> Tuple[bool, str]:
    if not read_only_root:
        return True, "Filesystem restrictions disabled"

    for pattern in WRITE_OPERATIONS:
        matches = re.findall(pattern, command_str)
        for target in matches:
            target_clean = target.strip()
            for restricted in RESTRICTED_WRITE_PATHS:
                if target_clean.startswith(restricted):
                    return False, f"Unauthorized write attempt to restricted path '{target_clean}'"

    return True, "Filesystem sandbox verified"
