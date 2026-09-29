from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Environment:
    name: str = "Default"
    variables: Dict[str, str] = field(default_factory=dict)

    def get(self, name: str, default=None):
        return self.variables.get(name, default)

    def set(self, name: str, value: str):
        self.variables[name] = value
