# FastAPI Pytest API Test Suite - OpenAPI 覆盖说明

本文档基于根目录 `openapi.json` 和当前 pytest 用例整理，用于说明接口自动化覆盖范围、覆盖方式和暂未覆盖原因。

## 总览

- OpenAPI 操作数：23
- 已自动化覆盖：17
- 暂未覆盖：6
- 当前 pytest 收集用例数：58
- 已知缺陷用例：1 条 `xfail`

当前覆盖重点放在核心业务回归：登录认证、用户资料、管理员用户管理、Item CRUD、权限隔离、响应契约校验和数据库断言。

## 已覆盖接口

| Method | Path | 覆盖点 | 主要用例 |
| --- | --- | --- | --- |
| GET | `/api/v1/utils/health-check/` | 服务可用性 | `test_01_health_check.py` |
| POST | `/api/v1/login/access-token` | 管理员登录成功、密码错误、不存在用户、空用户名、空密码 | `test_02_login.py` |
| POST | `/api/v1/login/test-token` | 有效 token、非法 token、空 token、缺失 token | `test_03_auth_token.py` |
| POST | `/api/v1/users/signup` | 注册成功、字段校验、重复邮箱 | `test_04_users.py` |
| GET | `/api/v1/users/me` | 当前用户读取、非法 token 访问 | `test_04_users.py`, `test_06_item_crud_flow.py` |
| PATCH | `/api/v1/users/me` | 当前用户资料更新、邮箱格式校验 | `test_04_users.py` |
| PATCH | `/api/v1/users/me/password` | 密码修改成功、旧密码失效、新密码可登录、旧密码错误 | `test_04_users.py` |
| GET | `/api/v1/users/` | 管理员列表读取、非管理员禁止访问 | `test_08_admin.py` |
| POST | `/api/v1/users/` | 管理员创建用户、字段校验、非管理员禁止访问 | `test_08_admin.py` |
| GET | `/api/v1/users/{user_id}` | 管理员读取指定用户、删除后读取 404 | `test_08_admin.py` |
| PATCH | `/api/v1/users/{user_id}` | 管理员更新用户、非管理员禁止更新 | `test_08_admin.py` |
| DELETE | `/api/v1/users/{user_id}` | 管理员删除用户、非管理员禁止删除 | `test_08_admin.py` |
| GET | `/api/v1/items/` | 列表读取、分页边界、负数分页已标记已知缺陷 | `test_05_items_api.py` |
| POST | `/api/v1/items/` | 创建成功、边界值、字段校验、缺失/非法 token、无 token 业务流 | `test_05_items_api.py`, `test_06_item_crud_flow.py` |
| GET | `/api/v1/items/{id}` | 读取成功、非法 UUID、不存在 ID、权限隔离、删除后读取 404 | `test_05_items_api.py`, `test_06_item_crud_flow.py` |
| PUT | `/api/v1/items/{id}` | 更新成功、边界值、非法 UUID、不存在 ID、缺失/非法 token、权限隔离 | `test_05_items_api.py`, `test_06_item_crud_flow.py` |
| DELETE | `/api/v1/items/{id}` | 删除成功、非法 UUID、不存在 ID、权限隔离 | `test_05_items_api.py`, `test_06_item_crud_flow.py` |

## 数据库断言覆盖

| Method | Path | 数据库校验点 | 主要用例 |
| --- | --- | --- | --- |
| POST | `/api/v1/items/` | 创建后 `item` 表存在对应记录 | `test_07_database.py` |
| PUT | `/api/v1/items/{id}` | 更新后 `title`、`description` 持久化 | `test_07_database.py` |
| DELETE | `/api/v1/items/{id}` | 删除后数据库记录不存在 | `test_07_database.py` |

数据库断言通过 `API_TEST_DATABASE_URL` 连接被测服务使用的 PostgreSQL 数据库，验证 API 操作后的持久化结果。

## 响应契约覆盖

当前 `utils/schemas.py` 根据 `openapi.json` 中的核心响应模型维护 JSON Schema：

- `Token`
- `Message`
- `UserPublic`
- `UsersPublic`
- `ItemPublic`
- `ItemsPublic`
- `HTTPValidationError`

核心业务响应对象禁止未知字段，避免接口返回结构偏离契约时仍被测试放过。FastAPI/Pydantic 的 422 校验错误响应保留适度弹性，以兼容不同版本可能出现的 `input`、`ctx` 等错误详情字段。

## 暂未覆盖接口

| Method | Path | 暂未覆盖原因 |
| --- | --- | --- |
| POST | `/api/v1/password-recovery/{email}` | 涉及邮件发送流程，依赖邮件服务或邮件测试替身，当前项目优先覆盖核心 API 回归。 |
| POST | `/api/v1/reset-password/` | 依赖密码找回 token 的生成和流转，适合在补齐邮件/验证码测试替身后覆盖。 |
| POST | `/api/v1/password-recovery-html-content/{email}` | 偏邮件模板内容生成接口，不属于当前核心业务回归范围。 |
| DELETE | `/api/v1/users/me` | 会删除当前登录用户，需额外设计一次性账号和后置校验，当前已通过管理员删除覆盖用户删除能力。 |
| POST | `/api/v1/utils/test-email/` | 依赖邮件配置，属于外部服务集成场景，当前不作为默认回归用例。 |
| POST | `/api/v1/private/users/` | 偏初始化/私有接口，不属于普通用户和管理员核心业务链路。 |

## 已知缺陷

`test_read_items_negative_skip_should_be_rejected` 当前标记为 `xfail`。

期望行为：`GET /api/v1/items/?skip=-1&limit=10` 返回参数校验错误。

当前行为：被测服务返回 500。

该用例保留在测试集中，用于展示缺陷发现和回归跟踪能力。

## 后续可扩展方向

- 为密码找回流程引入邮件测试替身，覆盖 recovery 和 reset-password。
- 为 `DELETE /api/v1/users/me` 设计独立一次性账号用例，验证自删除能力。
- 基于 `openapi.json` 生成接口覆盖矩阵，定期对比新增/删除接口。
- 在迁移到 WSL 后补充 Docker Compose 和 CI，使被测服务与自动化套件可一键运行。
