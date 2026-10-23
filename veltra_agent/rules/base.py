from typing import Dict, Any

class BaseVeltraRule:
    """Base class for all Veltra Security Hub rules."""
    rule_id: str = "base_rule"
    description: str = "Base rule class"

    def inspect(self, command: str) -> Dict[str, Any]:
        raise NotImplementedError("Each rule must implement the inspect method.")
