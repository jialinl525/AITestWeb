# 快速启动指南

## 第一步：启动后端

1. 打开终端，进入后端目录：
```bash
cd backend
```

2. 安装Python依赖（如果还没有安装）：
```bash
pip install -r requirements.txt
```

3. 初始化数据库：
```bash
python init_db.py
```

4. （可选）生成测试数据：
```bash
python seed_data.py
```

5. 启动后端服务：
```bash
# Windows
python -m uvicorn main:app --reload --port 8000

# 或使用启动脚本
start.bat
```

后端将在 http://localhost:8000 运行

## 第二步：启动前端

1. 打开新的终端窗口，进入前端目录：
```bash
cd frontend
```

2. 安装Node.js依赖：
```bash
npm install
```

3. 启动前端开发服务器：
```bash
npm run dev
```

前端将在 http://localhost:5173 运行

## 第三步：访问应用

在浏览器中打开 http://localhost:5173

## 功能测试

### 测试进度页面
- 查看测试进度列表
- 点击"新建测试"创建测试任务
- 编辑测试状态和进度

### Bug追踪页面
- 查看Bug列表和统计信息
- 使用筛选器按状态和严重程度筛选
- 创建、编辑、删除Bug

### KPI表现页面
- 查看天梯图：选择指标（准确率、精确率等）查看模型排名
- 查看坐标图：选择X轴和Y轴指标对比模型性能

## 常见问题

### 后端启动失败
- 确保Python版本 >= 3.8
- 检查是否安装了所有依赖：`pip install -r requirements.txt`
- 确保端口8000未被占用

### 前端启动失败
- 确保Node.js版本 >= 16
- 删除node_modules文件夹，重新运行 `npm install`
- 确保端口5173未被占用

### 数据库错误
- 运行 `python backend/init_db.py` 重新初始化数据库
- 如果使用SQLite，确保有写入权限

### CORS错误
- 确保后端CORS配置中包含前端地址（默认已配置 http://localhost:5173）
- 检查后端服务是否正常运行

## API文档

启动后端后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
