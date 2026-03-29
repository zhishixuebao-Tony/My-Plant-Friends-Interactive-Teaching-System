from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.endpoints import student_flow, teacher_dash, ai_agent, ws_routes
from fastapi.middleware.cors import CORSMiddleware
from app.db.mongodb import db_instance 


app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup(): await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown(): await close_mongo_connection()

@app.on_event("startup")
async def startup_db_client():
    # ... 原有的数据库连接代码 ...
    
    # 初始化教师密码（如果不存在则创建）
    admin_col = db_instance.db.admin_config
    existing = await admin_col.find_one({"key": "teacher_password"})
    if not existing:
        await admin_col.insert_one({"key": "teacher_password", "value": "123456"})
        print("✅ 教师端初始密码 123456 已存入数据库")

# 挂载路由 (按角色和功能划分)
app.include_router(student_flow.router, prefix="/api/student", tags=["1. 学生流程控制"])
app.include_router(ai_agent.router, prefix="/api/ai", tags=["2. AI 作文批改"])
app.include_router(teacher_dash.router, prefix="/api/teacher", tags=["3. 教师端数据展示"])
app.include_router(ws_routes.router, prefix="/ws", tags=["4. 实时通讯"])