from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

TOKEN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["access_token"],
    "properties": {
        "access_token": {"type": "string", "minLength": 1},
        "token_type": {"type": "string", "const": "bearer"},
    },
    "additionalProperties": False,
}

MESSAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["message"],
    "properties": {"message": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}

ERROR_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["detail"],
    "properties": {"detail": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}

VALIDATION_ERROR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["detail"],
    "properties": {
        "detail": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["loc", "msg", "type"],
                "properties": {
                    "loc": {"type": "array", "items": {"type": ["string", "integer"]}},
                    "msg": {"type": "string"},
                    "type": {"type": "string"},
                    "input": {},
                    "ctx": {"type": "object"},
                },
                "additionalProperties": True,
            },
        }
    },
    "additionalProperties": True,
}

USER_PUBLIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["id", "email"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "email": {"type": "string", "format": "email", "maxLength": 255},
        "full_name": {"type": ["string", "null"], "maxLength": 255},
        "is_active": {"type": "boolean"},
        "is_superuser": {"type": "boolean"},
        "created_at": {"type": ["string", "null"], "format": "date-time"},
    },
    "additionalProperties": False,
}

USERS_PUBLIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["data", "count"],
    "properties": {
        "data": {"type": "array", "items": USER_PUBLIC_SCHEMA},
        "count": {"type": "integer", "minimum": 0},
    },
    "additionalProperties": False,
}

ITEM_PUBLIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["id", "title", "owner_id"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "title": {"type": "string", "minLength": 1, "maxLength": 255},
        "description": {"type": ["string", "null"], "maxLength": 255},
        "owner_id": {"type": "string", "format": "uuid"},
        "created_at": {"type": ["string", "null"], "format": "date-time"},
    },
    "additionalProperties": False,
}

ITEMS_PUBLIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["data", "count"],
    "properties": {
        "data": {"type": "array", "items": ITEM_PUBLIC_SCHEMA},
        "count": {"type": "integer", "minimum": 0},
    },
    "additionalProperties": False,
}


def validate_schema(instance: Any, schema: dict[str, Any]) -> None:
    """Validate a response body against a JSON Schema and raise readable pytest errors."""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    assert not errors, "\n".join(f"schema error at {list(error.path) or '<root>'}: {error.message}" for error in errors)
