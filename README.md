# FastAPI Pytest API Test Suite

English | [简体中文](README.zh-CN.md)

[![API automation tests](https://github.com/Haohua-Sun/fastapi-pytest-api-tests/actions/workflows/api-tests.yml/badge.svg)](https://github.com/Haohua-Sun/fastapi-pytest-api-tests/actions/workflows/api-tests.yml)

An API automation test suite for [`full-stack-fastapi-template`](https://github.com/Haohua-Sun/full-stack-fastapi-template), built with `pytest`, `requests`, JSON Schema validation, SQLAlchemy database assertions, Allure result output, and GitHub Actions CI.

The suite covers authentication, token validation, user workflows, administrator user management, Item CRUD, permission isolation, response contract validation, business flows, and persistence checks against PostgreSQL.

## Highlights

- Encapsulated `ApiClient` for request routing, auth headers, timeouts, response handling, and Allure attachments.
- Pytest fixtures for environment loading, admin token management, temporary users/items, and test data cleanup.
- Data-driven login and Item test cases maintained in JSON files.
- JSON Schema assertions based on the OpenAPI contract in `openapi.json`.
- Database assertions for create, update, and delete persistence behavior.
- Sensitive value masking for Allure request/response attachments.
- GitHub Actions CI that starts the FastAPI application with Docker Compose, runs the test suite, and uploads Allure artifacts.

## Tech Stack

- `pytest`: test organization, fixtures, markers, parametrization
- `requests`: HTTP API calls
- `jsonschema`: response contract validation
- `SQLAlchemy` + `psycopg`: PostgreSQL persistence assertions
- `allure-pytest`: Allure raw result generation
- Allure CLI: HTML report generation in CI and local runs
- `python-dotenv`: local environment loading
- `ruff`: static checks
- GitHub Actions + Docker Compose: CI execution environment

## Project Structure

```text
.
├── data/
│   ├── item_create_cases.json
│   ├── item_update_cases.json
│   └── login_cases.json
├── tests/
│   ├── conftest.py
│   ├── test_01_health_check.py
│   ├── test_02_login.py
│   ├── test_03_auth_token.py
│   ├── test_04_users.py
│   ├── test_05_items_api.py
│   ├── test_06_item_crud_flow.py
│   ├── test_07_database.py
│   └── test_08_admin.py
├── utils/
│   ├── api_client.py
│   ├── assertions.py
│   ├── config.py
│   ├── db_client.py
│   └── schemas.py
├── .github/workflows/api-tests.yml
├── .env.example
├── Jenkinsfile
├── OPENAPI_COVERAGE.md
├── openapi.json
├── pytest.ini
├── pyproject.toml
└── requirements.txt
```

## Configuration

Create a local `.env` file from `.env.example` when running the suite outside CI:

```env
BASE_URL=http://localhost:8000
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
API_TEST_TIMEOUT=10
API_TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/app
```

Required values:

- `BASE_URL`: target FastAPI service URL
- `ADMIN_EMAIL` / `ADMIN_PASSWORD`: administrator credentials used to obtain tokens
- `API_TEST_TIMEOUT`: request timeout in seconds
- `API_TEST_DATABASE_URL`: PostgreSQL connection string for persistence assertions

## Local Setup

```bash
git clone https://github.com/Haohua-Sun/fastapi-pytest-api-tests.git
cd fastapi-pytest-api-tests
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run checks and tests:

```bash
python -m ruff check tests utils
python -m pytest -v
```

Generate Allure raw results:

```bash
python -m pytest -v
```

The raw results are written to `allure-results/`. To view an HTML report locally, install Allure CLI separately and run:

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

When downloading the `allure-report` artifact from GitHub Actions, serve the extracted directory over HTTP before opening it:

```bash
cd allure-report
python3 -m http.server 5050
```

Then open `http://localhost:5050`. Opening `index.html` directly with `file://` can show a blank Allure page because the browser blocks local JSON loading.

## Test Markers

- `smoke`: service availability
- `auth`: login, token, and authorization
- `users`: signup, profile, and password workflows
- `admin`: administrator user management
- `items`: Item resource operations
- `flow`: multi-step business workflows
- `schema`: response contract validation
- `db`: database persistence assertions

## Coverage

The suite currently collects `58` tests and covers `17/23` OpenAPI operations. See [OPENAPI_COVERAGE.md](OPENAPI_COVERAGE.md) for the coverage matrix, database assertion scope, known defect tracking, and planned extensions.

One known defect is tracked with `xfail`: `GET /api/v1/items/` returns `500` for negative `skip`, while a validation error is expected.

## Continuous Integration

GitHub Actions is enabled in [.github/workflows/api-tests.yml](.github/workflows/api-tests.yml).

On push, pull request, or manual dispatch, CI:

1. Checks out this API test suite.
2. Checks out `Haohua-Sun/full-stack-fastapi-template`.
3. Creates a CI-only `.env` file for the FastAPI application.
4. Starts the FastAPI backend and PostgreSQL with Docker Compose.
5. Runs `ruff` and the full `pytest` API test suite.
6. Generates an Allure HTML report from `allure-results`.
7. Uploads both `allure-results` and `allure-report` as workflow artifacts.
8. Prints Docker logs on failure and cleans up the Compose stack.

## Jenkins Pipeline

This repository also includes a [Jenkinsfile](Jenkinsfile). A Jenkins Pipeline job can run it with `Pipeline script from SCM`.

Recommended Jenkins setup:

- Run builds on an agent labeled `api-tests`.
- Keep the built-in node executor count at `0` after the agent is connected.
- Install the Allure Jenkins plugin to publish `allure-results` directly on the build page, while still archiving `allure-results` and `allure-report` as a fallback.
- Use GitHub webhooks when Jenkins is reachable from GitHub; for a local Jenkins instance, the Jenkinsfile also enables SCM polling every 5 minutes.

The Jenkins pipeline checks out this test suite, clones `Haohua-Sun/full-stack-fastapi-template`, creates CI environment files, starts the FastAPI backend and PostgreSQL with Docker Compose, runs `ruff` and `pytest`, publishes JUnit results, generates an Allure HTML report, archives report artifacts, and cleans up the Compose stack.

The Jenkinsfile publishes JUnit results, publishes the Allure report through the Allure Jenkins plugin, and also archives `allure-results` and the generated `allure-report` directory as build artifacts.
