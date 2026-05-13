import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import (
    assert_error_detail,
    assert_json_object,
    assert_message_response,
    assert_status,
    assert_user_public,
    assert_validation_error,
)
from utils.case_resolvers import random_email, random_password
from utils.test_resources import TestResourceRegistry, TestUser


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Admin users")
@allure.story("Admin user management flow")
@pytest.mark.admin
@pytest.mark.users
@pytest.mark.flow
def test_admin_user_management_flow(
    api_client: ApiClient,
    admin_token: str,
    resource_registry: TestResourceRegistry,
):
    email = random_email("admin_created")
    password = random_password()
    updated_email = random_email("admin_updated")
    updated_name = "Updated Admin Managed User"

    create_response = api_client.create_user(
        admin_token,
        email=email,
        password=password,
        full_name="Admin Managed User",
        is_active=True,
        is_superuser=False,
    )
    assert_status(create_response, 200)
    created = assert_json_object(create_response)
    resource_registry.register_user(created["id"])
    assert_user_public(created, expected_email=email)
    assert created["is_active"] is True
    assert created["is_superuser"] is False

    read_response = api_client.read_user(admin_token, created["id"])
    assert_status(read_response, 200)
    read_user = assert_json_object(read_response)
    assert_user_public(read_user, expected_email=email)

    update_response = api_client.update_user(
        admin_token,
        created["id"],
        email=updated_email,
        full_name=updated_name,
        is_active=False,
    )
    assert_status(update_response, 200)
    updated = assert_json_object(update_response)
    assert_user_public(updated, expected_email=updated_email)
    assert updated["full_name"] == updated_name
    assert updated["is_active"] is False

    delete_response = api_client.delete_user(admin_token, created["id"])
    assert_message_response(delete_response)
    resource_registry.discard_user(created["id"])

    read_deleted_response = api_client.read_user(admin_token, created["id"])
    assert_error_detail(read_deleted_response, 404)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Admin users")
@allure.story("Admin user validation")
@pytest.mark.admin
@pytest.mark.users
@pytest.mark.parametrize(
    "email, password",
    [
        ("bad_email", "ValidPass123!"),
        (None, "ValidPass123!"),
        (random_email("short_password"), "123"),
    ],
    ids=["bad email", "missing email", "short password"],
)
def test_admin_create_user_validation(api_client: ApiClient, admin_token: str, email: str | None, password: str | None):
    response = api_client.create_user(admin_token, email=email, password=password, full_name="Invalid Admin User")

    assert_validation_error(response)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Admin users")
@allure.story("Non-admin cannot manage users")
@pytest.mark.admin
@pytest.mark.auth
@pytest.mark.users
def test_non_admin_cannot_manage_users(api_client: ApiClient, test_user: TestUser):
    expected_detail = "The user doesn't have enough privileges"

    list_response = api_client.read_users(test_user.token, skip=0, limit=10)
    assert_error_detail(list_response, 403, expected_detail=expected_detail)

    create_response = api_client.create_user(
        test_user.token,
        email=random_email("blocked_admin_create"),
        password=random_password(),
        full_name="Blocked Admin Create",
    )
    assert_error_detail(create_response, 403, expected_detail=expected_detail)

    update_response = api_client.update_user(test_user.token, test_user.user_id, full_name="Blocked Update")
    assert_error_detail(update_response, 403, expected_detail=expected_detail)

    delete_response = api_client.delete_user(test_user.token, test_user.user_id)
    assert_error_detail(delete_response, 403, expected_detail=expected_detail)
