from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import allure
import requests

SENSITIVE_HEADER_NAMES = {"authorization", "cookie", "set-cookie"}
SENSITIVE_BODY_KEYS = {"password", "access_token", "token", "refresh_token"}
MAX_TEXT_LENGTH = 2000


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return normalized in SENSITIVE_HEADER_NAMES or normalized in SENSITIVE_BODY_KEYS or "password" in normalized


def _redact_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _redact_mapping(value)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(item) for item in value)
    return value


def _redact_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in data.items():
        if _is_sensitive_key(str(key)):
            redacted[key] = "<redacted>"
        else:
            redacted[key] = _redact_value(value)
    return redacted


def _truncate_text(text: str) -> str:
    if len(text) <= MAX_TEXT_LENGTH:
        return text
    return f"{text[:MAX_TEXT_LENGTH]}... <truncated>"


def attach_json(name: str, data: Any) -> None:
    allure.attach(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_request(method: str, url: str, request_kwargs: Mapping[str, Any], name: str = "HTTP request") -> None:
    meta: dict[str, Any] = {
        "method": method.upper(),
        "url": url,
    }
    for key in ("params", "headers", "json", "data", "timeout"):
        if key in request_kwargs:
            meta[key] = _redact_value(request_kwargs[key])
    attach_json(name, meta)


def attach_response(response: requests.Response, name: str = "HTTP response") -> None:
    request = response.request
    meta = {
        "method": request.method,
        "url": request.url,
        "status_code": response.status_code,
        "elapsed_seconds": response.elapsed.total_seconds(),
        "request_headers": _redact_mapping(dict(request.headers)),
        "response_headers": _redact_mapping(dict(response.headers)),
        "response_text": _truncate_text(response.text),
    }
    attach_json(name, meta)
