from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOTENV_PATH = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class TestSettings:
    base_url: str = "http://localhost:8000"
    admin_email: str = ""
    admin_password: str = ""
    request_timeout: float = 10.0
    database_url: str = ""


def load_settings() -> TestSettings:
    """Load test configuration from environment variables."""
    load_dotenv(DOTENV_PATH, override=False)

    base_url = os.getenv("BASE_URL", TestSettings.base_url).strip().rstrip("/")
    timeout_raw = os.getenv("API_TEST_TIMEOUT", str(TestSettings.request_timeout)).strip()
    admin_email = os.getenv("ADMIN_EMAIL", "").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    database_url = os.getenv("API_TEST_DATABASE_URL", "").strip()

    try:
        timeout = float(timeout_raw)
    except ValueError as exc:
        raise ValueError(f"API_TEST_TIMEOUT should be a number, got: {timeout_raw}") from exc

    if timeout <= 0:
        raise ValueError("API_TEST_TIMEOUT should be greater than 0")

    if not base_url.startswith(("http://", "https://")):
        raise ValueError(f"BASE_URL should start with http:// or https://, got: {base_url}")

    missing_vars = [
        name
        for name, value in {
            "ADMIN_EMAIL": admin_email,
            "ADMIN_PASSWORD": admin_password,
            "API_TEST_DATABASE_URL": database_url,
        }.items()
        if not value
    ]
    if missing_vars:
        missing = ", ".join(missing_vars)
        raise ValueError(
            f"Missing required environment variables: {missing}. Copy .env.example to .env and fill them in."
        )

    return TestSettings(
        base_url=base_url,
        admin_email=admin_email,
        admin_password=admin_password,
        request_timeout=timeout,
        database_url=database_url,
    )
