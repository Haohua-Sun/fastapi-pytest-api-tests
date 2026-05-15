# FastAPI Pytest API 测试套件

[English](README.md) | 简体中文

[![API automation tests](https://github.com/Haohua-Sun/fastapi-pytest-api-tests/actions/workflows/api-tests.yml/badge.svg)](https://github.com/Haohua-Sun/fastapi-pytest-api-tests/actions/workflows/api-tests.yml)

这是一个面向 [`full-stack-fastapi-template`](https://github.com/Haohua-Sun/full-stack-fastapi-template) 的接口自动化测试套件，使用 `pytest`、`requests`、JSON Schema 校验、PostgreSQL 数据库断言、Allure 报告、GitHub Actions 和 Jenkins 构建。

测试套件从外部客户端视角验证 FastAPI 后端，覆盖登录认证、token 校验、用户流程、管理员操作、Item CRUD、权限隔离、响应契约校验、多步骤业务链路以及数据库持久化检查。

## 测试结果

当前测试套件可收集 `58` 条 pytest 用例，覆盖 `17/23` 个 OpenAPI 操作。

- GitHub Actions 会在 push、pull request 和手动触发时运行测试。
- CI 会通过 Docker Compose 启动被测应用。
- Allure 原始结果和生成后的 HTML 报告会作为 CI artifacts 上传。
- 仓库通过 [Jenkinsfile](Jenkinsfile) 提供 Jenkins Pipeline 支持，可发布 JUnit 和 Allure 报告。
- 当前保留 1 条 `xfail` 已知缺陷：`GET /api/v1/items/` 在传入负数 `skip` 时返回 `500`，预期应返回参数校验错误。

覆盖矩阵、数据库断言范围、已知缺陷跟踪和后续扩展计划见 [OPENAPI_COVERAGE.md](OPENAPI_COVERAGE.md)。

## 测试报告

### Allure Report

![Allure report overview](assets/allure-overview.png)

### Jenkins Allure Report

![Jenkins Allure report](assets/jenkins-allure-report.png)

## 测试范围

- `smoke`: 服务可用性
- `auth`: 登录、token 和鉴权
- `users`: 注册、用户资料和密码流程
- `admin`: 管理员用户管理
- `items`: Item 资源操作
- `flow`: 多步骤业务链路
- `schema`: 响应契约校验
- `db`: PostgreSQL 持久化断言

## 技术栈

- `pytest`: 测试组织、fixture、marker、参数化
- `requests`: HTTP API 请求
- `jsonschema`: 响应契约校验
- `SQLAlchemy` + `psycopg`: PostgreSQL 持久化断言
- `allure-pytest`: Allure 原始结果生成
- Allure CLI: CI 和本地运行中的 HTML 报告生成
- `python-dotenv`: 本地环境变量加载
- `ruff`: 静态检查
- Docker Compose: CI 中的应用和数据库运行环境
- GitHub Actions + Jenkins: CI 执行和测试报告发布

## 持续集成

GitHub Actions 已在 [.github/workflows/api-tests.yml](.github/workflows/api-tests.yml) 中启用。

每次 push、pull request 或手动触发时，CI 会：

1. 拉取本 API 测试仓库。
2. 拉取 `Haohua-Sun/full-stack-fastapi-template`。
3. 为 FastAPI 应用创建 CI 专用 `.env` 文件。
4. 使用 Docker Compose 启动 FastAPI 后端和 PostgreSQL。
5. 执行 `ruff` 和完整的 `pytest` API 测试套件。
6. 写入 Allure environment 元信息，用于报告 Overview 展示。
7. 基于 `allure-results` 生成 Allure HTML 报告。
8. 上传 `allure-results` 和 `allure-report` 两个 workflow artifacts。
9. 失败时打印 Docker 日志，并清理 Compose 环境。

被测应用仓库也可以通过自己的 API 回归 workflow 调用本测试套件，因此测试仓库变更和应用仓库变更都可以触发接口验证。

## Jenkins Pipeline

本仓库提供 [Jenkinsfile](Jenkinsfile)，用于 Jenkins Pipeline as Code。

Jenkins 配置要求：

- 使用带有 `api-tests` label 的 agent 执行构建。
- 将 built-in node 的 executor 数量设置为 `0`。
- 安装 Allure Jenkins 插件，在构建页面直接发布 `allure-results`。
- Jenkins 可被 GitHub 访问时，配置 GitHub webhook 触发 push 构建。Jenkinsfile 同时配置了 SCM 轮询，以支持无法使用 webhook 的环境。

Jenkins 流水线会拉取本测试仓库，克隆 `Haohua-Sun/full-stack-fastapi-template`，生成 CI 环境配置，使用 Docker Compose 启动 FastAPI 后端和 PostgreSQL，执行 `ruff` 和 `pytest`，发布 JUnit 结果，生成 Allure HTML 报告，归档报告 artifacts，并清理 Compose 环境。

Jenkinsfile 已通过 `githubPush()` 预留 webhook 触发。若 Jenkins 部署在可访问地址上，可在 GitHub 仓库中添加 webhook：

```text
Payload URL: http(s)://<jenkins-host>/github-webhook/
Content type: application/json
Events: Just the push event
```

## 实现说明

- `ApiClient` 统一封装请求路径、鉴权头、超时、响应处理和 Allure 附件。
- session 级 fixtures 负责加载环境配置、验证服务可用性和管理管理员 token。
- function 级 fixtures 负责创建临时用户/Item，并通过资源注册器清理测试数据。
- 使用 JSON 文件维护登录和 Item 相关的数据驱动用例。
- 使用 JSON Schema 校验 token、用户、Item、列表、消息和参数校验错误响应。
- 针对创建、更新、删除行为提供数据库持久化断言。
- 对 Allure 请求/响应附件中的 password、token、`Authorization` 等敏感字段进行脱敏。
- Allure environment 元信息记录项目、框架、HTTP client、数据库、ORM、运行环境、Python 版本和 CI 平台。

## 项目结构

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

## 配置

在 CI 外本地运行测试时，可基于 `.env.example` 创建本地 `.env` 文件：

```env
BASE_URL=http://localhost:8000
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
API_TEST_TIMEOUT=10
API_TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/app
```

必填配置：

- `BASE_URL`: 被测 FastAPI 服务地址
- `ADMIN_EMAIL` / `ADMIN_PASSWORD`: 用于获取 token 的管理员账号
- `API_TEST_TIMEOUT`: 请求超时时间，单位为秒
- `API_TEST_DATABASE_URL`: 用于持久化断言的 PostgreSQL 连接串

## 本地运行

```bash
git clone https://github.com/Haohua-Sun/fastapi-pytest-api-tests.git
cd fastapi-pytest-api-tests
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

运行检查和测试：

```bash
python -m ruff check tests utils
python -m pytest -v
```

生成 Allure 结果和 HTML 报告：

```bash
python -m pytest -v
allure generate allure-results -o allure-report --clean
allure open allure-report
```

本地生成或打开 HTML 报告需要额外安装 Allure CLI。CI 会将 `allure-results` 和 `allure-report` 作为构建 artifacts 发布。
