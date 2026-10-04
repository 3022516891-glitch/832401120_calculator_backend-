# 前后端分离计算器后端

科学计算支持 `sqrt`、`log`（以 10 为底）、`ln`、`sin`、`cos`、`tan`，常数 `pi`（或 π）、`e`，以及幂和倒数表达式。计算请求可传 `angle_mode` 为 `DEG` 或 `RAD`，默认 DEG，历史记录保存该单位。例：`{"expression":"sin(30)","angle_mode":"DEG"}` 返回约 0.5。负数开根、非正数取对数、正切无定义和除零会返回明确错误。

## 项目信息

- 作业名称：第一次个人作业——前后端分离计算器
- 姓名：邱钰琪
- 学号：832401120
- 前端仓库：请填写链接
- 后端部署地址：部署后填写

## 项目介绍

这是计算器项目的后端部分。前端把用户输入的原始表达式发送到后端，后端负责校验、解析和计算，并将成功的计算记录保存到数据库。本地默认使用 SQLite，设置 DATABASE_URL 后使用外部 PostgreSQL。项目没有使用 `eval()` 或 `exec()` 执行用户输入，并扩展了历史搜索和收藏功能。

## 线上部署

前后端分别部署为 Vercel 项目，线上使用外部 PostgreSQL 持久化历史记录。具体配置、连接和验收步骤见 [DEPLOYMENT.md](DEPLOYMENT.md)。当前代码已准备部署入口，但部署地址和线上测试结果需要实际部署后填写。

## 技术栈

- Python 3.13
- FastAPI
- SQLite（本地）/ PostgreSQL（线上）
- Pytest

选择 SQLite 是因为本次作业的数据量较小，本地运行时不需要额外安装数据库服务。FastAPI 可以自动生成接口文档，便于前后端联调。

## 项目结构

```text
back_project/
├── app/
│   ├── calculator.py  # 表达式解析和计算
│   ├── database.py    # 数据库连接与初始化
│   ├── history.py     # 历史记录增删查
│   ├── main.py        # FastAPI 应用和接口
│   └── schemas.py     # 请求、响应数据结构
├── tests/test_calculator.py
├── requirements.txt
├── README.md
└── codestyle.md
```

## 安装和启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

启动后访问：

- 健康检查：`http://127.0.0.1:8000/api/health`
- 接口文档：`http://127.0.0.1:8000/docs`

`/docs` 是简洁的后端操作页，可以直接计算、查看历史、搜索、收藏和删除记录，不使用 Swagger 的 `Try it out` 按钮。页面通过 HTTP 请求调用同一套后端 API，计算与数据保存仍在后端完成。独立的前端项目继续使用这些 API。

数据库会在首次启动时自动创建为 `data/calculator.db`。

## API 说明

| 方法 | 地址 | 功能 |
| --- | --- | --- |
| GET | `/api/health` | 检查服务状态 |
| POST | `/api/calculate` | 计算并保存记录 |
| GET | `/api/history` | 查询历史记录 |
| GET | `/api/history?keyword=1%2B2` | 按表达式或结果搜索 |
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

联调时先启动后端，再用 Live Server 打开前端。部署后修改前端 js/config.js 的 API 地址和后端 FRONTEND_ORIGINS 环境变量，再重新部署。

## 测试

## 科学计算和历史分页

计算接口支持 `3^2`（平方）、`2^3`（幂）、`sqrt(9)`（平方根），可以与四则运算组合。幂从右到左结合，`-2^2` 为 -4，`(-2)^2` 为 4。函数只允许 `sqrt`、`log`、`ln`、`sin`、`cos`、`tan`，不执行任意代码。负数开根、零的负数次幂、绝对值超过 1000 的指数和过大结果会返回错误。

`GET /api/history?page=1&page_size=10` 返回 `items`、`total`、`page`、`page_size`。可以组合 `keyword` 和 `favorite_only`。不传 `page` 时保留原来的数组响应，兼容旧调用。

`DELETE /api/history` 删除所有历史，包含收藏记录，返回 `success` 和 `deleted_count`。前端操作前会弹出确认框；删除后无法撤销。

历史查询会将收藏记录排在普通记录之前，同组内按最新记录优先排列。每条记录可保存不超过 30 个字符的标签和不超过 200 个字符的备注；关键词搜索会同时匹配表达式、结果、标签和备注。`DELETE /api/history/batch` 接收 `{"ids":[1,2,3]}`，一次最多删除 100 条记录。

运行 `pytest`。测试覆盖优先级、括号、小数、负数、除零和非法表达式。
