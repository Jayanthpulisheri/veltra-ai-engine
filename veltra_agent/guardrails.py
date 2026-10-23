import importlib
import pkgutil
from typing import Dict, Any, List
from .rules.base import BaseVeltraRule

class VeltraGuardrails:
    def __init__(self):
        self.rules: List[BaseVeltraRule] = []
        self._load_rules()

    def _load_rules(self):
        import veltra_agent.rules as rules_pkg
        for _, module_name, _ in pkgutil.iter_modules(rules_pkg.__path__):
            if module_name in ["base", "__init__"]:
                continue
            module = importlib.import_module(f"veltra_agent.rules.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseVeltraRule) and attr is not BaseVeltraRule:
                    self.rules.append(attr())

    def inspect(self, command: str) -> Dict[str, Any]:
        for rule in self.rules:
            result = rule.inspect(command)
            if not result.get("allowed", True):
                return result
        return {"allowed": True, "reason": "All Veltra Security Hub rules passed."}
