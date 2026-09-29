import json
import re
from typing import Any, Dict


VARIABLE_PATTERN = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_.-]*)\}\}")


class VariableService:
    """
    Resolve variáveis no formato {{nome}} e extrai valores simples
    de JSON usando paths como $.token ou $.user.id.
    """

    def __init__(self, variables: Dict[str, Any] | None = None):
        self.variables = variables or {}

    def set(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def get(self, name: str, default=None):
        return self.variables.get(name, default)

    def resolve(self, text: str) -> str:
        if not isinstance(text, str):
            return text

        def replace(match):
            name = match.group(1)

            if name not in self.variables:
                # Mantém a variável original para facilitar identificação.
                return match.group(0)

            value = self.variables[name]

            if isinstance(value, (dict, list)):
                return json.dumps(
                    value,
                    ensure_ascii=False,
                )

            return str(value)

        return VARIABLE_PATTERN.sub(replace, text)

    def resolve_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: self.resolve(str(value))
            for key, value in data.items()
        }

    @staticmethod
    def extract_json_path(payload: Any, json_path: str) -> Any:
        """
        Implementação de JSON Path simples.

        Exemplos:
            $.token
            $.user.id
            $.data.access_token

        Também suporta índices:
            $.items.0.id
        """
        if not json_path.startswith("$."):
            raise ValueError(
                "JSON Path deve começar com '$.'"
            )

        path = json_path[2:]

        if not path:
            return payload

        current = payload

        for part in path.split("."):
            if isinstance(current, dict):
                if part not in current:
                    raise KeyError(
                        f"Campo '{part}' não encontrado."
                    )

                current = current[part]

            elif isinstance(current, list):
                try:
                    index = int(part)
                except ValueError as exc:
                    raise KeyError(
                        f"'{part}' não é um índice de lista."
                    ) from exc

                try:
                    current = current[index]
                except IndexError as exc:
                    raise KeyError(
                        f"Índice '{index}' não encontrado."
                    ) from exc

            else:
                raise KeyError(
                    f"Não foi possível acessar '{part}' em "
                    f"'{current}'."
                )

        return current

    def extract_from_response(
        self,
        response_text: str,
        json_path: str,
    ) -> Any:
        payload = json.loads(response_text)

        return self.extract_json_path(
            payload,
            json_path,
        )
