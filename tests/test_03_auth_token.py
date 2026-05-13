import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import assert_error_detail, assert_json_object, assert_status, assert_user_public


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Authentication")
@allure.story("Token validation success")
@pytest.mark.auth
def test_test_token_success(api_client: ApiClient, admin_token: str):
    with allure.step("Call test-token with valid admin token"):
        response = api_client.test_token(admin_token)

    assert_status(response, 200)
    body = assert_json_object(response)
    assert_user_public(body)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Authentication")
@allure.story("Token validation failures")
@pytest.mark.auth
@pytest.mark.parametrize(
    "token, expected_status, expected_detail",
    [
        ("invalid_token", 403, "Could not validate credentials"),
        ("", 403, "Could not validate credentials"),
        (None, 401, "Not authenticated"),
    ],
    ids=["invalid token", "empty token", "missing token"],
)
def test_test_token_failed(api_client: ApiClient, token: str | None, expected_status: int, expected_detail: str):
    response = api_client.test_token(token)

    assert_error_detail(response, expected_status, expected_detail=expected_detail)
