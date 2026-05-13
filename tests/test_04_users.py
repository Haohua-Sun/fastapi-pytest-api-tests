import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import (
    assert_error_detail,
    assert_json_object,
    assert_message_response,
    assert_status,
    assert_token_response,
    assert_user_public,
    assert_validation_error,
)
from utils.case_resolvers import random_email, random_password
from utils.test_resources import TestResourceRegistry, TestUser


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Users")
@allure.story("Signup success")
@pytest.mark.users
def test_signup_success(api_client: ApiClient, admin_token: str):
    email = random_email("signup")
    password = random_password()
    user_id: str | None = None

    try:
        with allure.step("Register a new user"):
            response = api_client.signup(email=email, password=password, full_name="Signup User")

        assert_status(response, 200)
        body = assert_json_object(response)
        user_id = body["id"]
        assert_user_public(body, expected_email=email)
    finally:
        if user_id:
            delete_response = api_client.delete_user(admin_token, user_id)
            assert_message_response(delete_response)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Users")
@allure.story("Signup validation")
@pytest.mark.users
@pytest.mark.parametrize(
    "email, password, expected_status",
    [
        ("bad_email", "ValidPass123!", 422),
        ("short_password@example.com", "123", 422),
        (None, "ValidPass123!", 422),
        ("missing_password@example.com", None, 422),
    ],
    ids=["bad email", "short password", "missing email", "missing password"],
)
def test_signup_validation(api_client: ApiClient, email: str | None, password: str | None, expected_status: int):
    response = api_client.signup(email=email, password=password, full_name="Invalid Signup")

    assert_status(response, expected_status)
    assert_validation_error(response)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Users")
@allure.story("Signup duplicate email")
@pytest.mark.users
def test_signup_duplicate_email_rejected(api_client: ApiClient, resource_registry: TestResourceRegistry):
    email = random_email("duplicate")
    password = random_password()

    first_response = api_client.signup(email=email, password=password, full_name="Duplicate User")
    assert_status(first_response, 200)
    first_body = assert_json_object(first_response)
    resource_registry.register_user(first_body["id"])

    second_response = api_client.signup(email=email, password=random_password(), full_name="Duplicate User Again")
    assert_error_detail(
        second_response,
        400,
        expected_detail="The user with this email already exists in the system",
    )


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Users")
@allure.story("Read current user")
@pytest.mark.users
def test_read_user_me_success(api_client: ApiClient, test_user: TestUser):
    response = api_client.read_user_me(test_user.token)

    assert_status(response, 200)
    body = assert_json_object(response)
    assert_user_public(body, expected_email=test_user.email)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Users")
@allure.story("Update current user")
@pytest.mark.users
def test_update_user_me_with_disposable_user(api_client: ApiClient, test_user: TestUser):
    new_name = "Updated By Pytest"
    new_email = random_email("updated")

    response = api_client.update_user_me(test_user.token, full_name=new_name, email=new_email)

    assert_status(response, 200)
    body = assert_json_object(response)
    assert_user_public(body, expected_email=new_email)
    assert body["full_name"] == new_name


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Users")
@allure.story("Update current user validation")
@pytest.mark.users
def test_update_user_me_invalid_email(api_client: ApiClient, test_user: TestUser):
    response = api_client.update_user_me(test_user.token, email="bad_email")

    assert_validation_error(response)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Users")
@allure.story("Password change flow")
@pytest.mark.users
def test_update_password_me_flow(api_client: ApiClient, test_user: TestUser):
    new_password = random_password()

    with allure.step("Change password with current password"):
        change_response = api_client.update_password_me(test_user.token, test_user.password, new_password)
        assert_message_response(change_response)

    with allure.step("Old password should no longer valid"):
        old_login_response = api_client.login(test_user.email, test_user.password)
        assert_error_detail(old_login_response, 400, expected_detail="Incorrect email or password")

    with allure.step("New password should login successfully"):
        new_login_response = api_client.login(test_user.email, new_password)
        assert_token_response(new_login_response)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Users")
@allure.story("Password change validation")
@pytest.mark.users
def test_update_password_wrong_old_password(api_client: ApiClient, test_user: TestUser):
    response = api_client.update_password_me(test_user.token, "WrongOldPass123!", random_password())

    assert_error_detail(response, 400)
