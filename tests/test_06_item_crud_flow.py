import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import (
    assert_error_detail,
    assert_item_public,
    assert_json_object,
    assert_message_response,
    assert_status,
)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Item CRUD business flow")
@pytest.mark.flow
@pytest.mark.items
def test_item_crud_flow(api_client: ApiClient, admin_token: str):
    create_title = "Pytest Flow Item"
    create_description = "Created in CRUD flow"
    update_title = "Pytest Flow Item Updated"
    update_description = "Updated in CRUD flow"

    item_id: str | None = None

    try:
        with allure.step("Create item"):
            create_response = api_client.create_item(admin_token, title=create_title, description=create_description)
            assert_status(create_response, 200)
            created = assert_json_object(create_response)
            assert_item_public(created, expected_title=create_title, expected_description=create_description)
            item_id = created["id"]
            assert isinstance(item_id, str)

        with allure.step("Read created item"):
            read_response = api_client.read_item(admin_token, item_id)
            assert_status(read_response, 200)
            read_item = assert_json_object(read_response)
            assert read_item["id"] == item_id
            assert_item_public(read_item, expected_title=create_title, expected_description=create_description)

        with allure.step("Update item"):
            update_response = api_client.update_item(
                admin_token, item_id=item_id, title=update_title, description=update_description
            )
            assert_status(update_response, 200)
            updated = assert_json_object(update_response)
            assert updated["id"] == item_id
            assert_item_public(updated, expected_title=update_title, expected_description=update_description)

        with allure.step("Read updated item"):
            read_updated_response = api_client.read_item(admin_token, item_id)
            assert_status(read_updated_response, 200)
            read_updated = assert_json_object(read_updated_response)
            assert read_updated["id"] == item_id
            assert_item_public(read_updated, expected_title=update_title, expected_description=update_description)

        with allure.step("Delete item"):
            delete_response = api_client.delete_item(admin_token, item_id)
            assert_message_response(delete_response)
            item_id = None

        with allure.step("Confirm deleted item cannot be read"):
            read_deleted_response = api_client.read_item(admin_token, created["id"])
            assert_error_detail(read_deleted_response, 404, expected_detail="Item not found")
    finally:
        # If the flow fails before the delete step, avoid leaving test data behind.
        if item_id:
            api_client.delete_item(admin_token, item_id)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Authorization")
@allure.story("Authorization negative flow")
@pytest.mark.flow
@pytest.mark.auth
def test_item_create_without_token_then_invalid_token_read_me(api_client: ApiClient):
    no_token_response = api_client.create_item(None, title="No Token Item", description="should fail")
    assert_error_detail(no_token_response, 401, expected_detail="Not authenticated")

    invalid_token_response = api_client.read_user_me("invalid_token")
    assert_error_detail(invalid_token_response, 403, expected_detail="Could not validate credentials")
