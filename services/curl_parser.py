import base64
import shlex
from typing import Dict, List, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit


class CurlParseError(ValueError):
    pass


class CurlParser:
    METHOD_FLAGS = {"-X", "--request"}
    HEADER_FLAGS = {"-H", "--header"}
    BODY_FLAGS = {
        "-d", "--data", "--data-raw", "--data-binary",
        "--data-ascii", "--data-urlencode",
    }
    FORM_FLAGS = {"-F", "--form"}
    URL_FLAGS = {"--url"}
    AUTH_FLAGS = {"-u", "--user"}
    COOKIE_FLAGS = {"-b", "--cookie"}

    IGNORED_WITH_VALUE = {
        "--connect-timeout", "--max-time", "--retry",
        "--retry-delay", "--proxy", "--proxy-user",
        "--cert", "--key", "--cacert", "--cookie-jar",
        "-o", "--output", "--interface",
    }

    IGNORED = {
        "-k", "--insecure", "-L", "--location", "--compressed",
        "-s", "--silent", "-S", "--show-error", "-v", "--verbose",
        "--http1.1", "--http2", "--http2-prior-knowledge",
        "--globoff", "--fail", "--fail-with-body", "--remote-name", "-N",
    }

    @classmethod
    def is_curl(cls, text: str) -> bool:
        text = text.strip()
        if not text:
            return False
        try:
            tokens = shlex.split(text, posix=True)
        except ValueError:
            return text.lower().startswith("curl ")
        return bool(tokens) and tokens[0].lower() in {"curl", "curl.exe"}

    @classmethod
    def parse(cls, command: str):
        parsed = cls.parse_request(command)
        return parsed["method"], parsed["url"], parsed["headers"], parsed["body"]

    @classmethod
    def parse_request(cls, command: str) -> dict:
        if not cls.is_curl(command):
            raise CurlParseError("O texto informado não parece ser um comando cURL.")

        command = command.strip().replace("\\\r\n", " ").replace("\\\n", " ")
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError as exc:
            raise CurlParseError(f"Não foi possível interpretar as aspas: {exc}") from exc

        if not tokens or tokens[0].lower() not in {"curl", "curl.exe"}:
            raise CurlParseError("O comando precisa começar com 'curl'.")

        method = None
        url = None
        headers: Dict[str, str] = {}
        body_parts: List[str] = []
        form_data: List[str] = []
        cookies: List[str] = []
        urlencoded: List[Tuple[str, str]] = []
        basic_auth = None

        i = 1
        while i < len(tokens):
            token = tokens[i]

            if token.startswith("--request="):
                method = token.split("=", 1)[1].upper()
                i += 1
                continue
            if token.startswith("--url="):
                url = token.split("=", 1)[1]
                i += 1
                continue
            if token.startswith("--header="):
                cls._add_header(headers, token.split("=", 1)[1])
                i += 1
                continue
            if token.startswith("--data-urlencode="):
                urlencoded.append(cls._parse_urlencode(token.split("=", 1)[1]))
                i += 1
                continue
            if token.startswith("--data-raw=") or token.startswith("--data="):
                body_parts.append(token.split("=", 1)[1])
                i += 1
                continue
            if token.startswith("--form="):
                form_data.append(token.split("=", 1)[1])
                i += 1
                continue
            if token.startswith("--user="):
                basic_auth = token.split("=", 1)[1]
                i += 1
                continue
            if token.startswith("--cookie="):
                cookies.append(token.split("=", 1)[1])
                i += 1
                continue

            if token in cls.METHOD_FLAGS:
                method, i = cls._next(tokens, i, token)
                method = method.upper()
                continue
            if token in cls.HEADER_FLAGS:
                value, i = cls._next(tokens, i, token)
                cls._add_header(headers, value)
                continue
            if token in cls.BODY_FLAGS:
                value, i = cls._next(tokens, i, token)
                if token == "--data-urlencode":
                    urlencoded.append(cls._parse_urlencode(value))
                else:
                    body_parts.append(value)
                continue
            if token in cls.FORM_FLAGS:
                value, i = cls._next(tokens, i, token)
                form_data.append(value)
                continue
            if token in cls.URL_FLAGS:
                url, i = cls._next(tokens, i, token)
                continue
            if token in cls.AUTH_FLAGS:
                basic_auth, i = cls._next(tokens, i, token)
                continue
            if token in cls.COOKIE_FLAGS:
                value, i = cls._next(tokens, i, token)
                cookies.append(value)
                continue
            if token in cls.IGNORED_WITH_VALUE:
                _, i = cls._next(tokens, i, token)
                continue
            if token in cls.IGNORED or token.startswith("-"):
                i += 1
                continue

            if url is None:
                url = token
            else:
                body_parts.append(token)
            i += 1

        if not url:
            raise CurlParseError("Não foi possível encontrar a URL no cURL.")

        if basic_auth and "Authorization" not in headers:
            encoded = base64.b64encode(basic_auth.encode()).decode("ascii")
            headers["Authorization"] = f"Basic {encoded}"

        if cookies and "Cookie" not in headers:
            headers["Cookie"] = "; ".join(cookies)

        query_params = dict(parse_qsl(
            urlsplit(url).query,
            keep_blank_values=True,
        ))

        if urlencoded:
            body_parts.append(urlencode(urlencoded, doseq=True))

        body = "&".join(body_parts) if body_parts else ""

        if form_data:
            body = "\n".join(form_data)
            if "Content-Type" not in headers:
                headers["Content-Type"] = "multipart/form-data"

        if method is None:
            method = "POST" if (body_parts or form_data) else "GET"

        return {
            "method": method,
            "url": url,
            "headers": headers,
            "body": body,
            "form_data": form_data,
            "query_params": query_params,
            "cookies": cookies,
            "auth": basic_auth,
        }

    @staticmethod
    def _next(tokens, index, flag):
        if index + 1 >= len(tokens):
            raise CurlParseError(f"A opção '{flag}' precisa de um valor.")
        return tokens[index + 1], index + 2

    @staticmethod
    def _add_header(headers, value):
        if ":" not in value:
            raise CurlParseError(
                f"Header inválido: '{value}'. Esperado 'Nome: valor'."
            )
        name, val = value.split(":", 1)
        if not name.strip():
            raise CurlParseError(f"Header inválido: '{value}'.")
        headers[name.strip()] = val.strip()

    @staticmethod
    def _parse_urlencode(value):
        return tuple(value.split("=", 1)) if "=" in value else ("", value)
