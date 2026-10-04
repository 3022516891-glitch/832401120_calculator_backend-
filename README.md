# 前后端分离计算器后端

科学计算支持 `sqrt`、`log`（以 10 为底）、`ln`、`sin`、`cos`、`tan`，常数 `pi`（或 π）、`e`，以及幂和倒数表达式。计算请求可传 `angle_mode` 为 `DEG` 或 `RAD`，默认 DEG，历史记录保存该单位。例：`{"expression":"sin(30)","angle_mode":"DEG"}` 返回约 0.5。负数开根、非正数取对数、正切无定义和除零会返回明确错误。

## 项目信息

- 作业名称：第一次个人作业——前后端分离计算器
- 姓名：邱钰琪
- 学号：832401120
- 后端仓库：https://github.com/3022516891-glitch/832401120_calculator_backend-
- 前端仓库：https://github.com/3022516891-glitch/832401120_calculator_frontend
- 前端访问地址：https://832401120calculatorfrontend.vercel.app/
- 后端部署地址：https://832401120-calculator-backend-vlaf.vercel.app/

## 项目介绍

这是计算器项目的后端部分。前端把用户输入的原始表达式发送到后端，后端负责校验、解析和计算，并将成功的计算记录保存到数据库。本地默认使用 SQLite，设置 DATABASE_URL 后使用外部 PostgreSQL。项目没有使用 `eval()` 或 `exec()` 执行用户输入，并扩展了历史搜索、收藏置顶、备注和批量删除功能。

## 线上部署

前后端分别部署为 Vercel 项目，线上使用外部 PostgreSQL 持久化历史记录。具体配置、连接和验收步骤见 [DEPLOYMENT.md](DEPLOYMENT.md)。

## 技术栈

- Python 3.13
- FastAPI
- SQLite（本地）/ PostgreSQL（线上）
- Pytest

本地使用 SQLite，不需要额外安装数据库服务。线上使用 PostgreSQL 保存历史记录。FastAPI 负责请求校验与接口响应，`/docs` 提供自定义操作页。

## 项目结构

```text
back_project/
├── app/
│   ├── calculator.py  # 表达式解析和计算
│   ├── database.py    # 数据库连接与初始化
│   ├── history.py     # 历史记录增删查
│   ├── main.py        # FastAPI 应用和接口
│   ├── schemas.py     # 请求、响应数据结构
│   └── api_guide.html # 后端操作页
├── tests/            # 计算、历史记录与部署配置测试
├── index.py          # Vercel 应用入口
├── .python-version   # Python 版本
├── .env.example      # 环境变量格式示例，不含真实密码
├── .gitignore
├── .vercelignore
├── requirements.txt
├── DEPLOYMENT.md
├── README.md
└── codestyle.md
```

## 安装和启动

以下步骤用于 Windows 本地运行，需要已安装 Python 3.13。先进入包含 requirements.txt 的后端目录。下面使用当前电脑上的路径；克隆仓库后应替换成实际保存位置。

```powershell
cd "D:\Download_D\软工_个人作业1\back_project"
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

上述命令直接使用虚拟环境中的 Python，无需激活环境，在 PowerShell 和 CMD 中均可执行。如果 CMD 当前位于其他盘符，进入目录时使用 `cd /d "D:\Download_D\软工_个人作业1\back_project"`。已有有效的 .venv 时可跳过创建步骤。启动命令会持续运行，不会自动弹出浏览器，按 Ctrl+C 停止服务。

启动后访问：

- 健康检查：`http://127.0.0.1:8000/api/health`
- 后端操作页：`http://127.0.0.1:8000/docs`

`/docs` 提供计算、历史查询、搜索、收藏和删除操作。页面通过 HTTP 请求调用后端 API，表达式计算和数据保存由后端完成。

本地未设置 DATABASE_URL 时，首次启动自动创建 `data/calculator.db`。设置 DATABASE_URL 后连接 PostgreSQL，并自动初始化历史表。本地和线上记录彼此独立，不会自动迁移。.env.example 只展示配置格式，程序不会自动读取 .env 文件；线上连接地址在 Vercel 环境变量中设置，不提交到仓库。

## API 说明

| 方法 | 地址 | 功能 |
| --- | --- | --- |
| GET | `/api/health` | 检查服务与数据库连接 |
| POST | `/api/calculate` | 计算并保存记录 |
| GET | `/api/history` | 查询历史记录 |
| GET | `/api/history?page=1&page_size=10` | 分页查询历史 |
| GET | `/api/history?keyword=1%2B2` | 按表达式、结果或备注搜索 |
| GET | `/api/history?favorite_only=true` | 只查询收藏记录 |
| PATCH | `/api/history/{id}/favorite` | 收藏或取消收藏 |
| PATCH | `/api/history/{id}/metadata` | 修改记录的备注 |
| DELETE | `/api/history/batch` | 批量删除指定记录 |
| DELETE | `/api/history/{id}` | 删除指定记录 |
| DELETE | `/api/history` | 删除全部历史记录 |

请求示例：`{"expression": "(1+2)*3"}`

成功响应：`{"success": true, "expression": "(1+2)*3", "result": 9}`

错误响应：`{"success": false, "message": "除数不能为零"}`

## 前后端连接

后端默认运行在 `http://127.0.0.1:8000`。前端 `js/config.js` 配置接口地址。前端通过 Live Server 运行时通常是 `http://127.0.0.1:5500`，该地址已经加入后端 CORS 白名单。

本地联调时将前端 js/config.js 的 API 地址设为 `http://127.0.0.1:8000/api`，先启动后端，再用 Live Server 打开前端。线上使用后端 HTTPS 地址，并在后端 FRONTEND_ORIGINS 环境变量中配置前端来源；修改环境变量后重新部署。来源地址不含 /api 或其他路径。

## 科学计算和历史分页

计算接口支持 `3^2`（平方）、`2^3`（幂）、`sqrt(9)`（平方根），可以与四则运算组合。幂从右到左结合，`-2^2` 为 -4，`(-2)^2` 为 4。函数只允许 `sqrt`、`log`、`ln`、`sin`、`cos`、`tan`，不执行任意代码。负数开根、零的负数次幂、绝对值超过 1000 的指数和过大结果会返回错误。

`GET /api/history?page=1&page_size=10` 返回 `items`、`total`、`page`、`page_size`。可以组合 `keyword` 和 `favorite_only`。不传 `page` 时返回记录数组。

`DELETE /api/history` 删除所有历史，包含收藏记录，返回 `success` 和 `deleted_count`。前端操作前会弹出确认框；删除后无法撤销。

历史查询会将收藏记录排在普通记录之前，同组内按最新记录优先排列。每条记录可保存不超过 200 个字符的备注；关键词搜索会同时匹配表达式、结果和备注。`DELETE /api/history/batch` 接收 `{"ids":[1,2,3]}`，一次最多删除 100 条记录。

## 测试

安装依赖后运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

测试覆盖运算优先级、括号、小数、负数、除零、非法表达式、科学计算、分页、收藏、备注、批量删除和部署配置。

单元测试使用临时 SQLite 数据库或模拟 PostgreSQL 连接，不操作线上数据库，也不能替代真实的线上持久化测试。

线上检查可使用 `(1+2)*3`，确认结果为 9 并出现在历史中；刷新页面、重新部署后端后检查记录是否保留。错误输入可用 `1/0` 测试。删除测试只使用专门创建的测试记录。

## 使用限制

目前没有登录与用户隔离，历史记录由所有访问者共享。全部删除会同时删除收藏记录且无法撤销。项目用于作业演示，不保存敏感信息。数据库密码和两步验证密钥不提交到 GitHub 或博客。
