# Vercel 部署步骤

前端和后端分别导入 Vercel，线上数据库使用外部 PostgreSQL。数据库可以选择 Neon 等托管服务，不需要自己租虚拟机，但数据库和后端依然运行在服务商的服务器上。

先使用 Vercel 分配的网址，确认功能可用再考虑购买域名。以下 YOUR-FRONTEND、YOUR-BACKEND 都是占位符，必须替换成实际项目地址。

## 1. 创建数据库

在 PostgreSQL 服务商创建一个专门用于此作业的数据库，复制连接字符串。使用服务商提供的带 SSL 的地址；如果提供 pooled / pooler 地址，优先使用它。

连接字符串通常类似：

```text
postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

连接字符串包含密码：不要放在前端、GitHub、博客或截图里，也不需要发给别人。

## 2. 部署后端

把 back_project 内的内容提交到单独的后端 GitHub 仓库。不要提交 .venv、data/calculator.db 和真实密码文件。

在 Vercel 选择 Add New → Project，导入后端仓库：

- Framework Preset：FastAPI；通常会自动识别。
- Root Directory：如果仓库根目录就是后端文件，保留默认；只有把整个作业目录上传时才填 back_project。
- 不要填写 uvicorn 启动命令，Vercel 会加载 index.py 中的 app。
- Python 版本由 .python-version 指定为 3.13。

在 Environment Variables 设置：

| 名称 | 值 | 用途 |
| --- | --- | --- |
| DATABASE_URL | 服务商给出的完整 PostgreSQL 地址 | 后端连接数据库，必须填写 |
| FRONTEND_ORIGINS | 实际前端地址，例如 https://YOUR-FRONTEND.vercel.app | 允许这个网页调用后端 |

前端地址暂时不知道，可以先只设置 DATABASE_URL 部署后端，等第 3 步获得前端地址，再补 FRONTEND_ORIGINS 并重新部署。值只填来源地址，不加 /api，不加路径，不加末尾斜杠；多个允许的地址用英文逗号分隔。

评审至少配置 Production 环境。Preview 如果也需要数据库，应使用独立测试库，不要让预览环境与正式环境共享可删除的记录。

应用启动时会创建历史表，不会自动导入本地 SQLite 的旧记录。首次部署后打开：

```text
https://YOUR-BACKEND.vercel.app/api/health
```

正常返回 {"status":"ok","database":"ok"}，代表后端能访问历史表。如果失败，查看 Vercel Logs；重点检查 DATABASE_URL、数据库网络访问限制和建表权限，不要把含密码的日志公开。

如需要提前建表，可在本地设置 DATABASE_URL 环境变量后运行 `python -m app.database`。本项目不会自动读取 .env 文件，.env.example 仅作为填写参考。

## 3. 部署前端并连接

在前端 js/config.js 中把接口地址改成实际后端网址：

```javascript
window.CALCULATOR_API_BASE_URL = "https://YOUR-BACKEND.vercel.app/api";
```

必须使用 https，保留末尾 /api；线上网页不能使用 127.0.0.1，否则会请求访问者自己的电脑。

把 front_project 内的文件提交到单独的前端 GitHub 仓库，在 Vercel 导入它。Framework Preset 选择 Other，不需要安装依赖或构建命令，Output Directory 使用 `.`。仓库根目录就是前端文件时，Root Directory 保留默认。

获得前端地址后，回后端 Settings → Environment Variables，把它填入 FRONTEND_ORIGINS，然后在 Deployments 重新部署后端。修改环境变量不会改变已经运行的旧部署。

前端配置是普通公开 JavaScript：不能在 Vercel 前端项目填一个同名环境变量就期待它自动替换，要修改 js/config.js 并提交、重新部署。

## 4. 上线检查

用不登录 Vercel 的浏览器或无痕窗口检查，确保正式前后端地址不要求 Vercel 登录。需要时在项目 Settings → Deployment Protection 中调整正式环境的访问保护。

1. 打开前端，计算 `(1+2)*3`，应得到 9。
2. 测试 `sqrt(9)`、`2^3`、`sin(30)`（DEG），以及 `1/0` 的错误提示。
3. 查看历史，测试搜索、收藏、分页和单条删除。
4. 刷新页面，再关闭后端本地终端，线上功能仍应正常。
5. 重新部署后端，确认已保存的线上历史仍存在，这是数据库持久化的重要检查。
6. 全部删除只在专门的测试记录上操作，它包含收藏记录且不能撤销。

当前历史是所有访问者共享的，接口没有登录权限；任何能访问接口的人都能删除记录。仅作为作业演示，不要存敏感数据。CORS 不是身份认证，也不能阻止他人直接请求接口。

这里列的是待执行检查，不代表已经完成线上验证。博客应填写自己实际验证的结果、日期和可公开访问的地址，并在评审前用自己的网络及其他设备检查可访问性。

## 5. 域名（可选）

功能跑通后，在前端 Vercel 项目的 Settings → Domains 添加购买的域名，按照界面提示配置 DNS。后端仍可使用原来的 vercel.app 地址。

前端改用新域名后，需要把新来源加入后端 FRONTEND_ORIGINS，再重新部署后端。如果后端也换域名，同时修改前端 js/config.js。

## 本地运行不变

不设置 DATABASE_URL 时继续使用 data/calculator.db。安装新增依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

本地前端 js/config.js 设置为 http://127.0.0.1:8000/api。本地和线上数据库是两套独立记录；切换配置不会搬运或删除原数据库。

## 官方参考

- [Vercel FastAPI 部署](https://vercel.com/docs/frameworks/backend/fastapi)
- [Python 运行环境](https://vercel.com/docs/functions/runtimes/python)
- [SQLite 与 Vercel](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel)
- [绑定域名](https://vercel.com/docs/domains/working-with-domains/add-a-domain)
