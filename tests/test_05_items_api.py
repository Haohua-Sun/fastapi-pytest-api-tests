import allure
import pytest
from utils.api_client import ApiClient
from utils.assertions import (
    assert_error_detail,
    assert_item_public,
    assert_json_object,
    assert_list_public,
    assert_status,
    assert_validation_error,
)
from utils.case_resolvers import build_case_id, resolve_auth_token, resolve_item_id, resolve_optional_text
from utils.data_loader import load_json_cases
from utils.test_resources import TestUser

CREATE_CASES = load_json_cases(
    "item_create_cases.json",
    required_keys={"case_id", "desc", "auth_type", "title", "description", "expected_status"},
    enum_fields={"auth_type": {"valid_token", "invalid_token", "missing_token"}},
)
UPDATE_CASES = load_json_cases(
    "item_update_cases.json",
    required_keys={"case_id", "desc", "auth_type", "id_source", "title", "description", "expected_status"},
    enum_fields={
        "auth_type": {"valid_token", "invalid_token", "missing_token"},
        "id_source": {"env_item_id", "not_exist", "invalid_uuid"},
    },
)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Read item list")
@pytest.mark.items
def test_read_items_success(api_client: ApiClient, admin_token: str):
    response = api_client.read_items(admin_token, skip=0, limit=10)

    assert_status(response, 200)
    body = assert_json_object(response)
    assert_list_public(body)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Read item list pagination boundaries")
@pytest.mark.items
@pytest.mark.parametrize(
    "skip, limit",
    [
        (0, 0),
        (0, 1),
    ],
    ids=["limit zero", "limit one"],
)
def test_read_items_pagination_boundaries(api_client: ApiClient, admin_token: str, skip: int, limit: int):
    response = api_client.read_items(admin_token, skip=skip, limit=limit)

    assert_status(response, 200)
    body = assert_json_object(response)
    assert_list_public(body)
    assert len(body["data"]) <= limit


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Read item list invalid pagination")
@pytest.mark.items
@pytest.mark.xfail(reason="Known API defect: negative skip currently returns 500 instead of validation error.")
def test_read_items_negative_skip_should_be_rejected(api_client: ApiClient, admin_token: str):
    response = api_client.read_items(admin_token, skip=-1, limit=10)

    assert_validation_error(response)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Create item data-driven tests")
@allure.title("Create item case: {case[case_id]} - {case[desc]}")
@pytest.mark.items
@pytest.mark.parametrize("case", CREATE_CASES, ids=build_case_id)
def test_create_item_dataset(api_client: ApiClient, admin_token: str, case: dict):
    token = resolve_auth_token(case["auth_type"], admin_token)
    title = resolve_optional_text(case["title"])
    description = resolve_optional_text(case["description"])
    created_item_id: str | None = None

    try:
        response = api_client.create_item(token, title=title, description=description)

        assert_status(response, case["expected_status"])
        if response.status_code == 200:
            body = assert_json_object(response)
            created_item_id = body.get("id")
            assert_item_public(body, expected_title=title, expected_description=description)

        elif response.status_code == 422:
            assert_validation_error(response)
        else:
            assert_error_detail(response, case["expected_status"], expected_detail=case.get("expected_detail"))
    finally:
        if created_item_id:
            api_client.delete_item(admin_token, created_item_id)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Update item data-driven tests")
@allure.title("Update item case: {case[case_id]} - {case[desc]}")
@pytest.mark.items
@pytest.mark.parametrize("case", UPDATE_CASES, ids=build_case_id)
def test_update_item_dataset(api_client: ApiClient, admin_token: str, created_item: dict, case: dict):
    token = resolve_auth_token(case["auth_type"], admin_token)
    item_id = resolve_item_id(case["id_source"], created_item_id=created_item["id"])
    title = resolve_optional_text(case["title"])
    description = resolve_optional_text(case["description"])

    response = api_client.update_item(token, item_id=item_id, title=title, description=description)

    assert_status(response, case["expected_status"])
    if response.status_code == 200:
        body = assert_json_object(response)
        assert_item_public(body, expected_title=title, expected_description=description)
    elif response.status_code == 422:
        assert_validation_error(response)
    else:
        assert_error_detail(response, case["expected_status"], expected_detail=case.get("expected_detail"))


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Read item invalid id")
@pytest.mark.items
@pytest.mark.parametrize(
    "item_id, expected_status, expected_detail",
    [
        ("bad_id", 422, None),
        ("00000000-0000-0000-0000-000000000001", 404, "Item not found"),
    ],
    ids=["invalid uuid", "not found"],
)
def test_read_item_invalid_id(
    api_client: ApiClient, admin_token: str, item_id: str, expected_status: int, expected_detail: str | None
):
    response = api_client.read_item(admin_token, item_id)

    if expected_status == 422:
        assert_validation_error(response)
    else:
        assert_error_detail(response, expected_status, expected_detail=expected_detail)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Delete item invalid id")
@pytest.mark.items
@pytest.mark.parametrize(
    "item_id, expected_status, expected_detail",
    [
        ("bad_id", 422, None),
        ("00000000-0000-0000-0000-000000000001", 404, "Item not found"),
    ],
    ids=["invalid uuid", "not found"],
)
def test_delete_item_invalid_id(
    api_client: ApiClient, admin_token: str, item_id: str, expected_status: int, expected_detail: str | None
):
    response = api_client.delete_item(admin_token, item_id)

    if expected_status == 422:
        assert_validation_error(response)
    else:
        assert_error_detail(response, expected_status, expected_detail=expected_detail)


@allure.epic("Full Stack FastAPI Template")
@allure.feature("Items")
@allure.story("Item ownership authorization")
@pytest.mark.items
@pytest.mark.auth
def test_user_cannot_access_other_user_item(
    api_client: ApiClient,
    test_user: TestUser,
    other_test_user: TestUser,
):
    owner_item_id: str | None = None

    try:
        with allure.step("Owner creates an item"):
            create_response = api_client.create_item(
                test_user.token,
                title="Owner Private Item",
                description="created for ownership authorization",
            )
            assert_status(create_response, 200)
            owner_item = assert_json_object(create_response)
            assert_item_public(
                owner_item,
                expected_title="Owner Private Item",
                expected_description="created for ownership authorization",
            )
            assert owner_item["owner_id"] == test_user.user_id
            owner_item_id = owner_item["id"]
            assert isinstance(owner_item_id, str)

        with allure.step("Another user cannot read the owner's item"):
            read_response = api_client.read_item(other_test_user.token, owner_item_id)
            assert_error_detail(read_response, 403)

        with allure.step("Another user cannot update the owner's item"):
            update_response = api_client.update_item(
                other_test_user.token,
                item_id=owner_item_id,
                title="Forbidden Update",
            )
            assert_error_detail(update_response, 403)

        with allure.step("Another user cannot delete the owner's item"):
            delete_response = api_client.delete_item(other_test_user.token, owner_item_id)
            assert_error_detail(delete_response, 403)

        with allure.step("Owner can still read the item after rejected operations"):
            owner_read_response = api_client.read_item(test_user.token, owner_item_id)
            assert_status(owner_read_response, 200)
            owner_read_item = assert_json_object(owner_read_response)
            assert owner_read_item["id"] == owner_item_id
    finally:
        if owner_item_id:
            api_client.delete_item(test_user.token, owner_item_id)
