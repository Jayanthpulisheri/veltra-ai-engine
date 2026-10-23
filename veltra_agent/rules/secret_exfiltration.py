import re
from typing import Dict, Any
from .base import BaseVeltraRule

class SecretExfiltrationRule(BaseVeltraRule):
    rule_id = "secret_exfiltration"
    description = "Prevents printing or exfiltrating environment files (.env)."

    PATTERNS = [
        r"cat\s+.*\.env",
        r"printenv\s*>",
        r"curl.*--data.*\.env"
    ]

    def inspect(self, command: str) -> Dict[str, Any]:
        for pattern in self.PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "allowed": False,
                    "rule_id": self.rule_id,
                    "reason": f"Secret exfiltration pattern detected: {pattern}"
                }
        return {"allowed": True, "rule_id": self.rule_id, "reason": "Passed"}
