# FastAPI Pytest API Test Suite

本项目面向 `full-stack-fastapi-template` 搭建接口自动化测试套件，用于展示基于 Python 的接口测试设计、框架封装、数据驱动、响应契约校验、测试数据清理和报告输出能力。

测试套件使用 `requests` 封装 HTTP 请求，使用 `pytest` 组织测试用例，结合 JSON 数据驱动、JSON Schema 校验、Allure 报告和可选数据库断言，覆盖登录认证、用户管理、管理员操作、Item 资源和核心业务链路。

## 技术栈

- `pytest`: 测试框架、fixture、marker、参数化用例
- `requests`: HTTP 请求封装
- `jsonschema`: 响应结构和字段契约校验
- `allure-pytest`: 测试报告原始结果生成
- `SQLAlchemy` + `psycopg`: 可选数据库断言
- `python-dotenv`: 本地 `.env` 配置加载
- `ruff`: 代码静态检查和格式约束

## 项目亮点

- 封装 `ApiClient`，统一管理接口路径、鉴权头、请求超时、异常提示和 Allure 请求/响应附件。
- 使用 pytest fixture 管理环境配置、管理员 token、临时用户、临时 item 和资源清理。
- 使用 JSON 文件维护登录、Item 创建、Item 更新等数据驱动用例。
- 根据根目录 `openapi.json` 维护响应 JSON Schema，校验 token、用户、Item、列表、消息和校验错误响应。
- 覆盖正向、反向、边界值、权限隔离、完整 CRUD 流程和管理员用户管理流程。
- 对 Allure 附件中的 token、password、Authorization 等敏感字段做脱敏处理。
- 提供可选数据库断言，验证 API 操作后的持久化结果。

## 目录结构

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
│   ├── allure_helpers.py
│   ├── api_client.py
│   ├── assertions.py
│   ├── case_resolvers.py
│   ├── config.py
│   ├── data_loader.py
│   ├── db_client.py
│   ├── schemas.py
│   └── test_resources.py
├── .env.example
├── openapi.json
├── OPENAPI_COVERAGE.md
├── pytest.ini
├── pyproject.toml
├── README.md
└── requirements.txt
```

## 环境配置

项目启动时会读取根目录下的 `.env` 文件。真实配置不应提交到仓库，可参考 `.env.example` 创建本地配置：

```env
BASE_URL=http://localhost:8000
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=changethis
API_TEST_TIMEOUT=10
API_TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/app
```

配置说明：

- `BASE_URL`: 被测 API 服务地址。
- `ADMIN_EMAIL` / `ADMIN_PASSWORD`: 管理员账号，用于获取管理员 token。
- `API_TEST_TIMEOUT`: 接口请求超时时间，单位为秒。
- `API_TEST_DATABASE_URL`: 可选数据库连接串。未配置时，`@pytest.mark.db` 用例会自动跳过。

## 安装依赖

建议为本项目创建独立虚拟环境，避免依赖安装到 WSL/系统 Python 全局环境：

```bash
git clone https://github.com/<your-username>/fastapi-pytest-api-tests.git
cd fastapi-pytest-api-tests
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

VS Code 中建议选择项目虚拟环境解释器：

```text
<repo-root>/.venv/bin/python
```

Allure 报告查看需要额外安装 Allure CLI。`requirements.txt` 中的 `allure-pytest` 只负责生成 `allure-results` 原始结果，不提供 `allure` 命令。

WSL/Ubuntu 可使用 npm 安装 Linux 版 Allure CLI：

```bash
sudo apt update
sudo apt install -y default-jre nodejs npm
sudo npm install -g allure-commandline
which allure
allure --version
```

如果 `which allure` 指向 `/mnt/c/...`，说明当前命中的是 Windows 版 Allure；应重新打开 WSL 终端，或优先使用 Linux 版 Allure 命令路径。

## 常用命令

收集用例：

```bash
python -m pytest --collect-only -q
```

全量执行：

```bash
python -m pytest -v
```

只跑冒烟用例：

```bash
python -m pytest -v -m smoke
```

只跑业务链路：

```bash
python -m pytest -v -m flow
```

只跑数据库断言：

```bash
python -m pytest -v -m db
```

代码检查：

```bash
python -m ruff check tests utils
```

查看 Allure 报告：

```bash
python -m pytest -v
allure generate allure-results -o allure-report --clean
allure open --host 0.0.0.0 --port 5050 allure-report
```

WSL 中 `allure open` 不一定会自动拉起 Windows 浏览器，可在 Windows 浏览器中手动打开：

```text
http://localhost:5050
```

如果 `localhost` 无法访问，可查看 WSL IP：

```bash
hostname -I
```

然后在 Windows 浏览器中访问：

```text
http://<WSL_IP>:5050
```

本机若已运行 Jenkins，默认会占用 `8080` 端口；Allure 本地查看建议使用 `5050` 或其他空闲端口。

## 测试分层

项目通过 pytest marker 区分测试范围：

- `smoke`: 服务可用性检查。
- `auth`: 登录、token 和鉴权相关测试。
- `users`: 用户注册、当前用户、资料修改、密码修改。
- `admin`: 管理员用户管理。
- `items`: Item 资源查询、创建、更新、删除。
- `flow`: 多步骤业务链路。
- `schema`: 响应 JSON Schema 校验。
- `db`: 可选数据库断言，需要配置 `API_TEST_DATABASE_URL`。

## 当前覆盖

当前测试可收集 `58` 条用例，覆盖 OpenAPI 中 `17/23` 个操作。详细覆盖说明见 [OPENAPI_COVERAGE.md](OPENAPI_COVERAGE.md)。

当前保留 1 条 `xfail` 用例：`GET /api/v1/items/` 传入负数 `skip` 时，被测服务当前返回 500，而预期应为参数校验错误。

## CI 状态

当前未启用 CI。原因是被测 FastAPI 服务运行在本地 Docker/WSL 环境，GitHub Actions 云端无法直接访问本机 `localhost:8000`。后续如果需要接入 Jenkins，可在 Jenkins 节点中启动被测服务并执行 `python -m pytest -v`，再由 Jenkins Allure 插件读取 `allure-results` 目录。
