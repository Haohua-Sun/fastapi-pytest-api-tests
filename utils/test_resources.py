from __future__ import annotations

from dataclasses import dataclass, field

from utils.api_client import ApiClient
from utils.assertions import assert_message_response, assert_token_response
from utils.case_resolvers import random_email, random_password


@dataclass(frozen=True)
class TestUser:
    __test__ = False

    email: str
    password: str
    token: str
    user_id: str


@dataclass
class TestResourceRegistry:
    __test__ = False

    api_client: ApiClient
    admin_token: str
    item_ids: list[str] = field(default_factory=list)
    user_ids: list[str] = field(default_factory=list)

    def register_item(self, item_id: str) -> str:
        self.item_ids.append(item_id)
        return item_id

    def register_user(self, user_id: str) -> str:
        self.user_ids.append(user_id)
        return user_id

    def discard_item(self, item_id: str) -> None:
        if item_id in self.item_ids:
            self.item_ids.remove(item_id)

    def discard_user(self, user_id: str) -> None:
        if user_id in self.user_ids:
            self.user_ids.remove(user_id)

    def cleanup(self) -> None:
        for item_id in reversed(self.item_ids):
            delete_test_item(self.api_client, self.admin_token, item_id)
        for user_id in reversed(self.user_ids):
            delete_test_user(self.api_client, self.admin_token, user_id)


def create_test_user(api_client: ApiClient, prefix: str, full_name: str) -> TestUser:
    email = random_email(prefix)
    password = random_password()

    signup_response = api_client.signup(email=email, password=password, full_name=full_name)
    assert signup_response.status_code == 200, signup_response.text
    user_body = signup_response.json()

    login_response = api_client.login(email, password)
    token = assert_token_response(login_response)

    return TestUser(email=email, password=password, token=token, user_id=user_body["id"])


def delete_test_user(api_client: ApiClient, admin_token: str, user_id: str) -> None:
    response = api_client.delete_user(admin_token, user_id)
    if response.status_code == 404:
        return
    assert_message_response(response)


def delete_test_item(api_client: ApiClient, admin_token: str, item_id: str) -> None:
    response = api_client.delete_item(admin_token, item_id)
    if response.status_code == 404:
        return
    assert_message_response(response)
