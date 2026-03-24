# 测试管理系统

一个基于 Vue 3 + FastAPI 的前后端分离测试管理项目，用于展示测试进度、追踪测试Bug以及展示测试KPI表现。

## 功能特性

1. **测试进度管理**
   - 查看测试进度列表
   - 创建和编辑测试任务
   - 实时显示测试进度百分比
   - 查看测试用例统计（通过/失败）

2. **Bug追踪**
   - Bug列表展示和筛选
   - Bug统计信息（总数、状态分布、严重程度分布）
   - 创建、编辑、删除Bug
   - 按测试任务查看Bug

3. **KPI表现展示**
   - 天梯图：展示不同模型的性能排名
   - 坐标图（散点图）：对比不同模型的多个指标
   - 支持多种指标选择（准确率、精确率、召回率、F1分数等）

4. **人员与权限管理**
   - 用户与权限组管理
   - 支持将用户加入 `manager-group` 获得测试编辑权限
   - 联动测试进度的“测试负责人”，查看每个人任务数与时间占用

## 技术栈

### 后端
- FastAPI - 现代、快速的Web框架
- SQLAlchemy - ORM框架
- SQLite - 数据库（可切换为PostgreSQL）

### 前端
- Vue 3 - 渐进式JavaScript框架
- Vite - 快速的前端构建工具
- Element Plus - Vue 3组件库
- ECharts - 数据可视化图表库

## 项目结构

```
.
├── backend/              # 后端代码
│   ├── routers/         # API路由
│   ├── models.py        # 数据库模型
│   ├── schemas.py       # Pydantic模式
│   ├── database.py      # 数据库配置
│   ├── main.py          # FastAPI应用入口
│   └── requirements.txt # Python依赖
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── api/         # API调用
│   │   ├── views/       # 页面组件
│   │   ├── router/      # 路由配置
│   │   └── App.vue      # 根组件
│   ├── package.json     # 前端依赖
│   └── vite.config.js   # Vite配置
└── README.md
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 后端启动

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 初始化数据库：
```bash
python init_db.py
```

4.1 若已有数据库，需执行迁移以添加新字段：
```bash
python migrate_db.py
```

> 新增人员管理功能后，建议先执行一次 `python migrate_db.py`，以创建用户/权限组相关表并补充 `estimated_hours` 字段。

5. 启动服务：
```bash
uvicorn main:app --reload --port 6000
```

后端服务将在 http://localhost:6000 启动

### 前端启动

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端服务将在 http://localhost:5173 启动

## API文档

启动后端服务后，可以访问以下地址查看API文档：

- Swagger UI: http://localhost:6000/docs
- ReDoc: http://localhost:6000/redoc

## 使用说明

### 测试进度管理

1. 在"测试进度"页面，可以查看所有测试任务的进度
2. 点击"新建测试"按钮创建新的测试任务
3. 可以编辑测试状态、进度和用例统计
4. 点击"查看Bug"可以查看该测试相关的Bug

### Bug追踪

1. 在"Bug追踪"页面，可以查看所有Bug
2. 使用筛选器按状态和严重程度筛选Bug
3. 点击"新建Bug"创建新的Bug记录
4. 可以编辑Bug信息或删除Bug

### KPI表现

1. 在"KPI表现"页面，可以查看两个图表：
   - **天梯图**：选择指标和时间范围，查看模型性能排名
   - **坐标图**：选择X轴和Y轴指标，对比不同模型的性能

### 人员管理与权限分组

1. 在"人员管理"页面中可新增用户、编辑用户并分配权限组。
2. 默认存在 `manager-group`，加入该组后可编辑测试进度与Bug。
3. 在"测试进度"页面创建/编辑任务时，测试负责人可从人员列表中直接选择。
4. 人员管理页面会自动汇总每个人关联任务与预计工时占用（多人任务按成员均摊工时）。

默认管理员账号：

- 用户名：`manager`
- 密码：`123456`

#### 一键将用户加入 manager-group

可使用脚本：`backend/add_user_to_manager_group.py`

1. 仅把已存在用户加入 manager-group：

```bash
cd backend
python add_user_to_manager_group.py alice
```

2. 若用户不存在，自动创建并加入 manager-group：

```bash
cd backend
python add_user_to_manager_group.py bob --create-if-missing --display-name "Bob" --password 123456
```

3. 若用户已存在但禁用，执行加入组并自动启用：

```bash
cd backend
python add_user_to_manager_group.py charlie --activate
```

### KPI 数据手动导入（宽表：一行一个模型）

当前 KPI 数据推荐通过 CSV 一键导入。新格式为宽表：每行只描述一个模型，避免 `source/model_size/description` 重复。

#### CSV 一键导入（推荐）

项目已内置脚本：`backend/import_kpi_csv.py`，可直接从 CSV 批量导入到数据库（不依赖接口服务启动）。

1. 若数据库是旧版本，先迁移字段：

```bash
cd backend
venv\Scripts\python migrate_db.py
```

2. 准备 CSV（UTF-8 编码，首行表头），列如下：

- `model_category`（必填，ASR/TTS/Translation/VoicecallTranslation Solution）
- `model_name`（必填）
- `source`（可选）
- `model_size`（可选）
- `description`（可选）
- `power_consumption`（必填，数字）
- `latency`（必填，数字）
- `accuracy_en`（必填，数字）
- `accuracy_zh`（必填，数字）
- `accuracy_es`（必填，数字）
- `accuracy_overall`（必填，数字）
- `test_date`（可选，ISO 时间，例如 `2026-03-14T10:30:00`）

3. CSV 示例：

```csv
model_category,model_name,source,model_size,description,power_consumption,latency,accuracy_en,accuracy_zh,accuracy_es,accuracy_overall,test_date
ASR,Model-A,Internal Benchmark Set A,1.2B,面向通用语音识别优化的轻量化模型，强调实时转写与端侧部署能力。,72.8,118.4,0.946,0.931,0.919,0.932,
Translation,Model-F,Global Translation Benchmark v2,1.9B,新一代多语言翻译模型，强化长句语义保持与跨领域术语一致性。,70.2,112.7,0.958,0.941,0.929,0.943,
```

4. 执行一键导入：

```bash
cd backend
venv\Scripts\python import_kpi_csv.py .\kpi_data_sample_5models.csv
```

5. 如需导入前清空旧 KPI 数据：

```bash
cd backend
venv\Scripts\python import_kpi_csv.py .\kpi_data_sample_5models.csv --clear
```

> 说明：当前脚本不兼容旧的 `metric_name/metric_value` 长表 CSV。

#### 快速校验是否导入成功

```bash
curl "http://localhost:6000/api/kpi/metrics?model_name=Model-A"
```

## 开发说明

### 添加新的API端点

1. 在 `backend/routers/` 目录下创建或修改路由文件
2. 在 `backend/main.py` 中注册路由
3. 在 `backend/schemas.py` 中定义数据模式（如需要）

### 添加新的前端页面

1. 在 `frontend/src/views/` 目录下创建Vue组件
2. 在 `frontend/src/router/index.js` 中添加路由配置
3. 在 `frontend/src/App.vue` 中添加菜单项（如需要）

## 数据库

默认使用SQLite数据库，数据库文件为 `backend/test_management.db`。

如需使用PostgreSQL，请：
1. 修改 `backend/database.py` 中的数据库URL
2. 安装PostgreSQL并创建数据库
3. 更新 `requirements.txt` 中的数据库驱动

## 许可证

MIT License
