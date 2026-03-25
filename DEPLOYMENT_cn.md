# 测试管理系统部署文档（Windows / Linux 内网）

本文档用于将本项目部署到公司内网机器，和 README 分离维护。

## 1. 部署目标与推荐架构

推荐在同一台服务器部署：

- Nginx：对外提供 Web 入口（80/443）
- FastAPI(Uvicorn)：仅监听本机端口（127.0.0.1:8080）
- 前端静态文件：由 Nginx 托管（frontend/dist）
- 数据库：SQLite（默认）或 PostgreSQL（可选）

推荐原因：

- 前端请求使用相对路径 `/api`，同域部署最简单
- 后端无需暴露到内网，减少攻击面
- 易于做开机自启和后续升级

## 2. 版本与资源要求

- Python 3.10+
- Node.js 18+（Vite 5 要求）
- npm 9+
- Nginx 1.20+
- CPU 2 核 / 内存 4GB 起步

## 3. 部署前准备

1. 获取代码到目标机器（git clone 或拷贝源码）。
2. 规划安装目录（示例）：
   - Windows: `C:\apps\AITestWeb`
   - Linux: `/opt/aitestweb`
3. 规划数据目录（建议和代码分离）：
   - Windows: `C:\apps\AITestWeb\data`
   - Linux: `/opt/aitestweb/data`
4. 规划访问地址（示例）：
   - `http://test-mgr.intra`

## 4. Windows 内网部署

以下命令使用 PowerShell。

### 4.1 安装依赖

- 安装 Python 3.10+（勾选 Add to PATH）
- 安装 Node.js 18+
- 安装 Nginx for Windows（解压到 `C:\apps\nginx`）

### 4.2 后端部署

```powershell
cd C:\apps\AITestWeb\backend

# 创建虚拟环境
py -3 -m venv .venv

# 安装依赖
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt

# 建议显式指定数据库路径，避免相对路径引发误写
$env:DATABASE_URL = "sqlite:///C:/apps/AITestWeb/data/test_management.db"

# 初始化与迁移
.\.venv\Scripts\python init_db.py
.\.venv\Scripts\python migrate_db.py
```

手工启动验证：

```powershell
cd C:\apps\AITestWeb\backend
$env:DATABASE_URL = "sqlite:///C:/apps/AITestWeb/data/test_management.db"
.\.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8080 --workers 2
```

验证接口：

```powershell
curl http://127.0.0.1:8080/api/health
```

### 4.3 前端打包

```powershell
cd C:\apps\AITestWeb\frontend
npm ci
npm run build
```

产物目录：`C:\apps\AITestWeb\frontend\dist`

### 4.4 Nginx 配置

编辑 `C:\apps\nginx\conf\nginx.conf`，增加 server 块（可按实际合并）：

```nginx
server {
    listen 80;
    server_name test-mgr.intra;

    root C:/apps/AITestWeb/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
      proxy_pass http://127.0.0.1:8080/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启动 Nginx：

```powershell
cd C:\apps\nginx
.\nginx.exe -t
.\nginx.exe
```

说明：

- `server_name test-mgr.intra;` 只是示例域名。如果公司内网 DNS 没有为它做解析，需要先在本机 hosts 文件中增加映射，或直接改成服务器实际主机名/IP。
- Windows hosts 文件路径：`C:\Windows\System32\drivers\etc\hosts`
- 本机测试可先加一行：`127.0.0.1 test-mgr.intra`
- ` .\nginx.exe ` 执行后即使当前终端没有明显输出，也不代表失败。可新开一个 PowerShell 验证：`curl http://127.0.0.1/`、`curl http://127.0.0.1/api/health`，以及 `curl http://test-mgr.intra/api/health`
- 如果想让 PowerShell 立即返回，可使用：`Start-Process .\nginx.exe`

### 4.5 Windows 开机自启（建议）

推荐用 NSSM 将后端与 Nginx 注册为服务。

1. 下载 NSSM（Non-Sucking Service Manager）
2. 注册后端服务：

```powershell
nssm install AITestWebBackend C:\apps\AITestWeb\backend\.venv\Scripts\python.exe
nssm set AITestWebBackend AppParameters "-m uvicorn main:app --host 127.0.0.1 --port 8080 --workers 2"
nssm set AITestWebBackend AppDirectory C:\apps\AITestWeb\backend
nssm set AITestWebBackend AppEnvironmentExtra DATABASE_URL=sqlite:///C:/apps/AITestWeb/data/test_management.db
nssm start AITestWebBackend
```

3. 注册 Nginx 服务（可选）：

```powershell
nssm install AITestWebNginx C:\apps\nginx\nginx.exe
nssm set AITestWebNginx AppDirectory C:\apps\nginx
nssm start AITestWebNginx
```

## 5. Linux 内网部署

以下以 Ubuntu 为例（Debian/CentOS 可类比调整）。

### 5.1 安装依赖

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx curl
```

安装 Node.js 18+（示例 NodeSource）：

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

### 5.2 创建运行用户与目录

```bash
sudo useradd -r -m -d /opt/aitestweb -s /bin/bash aittest || true
sudo mkdir -p /opt/aitestweb
sudo mkdir -p /opt/aitestweb/data
sudo chown -R aittest:aittest /opt/aitestweb
```

将项目代码放到 `/opt/aitestweb` 后执行：

### 5.3 后端部署

```bash
cd /opt/aitestweb/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

export DATABASE_URL="sqlite:////opt/aitestweb/data/test_management.db"
python init_db.py
python migrate_db.py
```

手工启动验证：

```bash
cd /opt/aitestweb/backend
export DATABASE_URL="sqlite:////opt/aitestweb/data/test_management.db"
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8080 --workers 2
```

验证接口：

```bash
curl http://127.0.0.1:8080/api/health
```

### 5.4 前端打包

```bash
cd /opt/aitestweb/frontend
npm ci
npm run build
```

### 5.5 systemd 托管后端

创建环境文件 `/etc/aitestweb/backend.env`：

```bash
DATABASE_URL=sqlite:////opt/aitestweb/data/test_management.db
```

创建服务文件 `/etc/systemd/system/aitestweb-backend.service`：

```ini
[Unit]
Description=AITestWeb FastAPI Backend
After=network.target

[Service]
Type=simple
User=aittest
Group=aittest
WorkingDirectory=/opt/aitestweb/backend
EnvironmentFile=/etc/aitestweb/backend.env
ExecStart=/opt/aitestweb/backend/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8080 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

生效并启动：

```bash
sudo mkdir -p /etc/aitestweb
sudo systemctl daemon-reload
sudo systemctl enable --now aitestweb-backend
sudo systemctl status aitestweb-backend
```

### 5.6 Nginx 配置

创建 `/etc/nginx/sites-available/aitestweb`：

```nginx
server {
    listen 80;
    server_name test-mgr.intra;

    root /opt/aitestweb/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
      proxy_pass http://127.0.0.1:8080/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用并重载：

```bash
sudo ln -sf /etc/nginx/sites-available/aitestweb /etc/nginx/sites-enabled/aitestweb
sudo nginx -t
sudo systemctl reload nginx
```

## 6. 验证清单

部署完成后检查：

1. 浏览器访问 `http://test-mgr.intra` 可打开系统。
2. `http://test-mgr.intra/api/health` 返回 `{"status":"ok"}`。
3. 登录默认管理员：
   - 用户名：`manager`
   - 密码：`123456`
4. 新建测试、Bug、KPI 页面接口可正常读写。

## 7. 升级发布流程（建议）

1. 备份数据库文件：
   - Windows: `C:\apps\AITestWeb\data\test_management.db`
   - Linux: `/opt/aitestweb/data/test_management.db`
2. 更新代码。
3. 后端执行依赖与迁移：
   - `pip install -r requirements.txt`
   - `python migrate_db.py`
4. 前端重新打包：`npm run build`
5. 重启后端服务并 reload Nginx。
6. 回归验证健康检查与关键页面。

## 8. 安全与内网建议

- 不要把 Uvicorn 直接绑定 `0.0.0.0` 对外暴露，优先走 Nginx 反向代理。
- 启用主机防火墙，仅开放 80/443（或内网约定端口）。
- 建议替换默认管理员密码。
- 建议开启 HTTPS（公司 CA 证书或内网证书体系）。
- 生产环境不要使用 `--reload`。

## 9. 常见问题

1. 页面打开空白或接口 404：
   - 检查 Nginx `try_files` 是否为 `/index.html`
   - 检查 `/api/` 代理是否指向 `127.0.0.1:8080`

2. 启动后找不到数据库或写入到错误位置：
   - 检查是否设置了 `DATABASE_URL`
   - 推荐使用绝对路径（本文示例）

3. 跨域报错：
   - 同域部署通常不会触发跨域
   - 若前后端分域部署，需要在后端 `main.py` 的 CORS `allow_origins` 中加入内网域名

4. 前端构建失败（Node 版本问题）：
   - Vite 5 需要 Node.js 18+

---

如需我再补一版“PostgreSQL 生产化部署”（含备份策略、连接池和主从建议），我可以在本文件后追加第 10 章。