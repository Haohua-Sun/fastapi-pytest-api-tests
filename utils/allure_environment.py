from __future__ import annotations

import os
import platform
from pathlib import Path

import pytest


def _detect_ci() -> str:
    if os.getenv("GITHUB_ACTIONS") == "true":
        return "GitHub Actions"
    if os.getenv("JENKINS_URL") or os.getenv("JENKINS_HOME") or os.getenv("BUILD_TAG"):
        return "Jenkins"
    if os.getenv("CI"):
        return "CI"
    return "Local"


def _escape_property(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n")


def write_allure_environment(pytestconfig: pytest.Config) -> None:
    alluredir = pytestconfig.getoption("--alluredir", default=None)
    if not alluredir:
        return

    environment = {
        "Project": "full-stack-fastapi-template",
        "Test_Project": "fastapi-pytest-api-tests",
        "Framework": "pytest",
        "HTTP_Client": "requests",
        "Database": "PostgreSQL",
        "ORM": "SQLAlchemy",
        "Report": "Allure",
        "CI": _detect_ci(),
        "Runtime": "Docker Compose",
        "Python": platform.python_version(),
    }

    alluredir_path = Path(str(alluredir))
    alluredir_path.mkdir(parents=True, exist_ok=True)
    content = "\n".join(f"{key}={_escape_property(value)}" for key, value in environment.items())
    alluredir_path.joinpath("environment.properties").write_text(f"{content}\n", encoding="utf-8")
