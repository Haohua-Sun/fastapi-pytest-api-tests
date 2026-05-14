# FastAPI Pytest API 测试套件

[English](README.md) | 简体中文

[![API automation tests](https://github.com/Haohua-Sun/fastapi-pytest-api-tests/actions/workflows/api-tests.yml/badge.svg)](https://github.com/Haohua-Sun/fastapi-pytest-api-tests/actions/workflows/api-tests.yml)

这是一个面向 [`full-stack-fastapi-template`](https://github.com/Haohua-Sun/full-stack-fastapi-template) 的接口自动化测试套件，使用 `pytest`、`requests`、JSON Schema 校验、SQLAlchemy 数据库断言、Allure 报告输出和 GitHub Actions CI 构建。

测试套件覆盖登录认证、token 校验、用户流程、管理员用户管理、Item CRUD、权限隔离、响应契约校验、业务链路以及 PostgreSQL 持久化检查。

## 项目亮点

- 封装 `ApiClient`，统一管理请求路径、鉴权头、超时、响应处理和 Allure 附件。
- 使用 pytest fixtures 管理环境加载、管理员 token、临时用户/Item 和测试数据清理。
- 使用 JSON 文件维护登录和 Item 相关的数据驱动用例。
- 基于 `openapi.json` 中的 OpenAPI 契约进行 JSON Schema 响应断言。
- 针对创建、更新、删除行为提供数据库持久化断言。
- 对 Allure 请求/响应附件中的敏感字段进行脱敏。
- GitHub Actions CI 会通过 Docker Compose 启动 FastAPI 应用，执行测试套件，并上传 Allure artifacts。

## 技术栈

- `pytest`: 测试组织、fixture、marker、参数化
- `requests`: HTTP API 请求
- `jsonschema`: 响应契约校验
- `SQLAlchemy` + `psycopg`: PostgreSQL 持久化断言
- `allure-pytest`: Allure 原始结果生成
- Allure CLI: CI 和本地运行中的 HTML 报告生成
- `python-dotenv`: 本地环境变量加载
- `ruff`: 静态检查
- GitHub Actions + Docker Compose: CI 执行环境

## 项目结构

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

生成 Allure 原始结果：

```bash
python -m pytest -v
```

原始结果会写入 `allure-results/`。如需本地查看 HTML 报告，需要额外安装 Allure CLI 并执行：

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

从 GitHub Actions 下载 `allure-report` artifact 后，建议通过 HTTP 服务打开解压后的目录：

```bash
cd allure-report
python3 -m http.server 5050
```

然后访问 `http://localhost:5050`。直接通过 `file://` 打开 `index.html` 可能会显示空白页，因为浏览器会阻止本地 JSON 文件加载。

## 测试标记

- `smoke`: 服务可用性
- `auth`: 登录、token 和鉴权
- `users`: 注册、用户资料和密码流程
- `admin`: 管理员用户管理
- `items`: Item 资源操作
- `flow`: 多步骤业务链路
- `schema`: 响应契约校验
- `db`: 数据库持久化断言

## 覆盖范围

当前测试套件可收集 `58` 条用例，覆盖 `17/23` 个 OpenAPI 操作。覆盖矩阵、数据库断言范围、已知缺陷跟踪和后续扩展计划见 [OPENAPI_COVERAGE.md](OPENAPI_COVERAGE.md)。

当前保留 1 条 `xfail` 已知缺陷用例：`GET /api/v1/items/` 在传入负数 `skip` 时返回 `500`，预期应返回参数校验错误。

## 持续集成

GitHub Actions 已在 [.github/workflows/api-tests.yml](.github/workflows/api-tests.yml) 中启用。

每次 push、pull request 或手动触发时，CI 会：

1. 拉取本 API 测试仓库。
2. 拉取 `Haohua-Sun/full-stack-fastapi-template`。
3. 为 FastAPI 应用创建 CI 专用 `.env` 文件。
4. 使用 Docker Compose 启动 FastAPI 后端和 PostgreSQL。
5. 执行 `ruff` 和完整的 `pytest` API 测试套件。
6. 基于 `allure-results` 生成 Allure HTML 报告。
7. 上传 `allure-results` 和 `allure-report` 两个 workflow artifacts。
8. 失败时打印 Docker 日志，并清理 Compose 环境。

## Jenkins Pipeline

本仓库也提供 [Jenkinsfile](Jenkinsfile)，Jenkins Pipeline 任务可以通过 `Pipeline script from SCM` 直接从 GitHub 读取并执行。

推荐的 Jenkins 配置：

- 使用带有 `api-tests` label 的 agent 执行构建。
- agent 连接成功后，将 built-in node 的 executor 数量设置为 `0`。
- 安装 Allure Jenkins 插件，在构建页面直接发布 `allure-results`，同时继续归档 `allure-results` 和 `allure-report` 作为兜底。
- 如果 Jenkins 能被 GitHub 访问，建议使用 GitHub webhook 触发；本地 Jenkins 无法被 GitHub 访问时，Jenkinsfile 仍保留每 5 分钟一次的 SCM 轮询作为兜底。

Jenkins 流水线会拉取本测试仓库，克隆 `Haohua-Sun/full-stack-fastapi-template`，生成 CI 环境配置，使用 Docker Compose 启动 FastAPI 后端和 PostgreSQL，执行 `ruff` 和 `pytest`，发布 JUnit 结果，生成 Allure HTML 报告，归档报告 artifacts，并清理 Compose 环境。

Jenkinsfile 会发布 JUnit 结果，通过 Allure Jenkins 插件发布 Allure 报告，同时将 `allure-results` 和生成的 `allure-report` 目录作为构建 artifacts 归档。

Jenkinsfile 已通过 `githubPush()` 预留 webhook 触发。若 Jenkins 部署在 GitHub 可访问的地址上，可在 GitHub 仓库中添加 webhook：

```text
Payload URL: http(s)://<jenkins-host>/github-webhook/
Content type: application/json
Events: Just the push event
```

本地 Docker/WSL 中的 Jenkins 通常无法被 GitHub 访问，因此本地自动化仍依赖 SCM 轮询触发。
