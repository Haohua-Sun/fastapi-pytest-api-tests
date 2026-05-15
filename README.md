# FastAPI Pytest API Test Suite

English | [简体中文](README.zh-CN.md)

[![API automation tests](https://github.com/Haohua-Sun/fastapi-pytest-api-tests/actions/workflows/api-tests.yml/badge.svg)](https://github.com/Haohua-Sun/fastapi-pytest-api-tests/actions/workflows/api-tests.yml)

An API automation test suite for [`full-stack-fastapi-template`](https://github.com/Haohua-Sun/full-stack-fastapi-template), built with `pytest`, `requests`, JSON Schema validation, PostgreSQL database assertions, Allure reporting, GitHub Actions, and Jenkins.

The suite validates the FastAPI backend from an external client perspective. It covers authentication, token validation, user workflows, administrator operations, Item CRUD, permission isolation, response contract validation, multi-step business flows, and persistence checks.

## Test Results

The current suite collects `58` pytest cases and covers `17/23` OpenAPI operations.

- GitHub Actions runs the suite on push, pull request, and manual dispatch.
- The application under test is started in CI with Docker Compose.
- Allure raw results and generated HTML reports are uploaded as CI artifacts.
- Jenkins Pipeline support is included through [Jenkinsfile](Jenkinsfile), with JUnit and Allure publication.
- One known API defect is tracked with `xfail`: `GET /api/v1/items/` returns `500` for negative `skip`, while a validation error is expected.

See [OPENAPI_COVERAGE.md](OPENAPI_COVERAGE.md) for the coverage matrix, database assertion scope, known defect tracking, and planned extensions.

## Reports

### Allure Report

![Allure report overview](assets/allure-overview.png)

### Jenkins Allure Report

![Jenkins Allure report](assets/jenkins-allure-report.png)

## Test Scope

- `smoke`: service availability
- `auth`: login, token, and authorization
- `users`: signup, profile, and password workflows
- `admin`: administrator user management
- `items`: Item resource operations
- `flow`: multi-step business workflows
- `schema`: response contract validation
- `db`: PostgreSQL persistence assertions

## Tech Stack

- `pytest`: test organization, fixtures, markers, parametrization
- `requests`: HTTP API calls
- `jsonschema`: response contract validation
- `SQLAlchemy` + `psycopg`: PostgreSQL persistence assertions
- `allure-pytest`: Allure raw result generation
- Allure CLI: HTML report generation in CI and local runs
- `python-dotenv`: local environment loading
- `ruff`: static checks
- Docker Compose: application and database runtime in CI
- GitHub Actions + Jenkins: CI execution and reporting

## Continuous Integration

GitHub Actions is enabled in [.github/workflows/api-tests.yml](.github/workflows/api-tests.yml).

On push, pull request, or manual dispatch, CI:

1. Checks out this API test suite.
2. Checks out `Haohua-Sun/full-stack-fastapi-template`.
3. Creates a CI-only `.env` file for the FastAPI application.
4. Starts the FastAPI backend and PostgreSQL with Docker Compose.
5. Runs `ruff` and the full `pytest` API test suite.
6. Writes Allure environment metadata for the report overview.
7. Generates an Allure HTML report from `allure-results`.
8. Uploads `allure-results` and `allure-report` as workflow artifacts.
9. Prints Docker logs on failure and cleans up the Compose stack.

The application repository can also run this external suite through its own API regression workflow, so both test-suite changes and application changes can trigger API validation.

## Jenkins Pipeline

This repository includes a [Jenkinsfile](Jenkinsfile) for Jenkins Pipeline as Code.

Jenkins requirements:

- Run builds on an agent labeled `api-tests`.
- Keep the built-in node executor count at `0`.
- Install the Allure Jenkins plugin to publish `allure-results` directly on the build page.
- Configure GitHub webhooks for push-triggered builds when Jenkins is reachable from GitHub. SCM polling is also configured for environments without webhook access.

The Jenkins pipeline checks out this test suite, clones `Haohua-Sun/full-stack-fastapi-template`, creates CI environment files, starts the FastAPI backend and PostgreSQL with Docker Compose, runs `ruff` and `pytest`, publishes JUnit results, generates an Allure HTML report, archives report artifacts, and cleans up the Compose stack.

Webhook trigger support is preconfigured with `githubPush()`. For a reachable Jenkins instance, add this GitHub repository webhook:

```text
Payload URL: http(s)://<jenkins-host>/github-webhook/
Content type: application/json
Events: Just the push event
```

## Implementation Notes

- `ApiClient` centralizes request routing, auth headers, timeouts, response handling, and Allure attachments.
- Session-level fixtures load environment settings, verify service readiness, and manage the administrator token.
- Function-level fixtures create temporary users/items and clean up test data through a resource registry.
- JSON files maintain data-driven login and Item test cases.
- JSON Schema assertions validate token, user, Item, list, message, and validation-error responses.
- Database assertions verify create, update, and delete persistence behavior.
- Allure attachments mask sensitive values such as passwords, tokens, and `Authorization` headers.
- Allure environment metadata records project, framework, HTTP client, database, ORM, runtime, Python version, and CI provider.

## Project Structure

```text
.
├── assets/
│   ├── allure-overview.png
│   └── jenkins-allure-report.png
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
│   ├── allure_environment.py
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

Generate Allure results and HTML report:

```bash
python -m pytest -v
allure generate allure-results -o allure-report --clean
allure open allure-report
```

Allure CLI is required only for generating or serving the HTML report locally. CI publishes `allure-results` and `allure-report` as build artifacts.
