from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.endpoints import student_flow, teacher_dash, ai_agent, ws_routes

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, 
    allow_methods=["*"], allow_headers=["*"]
)

@app.on_event("startup")
async def startup(): await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown(): await close_mongo_connection()

# 挂载路由 (按角色和功能划分)
app.include_router(student_flow.router, prefix="/api/student", tags=["1. 学生流程控制"])
app.include_router(ai_agent.router, prefix="/api/ai", tags=["2. AI 作文批改"])
app.include_router(teacher_dash.router, prefix="/api/teacher", tags=["3. 教师端数据展示"])
app.include_router(ws_routes.router, prefix="/ws", tags=["4. 实时通讯"])