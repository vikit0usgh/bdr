from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ResponseVariable:
    name: str
    json_path: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "json_path": self.json_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResponseVariable":
        return cls(
            name=data.get("name", ""),
            json_path=data.get("json_path", ""),
        )


@dataclass
class HttpRequest:
    name: str = "New Request"
    method: str = "GET"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    response_variables: List[ResponseVariable] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "response_variables": [
                variable.to_dict()
                for variable in self.response_variables
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HttpRequest":
        return cls(
            name=data.get("name", "New Request"),
            method=data.get("method", "GET"),
            url=data.get("url", ""),
            headers=data.get("headers", {}),
            body=data.get("body", ""),
            response_variables=[
                ResponseVariable.from_dict(item)
                for item in data.get("response_variables", [])
            ],
        )
