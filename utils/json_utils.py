import json


def format_json(text: str) -> str:
    if not text.strip():
        return ""

    try:
        parsed = json.loads(text)

        return json.dumps(
            parsed,
            indent=4,
            ensure_ascii=False,
        )
    except json.JSONDecodeError:
        return text
