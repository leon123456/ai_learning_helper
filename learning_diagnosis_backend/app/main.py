# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import routes_ocr, routes_diagnostic, routes_teacher, routes_planner, routes_paper

app = FastAPI(
    title="Learning Diagnosis Backend",
    version="0.1.0",
    description="智能学习诊断系统后端（Demo 骨架）"
)

# 简单 CORS 设置，方便前端或本地调试
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 之后可以根据域名收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(routes_ocr.router, prefix="/api/v1", tags=["ocr"])
app.include_router(routes_diagnostic.router, prefix="/api/v1", tags=["diagnostic"])
app.include_router(routes_paper.router, prefix="/api/v1", tags=["paper"])
app.include_router(routes_teacher.router, prefix="/api/v1", tags=["teacher"])
app.include_router(routes_planner.router, prefix="/api/v1", tags=["planner"])


@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "Learning Diagnosis Backend API",
        "version": "0.1.0",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "ocr": "/api/v1/ocr/parse",
            "diagnose": "/api/v1/diagnose",
            "paper_recognize": "/api/v1/paper/recognize",
            "paper_batch_diagnose": "/api/v1/paper/batch-diagnose",
            "teacher": "/api/v1/teacher/*",
            "planner": "/api/v1/planner/*"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}
