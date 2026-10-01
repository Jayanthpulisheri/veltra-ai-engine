import re
from typing import List, Tuple

# Pattern to detect explicit network requests and port flags in commands
PORT_PATTERNS = [
    r"(?:nc|netcat|ncat|telnet|curl|wget)\s+.*:(\d+)",
    r"-p\s*(\d+)",
    r"--port[=\s](\d+)"
]

def inspect_network_rules(command_str: str, allowed_ports: List[int]) -> Tuple[bool, str]:
    """
    Parses execution string for explicit port calls and verifies against policy.
    """
    for pattern in PORT_PATTERNS:
        matches = re.findall(pattern, command_str)
        for match in matches:
            port = int(match)
            if port not in allowed_ports:
                return False, f"Unauthorized outbound port access detected: port {port} is not in allowed_ports {allowed_ports}"
                
    return True, "Network policy verified"
