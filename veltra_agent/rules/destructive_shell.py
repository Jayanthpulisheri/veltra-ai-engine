import re
from typing import Dict, Any
from .base import BaseVeltraRule

class DestructiveShellRule(BaseVeltraRule):
    rule_id = "destructive_shell"
    description = "Blocks high-risk shell destruction commands (rm -rf, mkfs, dd)."

    PATTERNS = [
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+\*",
        r"mkfs",
        r"dd\s+if="
    ]

    def inspect(self, command: str) -> Dict[str, Any]:
        for pattern in self.PATTERNS:
            if re.search(pattern, command):
                return {
                    "allowed": False,
                    "rule_id": self.rule_id,
                    "reason": f"Destructive command detected matching pattern: {pattern}"
                }
        return {"allowed": True, "rule_id": self.rule_id, "reason": "Passed"}
