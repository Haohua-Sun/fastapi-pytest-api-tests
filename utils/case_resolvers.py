from __future__ import annotations

import secrets
import time
from collections.abc import Mapping
from typing import Any

TEXT_PLACEHOLDERS = {
    "__MISSING__": None,
    "__TITLE_LEN_1__": "T",
    "__TITLE_LEN_255__": "T" * 255,
    "__TITLE_OVER_255__": "T" * 256,
    "__DESC_LEN_255__": "D" * 255,
    "__DESC_OVER_255__": "D" * 256,
}

NOT_EXIST_ITEM_ID = "00000000-0000-0000-0000-000000000001"


def resolve_auth_token(auth_type: str, valid_token: str) -> str | None:
    tokens = {
        "valid_token": valid_token,
        "invalid_token": "invalid_token",
        "missing_token": None,
    }
    if auth_type not in tokens:
        raise ValueError(f"Unknown auth_type: {auth_type}")
    return tokens[auth_type]


def resolve_optional_text(value: str) -> str | None:
    return TEXT_PLACEHOLDERS.get(value, value)


def resolve_item_id(id_source: str, created_item_id: str) -> str:
    item_ids = {
        "env_item_id": created_item_id,
        "not_exist": NOT_EXIST_ITEM_ID,
        "invalid_uuid": "bad_id",
    }
    if id_source not in item_ids:
        raise ValueError(f"Unknown id_source: {id_source}")
    return item_ids[id_source]


def build_case_id(case: Mapping[str, Any]) -> str:
    """Build stable and readable pytest parameter ids from JSON test cases."""
    case_id = case.get("case_id", "<missing-case-id>")
    desc = case.get("desc", "<missing-desc>")
    return f"{case_id} - {desc}"


def random_email(prefix: str = "pytest") -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{secrets.token_hex(4)}@example.com"


def random_password() -> str:
    return f"Pass{secrets.randbelow(900000) + 100000}!"
