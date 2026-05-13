from __future__ import annotations

from collections.abc import Iterator

import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import assert_status, assert_token_response
from utils.config import TestSettings, load_settings
from utils.db_client import DatabaseClient
from utils.test_resources import TestResourceRegistry, TestUser, create_test_user


def pytest_runtest_setup(item: pytest.Item) -> None:
    if item.get_closest_marker("smoke"):
        allure.dynamic.severity(allure.severity_level.BLOCKER)
    elif item.get_closest_marker("flow"):
        allure.dynamic.severity(allure.severity_level.CRITICAL)
    elif item.get_closest_marker("auth") or item.get_closest_marker("admin"):
        allure.dynamic.severity(allure.severity_level.NORMAL)
    elif item.get_closest_marker("db"):
        allure.dynamic.severity(allure.severity_level.MINOR)


@pytest.fixture(scope="session")
def settings() -> TestSettings:
    return load_settings()


@pytest.fixture(scope="session")
def base_url(settings: TestSettings) -> str:
    return settings.base_url


@pytest.fixture(scope="session")
def admin_email(settings: TestSettings) -> str:
    return settings.admin_email


@pytest.fixture(scope="session")
def admin_password(settings: TestSettings) -> str:
    return settings.admin_password


@pytest.fixture(scope="session")
def api_client(settings: TestSettings) -> Iterator[ApiClient]:
    client = ApiClient(base_url=settings.base_url, timeout=settings.request_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session", autouse=True)
def service_ready(api_client: ApiClient) -> None:
    try:
        response = api_client.health_check()
    except AssertionError as exc:
        pytest.exit(str(exc), returncode=2)

    if response.status_code != 200:
        pytest.exit(f"API service is not ready: expected health check 200, got {response.status_code}", returncode=2)

    try:
        is_healthy = response.json() is True
    except ValueError:
        is_healthy = False

    if not is_healthy:
        pytest.exit(f"API service is not healthy. Response body: {response.text}", returncode=2)


@pytest.fixture(scope="session")
def admin_token(api_client: ApiClient, admin_email: str, admin_password: str) -> str:
    response = api_client.login(admin_email, admin_password)
    return assert_token_response(response)


@pytest.fixture(scope="session")
def db_client(settings: TestSettings) -> DatabaseClient:
    return DatabaseClient(settings.database_url)


@pytest.fixture()
def resource_registry(api_client: ApiClient, admin_token: str) -> Iterator[TestResourceRegistry]:
    registry = TestResourceRegistry(api_client=api_client, admin_token=admin_token)
    yield registry
    registry.cleanup()


@pytest.fixture()
def test_user(api_client: ApiClient, resource_registry: TestResourceRegistry) -> TestUser:
    user = create_test_user(api_client, prefix="user", full_name="Pytest User")
    resource_registry.register_user(user.user_id)
    return user


@pytest.fixture()
def other_test_user(api_client: ApiClient, resource_registry: TestResourceRegistry) -> TestUser:
    user = create_test_user(api_client, prefix="other", full_name="Other Pytest User")
    resource_registry.register_user(user.user_id)
    return user


@pytest.fixture()
def created_item(api_client: ApiClient, admin_token: str, resource_registry: TestResourceRegistry):
    response = api_client.create_item(admin_token, title="Fixture Item", description="created in fixture")
    assert_status(response, 200)
    item = response.json()
    resource_registry.register_item(item["id"])
    return item
