from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import test_progress, bugs, kpi

app = FastAPI(title="测试管理系统", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(test_progress.router, prefix="/api/test-progress", tags=["测试进度"])
app.include_router(bugs.router, prefix="/api/bugs", tags=["Bug追踪"])
app.include_router(kpi.router, prefix="/api/kpi", tags=["KPI数据"])

@app.get("/")
async def root():
    return {"message": "测试管理系统API"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
