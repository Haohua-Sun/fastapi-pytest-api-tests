import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import assert_status


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Health check")
@allure.story("Service availability")
@pytest.mark.smoke
def test_health_check(api_client: ApiClient):
    with allure.step("Call health check API"):
        response = api_client.health_check()

    with allure.step("Assert service is healthy"):
        assert_status(response, 200)
        assert response.json() is True
