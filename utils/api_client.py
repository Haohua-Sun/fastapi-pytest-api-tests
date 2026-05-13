from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import requests

from utils.allure_helpers import attach_request, attach_response


def compact_json(**values: Any) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


@dataclass
class ApiClient:
    base_url: str
    timeout: float = 10.0
    session: requests.Session = field(init=False)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        normalized_path = path if path.startswith("/") else f"/{path}"
        request_method = method.upper()
        url = f"{self.base_url}{normalized_path}"
        kwargs.setdefault("timeout", self.timeout)
        attach_request(request_method, url, kwargs, name=f"{request_method} {normalized_path} request")
        try:
            response = self.session.request(method=request_method, url=url, **kwargs)
        except requests.RequestException as exc:
            raise AssertionError(
                f"HTTP request failed: {request_method} {url}. "
                f"Check BASE_URL={self.base_url!r}, whether the API service is running, "
                f"and whether API_TEST_TIMEOUT={kwargs['timeout']!r} is suitable. "
                f"Original error: {exc}"
            ) from exc
        attach_response(response, name=f"{request_method} {normalized_path} response [{response.status_code}]")
        return response

    def close(self) -> None:
        self.session.close()

    @staticmethod
    def bearer_headers(token: str | None) -> dict[str, str]:
        return {} if token is None else {"Authorization": f"Bearer {token}"}

    def health_check(self) -> requests.Response:
        return self.request("GET", "/api/v1/utils/health-check/")

    def login(self, username: str, password: str) -> requests.Response:
        return self.request(
            "POST",
            "/api/v1/login/access-token",
            data={
                "username": username,
                "password": password,
                "grant_type": "password",
                "scope": "",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    def test_token(self, token: str | None) -> requests.Response:
        return self.request("POST", "/api/v1/login/test-token", headers=self.bearer_headers(token))

    def signup(self, email: str | None, password: str | None, full_name: str | None = None) -> requests.Response:
        return self.request(
            "POST", "/api/v1/users/signup", json=compact_json(email=email, password=password, full_name=full_name)
        )

    def read_user_me(self, token: str | None) -> requests.Response:
        return self.request("GET", "/api/v1/users/me", headers=self.bearer_headers(token))

    def update_user_me(
        self, token: str | None, full_name: str | None = None, email: str | None = None
    ) -> requests.Response:
        return self.request(
            "PATCH",
            "/api/v1/users/me",
            json=compact_json(full_name=full_name, email=email),
            headers=self.bearer_headers(token),
        )

    def update_password_me(
        self, token: str | None, current_password: str | None, new_password: str | None
    ) -> requests.Response:
        return self.request(
            "PATCH",
            "/api/v1/users/me/password",
            json=compact_json(current_password=current_password, new_password=new_password),
            headers=self.bearer_headers(token),
        )

    def read_users(self, token: str | None, skip: int = 0, limit: int = 100) -> requests.Response:
        return self.request(
            "GET", "/api/v1/users/", params={"skip": skip, "limit": limit}, headers=self.bearer_headers(token)
        )

    def create_user(
        self,
        token: str | None,
        email: str | None,
        password: str | None,
        full_name: str | None = None,
        is_active: bool | None = None,
        is_superuser: bool | None = None,
    ) -> requests.Response:
        return self.request(
            "POST",
            "/api/v1/users/",
            json=compact_json(
                email=email,
                password=password,
                full_name=full_name,
                is_active=is_active,
                is_superuser=is_superuser,
            ),
            headers=self.bearer_headers(token),
        )

    def read_user(self, token: str | None, user_id: str) -> requests.Response:
        return self.request("GET", f"/api/v1/users/{user_id}", headers=self.bearer_headers(token))

    def update_user(
        self,
        token: str | None,
        user_id: str,
        email: str | None = None,
        password: str | None = None,
        full_name: str | None = None,
        is_active: bool | None = None,
        is_superuser: bool | None = None,
    ) -> requests.Response:
        return self.request(
            "PATCH",
            f"/api/v1/users/{user_id}",
            json=compact_json(
                email=email,
                password=password,
                full_name=full_name,
                is_active=is_active,
                is_superuser=is_superuser,
            ),
            headers=self.bearer_headers(token),
        )

    def delete_user(self, token: str | None, user_id: str) -> requests.Response:
        return self.request("DELETE", f"/api/v1/users/{user_id}", headers=self.bearer_headers(token))

    def create_item(self, token: str | None, title: str | None, description: str | None = None) -> requests.Response:
        return self.request(
            "POST",
            "/api/v1/items/",
            json=compact_json(title=title, description=description),
            headers=self.bearer_headers(token),
        )

    def read_items(self, token: str | None, skip: int = 0, limit: int = 100) -> requests.Response:
        return self.request(
            "GET", "/api/v1/items/", params={"skip": skip, "limit": limit}, headers=self.bearer_headers(token)
        )

    def read_item(self, token: str | None, item_id: str) -> requests.Response:
        return self.request("GET", f"/api/v1/items/{item_id}", headers=self.bearer_headers(token))

    def update_item(
        self, token: str | None, item_id: str, title: str | None = None, description: str | None = None
    ) -> requests.Response:
        return self.request(
            "PUT",
            f"/api/v1/items/{item_id}",
            json=compact_json(title=title, description=description),
            headers=self.bearer_headers(token),
        )

    def delete_item(self, token: str | None, item_id: str) -> requests.Response:
        return self.request("DELETE", f"/api/v1/items/{item_id}", headers=self.bearer_headers(token))
