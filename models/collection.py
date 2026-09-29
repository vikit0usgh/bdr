from dataclasses import dataclass, field
from typing import Dict, List

from models.request import HttpRequest


@dataclass
class Collection:
    name: str = "My Collection"
    variables: Dict[str, str] = field(default_factory=dict)
    requests: List[HttpRequest] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "variables": self.variables,
            "requests": [
                request.to_dict()
                for request in self.requests
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Collection":
        return cls(
            name=data.get("name", "My Collection"),
            variables=data.get("variables", {}),
            requests=[
                HttpRequest.from_dict(item)
                for item in data.get("requests", [])
            ],
        )
