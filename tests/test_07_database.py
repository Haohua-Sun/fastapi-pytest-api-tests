from __future__ import annotations

import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import assert_item_public, assert_json_object, assert_message_response, assert_status
from utils.db_client import DatabaseClient


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Database assertions")
@pytest.mark.db
@pytest.mark.items
def test_create_update_delete_item_persisted_in_database(
    api_client: ApiClient,
    admin_token: str,
    db_client: DatabaseClient,
):
    item_id: str | None = None

    try:
        with allure.step("Create item by API"):
            create_response = api_client.create_item(
                admin_token,
                title="DB Assert Item",
                description="created for database assertion",
            )
            assert_status(create_response, 200)
            created = assert_json_object(create_response)
            assert_item_public(
                created, expected_title="DB Assert Item", expected_description="created for database assertion"
            )
            item_id = created["id"]
            assert isinstance(item_id, str)

        with allure.step("Assert created item exists in database"):
            db_item = db_client.fetch_item_by_id(item_id)
            assert db_item is not None
            assert str(db_item["id"]) == item_id
            assert db_item["title"] == "DB Assert Item"
            assert db_item["description"] == "created for database assertion"
            assert str(db_item["owner_id"]) == created["owner_id"]

        with allure.step("Update item by API"):
            update_response = api_client.update_item(
                admin_token,
                item_id=item_id,
                title="DB Assert Item Updated",
                description="updated for database assertion",
            )
            assert_status(update_response, 200)

        with allure.step("Assert updated item is persisted in database"):
            db_item = db_client.fetch_item_by_id(item_id)
            assert db_item is not None
            assert db_item["title"] == "DB Assert Item Updated"
            assert db_item["description"] == "updated for database assertion"

        with allure.step("Delete item by API"):
            delete_response = api_client.delete_item(admin_token, item_id)
            assert_message_response(delete_response)

        with allure.step("Assert deleted item no longer exists in database"):
            assert db_client.fetch_item_by_id(item_id) is None
            item_id = None
    finally:
        # API cleanup is still attempted even when the database assertion fails.
        if item_id:
            api_client.delete_item(admin_token, item_id)
