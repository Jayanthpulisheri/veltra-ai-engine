import re
from typing import List, Tuple, Dict, Any

SENSITIVE_KEY_PATTERNS = [
    r".*API_KEY.*",
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*TOKEN.*",
    r".*PRIVATE_KEY.*"
]

def sanitize_environment(env_vars: Dict[str, str]) -> Dict[str, str]:
    clean_env = env_vars.copy()
    for key in list(clean_env.keys()):
        for pattern in SENSITIVE_KEY_PATTERNS:
            if re.match(pattern, key, re.IGNORECASE):
                clean_env[key] = "[REDACTED_BY_VELTRA]"
                break
    return clean_env

def inspect_environment_leak(command_str: str) -> Tuple[bool, str]:
    for pattern in SENSITIVE_KEY_PATTERNS:
        regex = re.compile(rf"(?:\$|env|printenv|echo).*{pattern}", re.IGNORECASE)
        if regex.search(command_str):
            return False, f"Potential environment secret leak detected matching pattern '{pattern}'"
            
    return True, "Environment safety verified"
