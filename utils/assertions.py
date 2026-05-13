from __future__ import annotations

from collections.abc import Mapping
from json import JSONDecodeError
from typing import Any

import requests

from utils.schemas import (
    ERROR_DETAIL_SCHEMA,
    ITEM_PUBLIC_SCHEMA,
    ITEMS_PUBLIC_SCHEMA,
    MESSAGE_SCHEMA,
    TOKEN_SCHEMA,
    USER_PUBLIC_SCHEMA,
    USERS_PUBLIC_SCHEMA,
    VALIDATION_ERROR_SCHEMA,
    validate_schema,
)


def assert_status(response: requests.Response, expected_status: int) -> None:
    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code}. Response: {response.text}"
    )


def assert_json_object(response: requests.Response) -> dict[str, Any]:
    try:
        body = response.json()
    except JSONDecodeError as exc:
        raise AssertionError(f"Response is not valid JSON. Body: {response.text}") from exc
    assert isinstance(body, dict), f"Expected JSON object, got: {type(body)}"
    return body


def assert_error_detail(
    response: requests.Response,
    expected_status: int,
    expected_detail: str | None = None,
) -> str:
    assert_status(response, expected_status)
    body = assert_json_object(response)
    validate_schema(body, ERROR_DETAIL_SCHEMA)
    detail = body["detail"]
    if expected_detail is not None:
        assert detail == expected_detail
    return detail


def assert_validation_error(response: requests.Response) -> None:
    assert_status(response, 422)
    body = assert_json_object(response)
    validate_schema(body, VALIDATION_ERROR_SCHEMA)


def assert_message_response(
    response: requests.Response,
    expected_status: int = 200,
    expected_message: str | None = None,
) -> str:
    assert_status(response, expected_status)
    body = assert_json_object(response)
    validate_schema(body, MESSAGE_SCHEMA)
    message = body["message"]
    if expected_message is not None:
        assert message == expected_message
    return message


def assert_token_response(response: requests.Response) -> str:
    assert_status(response, 200)
    body = assert_json_object(response)
    validate_schema(body, TOKEN_SCHEMA)
    return body["access_token"]


def assert_user_public(body: Mapping[str, Any], expected_email: str | None = None) -> None:
    validate_schema(dict(body), USER_PUBLIC_SCHEMA)
    if expected_email is not None:
        assert body["email"] == expected_email


def assert_users_public(body: Mapping[str, Any]) -> None:
    validate_schema(dict(body), USERS_PUBLIC_SCHEMA)


def assert_item_public(
    body: Mapping[str, Any],
    expected_title: str | None = None,
    expected_description: str | None = None,
) -> None:
    validate_schema(dict(body), ITEM_PUBLIC_SCHEMA)
    if expected_title is not None:
        assert body["title"] == expected_title
    if expected_description is not None:
        assert body.get("description") == expected_description


def assert_list_public(body: Mapping[str, Any]) -> None:
    validate_schema(dict(body), ITEMS_PUBLIC_SCHEMA)
