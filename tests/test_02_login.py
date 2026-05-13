import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import assert_error_detail, assert_status, assert_token_response, assert_validation_error
from utils.case_resolvers import build_case_id
from utils.data_loader import load_json_cases

LOGIN_CASES = load_json_cases(
    "login_cases.json",
    required_keys={"case_id", "desc", "username_source", "username", "password_source", "password", "expected_status"},
    enum_fields={
        "username_source": {"admin", "direct"},
        "password_source": {"admin_password", "direct"},
    },
)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Authentication")
@allure.story("Login data-driven tests")
@allure.title("Login case: {case[case_id]} - {case[desc]}")
@pytest.mark.auth
@pytest.mark.parametrize("case", LOGIN_CASES, ids=build_case_id)
def test_login_with_dataset(api_client: ApiClient, admin_email: str, admin_password: str, case: dict):
    username = admin_email if case["username_source"] == "admin" else case["username"]
    password = admin_password if case["password_source"] == "admin_password" else case["password"]

    with allure.step("Send login request"):
        response = api_client.login(username=username, password=password)

    with allure.step("Assert login response"):
        assert_status(response, case["expected_status"])
        if response.status_code == 200:
            assert_token_response(response)
        elif response.status_code == 422:
            assert_validation_error(response)
        else:
            assert_error_detail(response, case["expected_status"], expected_detail=case.get("expected_detail"))
