from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

# 导入项目内部模块
from app.db.mongodb import db_instance
from app.core.config import settings
from app.websockets.ws_manager import ws_manager
from app.services.oss_service import get_presigned_url

router = APIRouter()

# --- 数据传输模型定义 ---

class LoginReq(BaseModel):
    student_id: str

class HeartbeatReq(BaseModel):
    student_id: str

class OssSignReq(BaseModel):
    student_id: str
    module_name: str     
    file_extension: str  

class SensoryReq(BaseModel):
    student_id: str
    checks: List[str]

class RecordCardReq(BaseModel):
    student_id: str
    checks: List[str]
    img_url: str  

class DraftSubmitReq(BaseModel):
    student_id: str
    img_url: str  

class ResourceCompleteReq(BaseModel):
    student_id: str

class FinalSubmitReq(BaseModel):
    student_id: str
    img_url: str  

# --- 核心业务接口实现 ---

@router.post("/stage0/login")
async def student_login(req: LoginReq):
    """环节0：学生登录，下发预置照片，初始化心跳时间"""
    name = settings.STUDENT_ROSTER.get(req.student_id)
    if not name:
        raise HTTPException(status_code=404, detail="该序号不在花名册中，请检查")
    
    pre_media = settings.PRELOAD_MEDIA.get(req.student_id, "https://via.placeholder.com/300?text=Plant_Photo")
    
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "student_name": name,
            "is_logged_in": True,
            "pre_photo_url": pre_media,
            "current_stage": "1_sensory",
            "last_active_time": datetime.now() # 初始化心跳
        }},
        upsert=True
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"student_id": req.student_id, "student_name": name, "pre_photo_url": pre_media}

@router.post("/stage0/logout")
async def student_logout(req: LoginReq):
    """学生主动退出登录"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "is_logged_in": False,
            "current_stage": "0_login",
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}

@router.post("/stage0/heartbeat")
async def student_heartbeat(req: HeartbeatReq):
    """学生端隐式心跳检测 (每5秒发一次)"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "is_logged_in": True,
            "last_active_time": datetime.now()
        }}
    )
    return {"status": "alive"}

@router.post("/get-oss-ticket")
async def generate_oss_upload_ticket(req: OssSignReq):
    """前端直传 OSS 签名接口"""
    try:
        urls = get_presigned_url(req.student_id, req.file_extension, req.module_name)
        return {"status": "success", "data": urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取阿里云签名失败: {str(e)}")

@router.post("/stage1/sensory")
async def submit_stage1(req: SensoryReq):
    """环节1：提交感官自评"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "sensory_evaluations": req.checks,
            "current_stage": "2_record_card",
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}

@router.post("/stage2/record-card")
async def submit_stage2(req: RecordCardReq):
    """环节2：提交修改后的记录卡照片与评价维度"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "dimension_evaluations": req.checks,
            "record_card_img": req.img_url,
            "current_stage": "3_draft_ai",
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}

@router.post("/stage3/save-draft")
async def save_draft_only(req: DraftSubmitReq):
    """环节3：仅保存初稿照片"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "draft_img": req.img_url,
            "current_stage": "3_draft_submitted",
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}

@router.post("/track-resource-click/{student_id}/{res_id}")
async def track_resource_click(student_id: str, res_id: str):
    """环节4：上报资源包点击热度（供大屏表3展示）"""
    await db_instance.db.students.update_one(
        {"student_id": student_id},
        {
            "$inc": {f"resource_click_stats.{res_id}": 1},
            "$set": {"last_active_time": datetime.now()}
        }
    )
    return {"status": "recorded"}

@router.post("/stage4/complete-resources")
async def complete_stage4(req: ResourceCompleteReq):
    """环节4：完成资源包与习题通关"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "has_viewed_resources": True,
            "current_stage": "5_final",
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}

@router.post("/stage5/final")
async def submit_stage5(req: FinalSubmitReq):
    """环节5：提交定稿作文照片"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "final_img": req.img_url,
            "current_stage": "6_completed",
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}

@router.post("/update-stage-only")
async def update_stage_only(student_id: str = Form(...), new_stage: str = Form(...)):
    """开发测试专用：强制更新环节"""
    await db_instance.db.students.update_one(
        {"student_id": student_id},
        {"$set": {
            "current_stage": new_stage,
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}