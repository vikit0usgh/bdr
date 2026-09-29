import json
import time
from typing import Dict, Tuple

import requests


class HttpClient:
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")

    def send(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] | None = None,
        body: str = "",
        timeout: int = 30,
    ) -> Tuple[int, float, str, Dict[str, str]]:
        method = method.upper()
        headers = headers or {}

        if not url.strip():
            raise ValueError("A URL não pode estar vazia.")

        if method not in self.SUPPORTED_METHODS:
            raise ValueError(f"Método HTTP não suportado: {method}")

        kwargs = {
            "headers": headers,
            "timeout": timeout,
        }

        if body.strip() and method in {"POST", "PUT", "PATCH", "DELETE"}:
            try:
                kwargs["json"] = json.loads(body)
            except json.JSONDecodeError:
                kwargs["data"] = body

        start = time.perf_counter()

        response = requests.request(
            method=method,
            url=url,
            **kwargs,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        return (
            response.status_code,
            elapsed_ms,
            response.text,
            dict(response.headers),
        )
