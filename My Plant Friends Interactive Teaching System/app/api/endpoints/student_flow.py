from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import List
from datetime import datetime

# 导入项目内部模块
from app.db.mongodb import db_instance
from app.websockets.ws_manager import ws_manager
from app.services.oss_service import get_presigned_url

router = APIRouter()

# --- 1. 更新数据请求模型 ---

class LoginReq(BaseModel):
    student_id: str

class RecordCardReq(BaseModel):
    student_id: str
    checks: List[str]
    img_url: str

class SensoryReq(BaseModel):
    student_id: str
    checks: List[str]

class ResourceCompleteReq(BaseModel):
    student_id: str

class OssSignReq(BaseModel):
    student_id: str
    module_name: str     
    file_extension: str

class DraftSubmitReq(BaseModel):
    student_id: str
    img_url: str

class FinalSubmitReq(BaseModel):
    student_id: str

# --- 2. 核心业务接口修正 ---

@router.post("/stage0/login")
async def student_login(req: LoginReq):
    """
    环节0：学生登录
    """
    # 统一学号格式，确保是两位字符串（如 "1" -> "01"）
    sid = req.student_id.zfill(2)
    
    # 从数据库查找
    student = await db_instance.db.students.find_one({"student_id": sid})

    if not student:
        raise HTTPException(status_code=404, detail=f"学号 {sid} 不在数据库中")

    await db_instance.db.students.update_one(
            {"student_id": req.student_id},
            {"$set": {
                "is_logged_in": True,
            }}
        )

    # 通知教师端刷新
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    # 返回完整的数据包给前端 Pinia 存储
    return {
        "status": "success",
        "data": {
            "student_id": student["student_id"],
            "student_name": student["student_name"],
            "pre_record_card": student.get("pre_record_card", ""), # 记录卡
            "pre_plant_1": student.get("pre_plant_1", ""),        # 植物1
            "pre_plant_2": student.get("pre_plant_2", ""),        # 植物2
            "pre_plant_3": student.get("pre_plant_3", ""),        # 植物3
        }
    }

@router.post("/stage1/sensory")
async def submit_stage1(req: SensoryReq):
    """环节1：感知评估"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "sensory_evaluations": req.checks,
            "current_stage": "1", # 建议统一用数字字符串
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}

@router.post("/stage2/record-card")
async def submit_stage2(req: RecordCardReq):
    """环节2：记录卡提交"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "dimension_evaluations": req.checks,
            "record_card_img": req.img_url,
            "current_stage": "2",
            "last_active_time": datetime.now()
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success"}

@router.post("/stage3/save-draft")
async def save_draft_only(req: DraftSubmitReq):
    """环节3：保存习作初稿照片"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "draft_img": req.img_url,
            "current_stage": "3",  # 更新学生当前环节状态
            "last_active_time": datetime.now()
        }}
    )
    # 通知教师端大屏：有学生更新了数据，请刷新
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success", "message": "初稿已保存"}

@router.post("/stage4/complete-resources")
async def complete_stage4(req: ResourceCompleteReq):
    """环节4：完成资源包与习题通关"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "has_viewed_resources": True,  # 标记为已通关
            "current_stage": "4",          # 记录当前进度
            "last_active_time": datetime.now()
        }}
    )
    # 实时通知大屏更新通关人数
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success", "message": "知识闯关大成功！"}

@router.post("/track-resource-click/{student_id}/{res_id}")
async def track_resource_click(student_id: str, res_id: str):
    """
    环节4：资源点击统计
    """
    await db_instance.db.students.update_one(
        {"student_id": student_id},
        {
            # 使用 $inc 进行原子计数
            "$inc": {f"resource_click_stats.{res_id}": 1},
            "$set": {"last_active_time": datetime.now()}
        }
    )
    # 实时通知老师更新热度表
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "recorded"}

@router.post("/stage5/final")
async def submit_stage5(req: FinalSubmitReq):
    """环节5：完成本课程"""
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "current_stage": "5",  # 更新为定稿阶段
            "last_active_time": datetime.now()
        }}
    )
    # 通知教师端大屏：此时大屏上该学生的格子会出现 🏆 奖杯
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    return {"status": "success", "message": "定稿已提交，奖状已生成"}

@router.get("/student/info/{student_id}")
async def get_student_info(student_id: str):
    """
    获取学生完整信息（用于刷新页面后重新拉取数据）
    """
    sid = student_id.zfill(2)
    student = await db_instance.db.students.find_one({"student_id": sid})
    if student:
        return {
            "student_id": student["student_id"],
            "student_name": student["student_name"],
            "pre_record_card": student.get("pre_record_card", ""),
            "pre_plant_1": student.get("pre_plant_1", ""),
            "pre_plant_2": student.get("pre_plant_2", ""),
            "pre_plant_3": student.get("pre_plant_3", ""),
        }
    raise HTTPException(status_code=404, detail="学生不存在")

@router.post("/get-oss-ticket")
async def generate_oss_upload_ticket(req: OssSignReq):
    """
    前端拍照后，会先请求这个接口获取一个“临时通行证”
    """
    try:
        # 这里的 get_presigned_url 是你之前写好的阿里云 OSS 签名逻辑
        urls = get_presigned_url(req.student_id, req.file_extension, req.module_name)
        return {"status": "success", "data": urls}
    except Exception as e:
        print(f"OSS 签名生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取阿里云签名失败: {str(e)}")