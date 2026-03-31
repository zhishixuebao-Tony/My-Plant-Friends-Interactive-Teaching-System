from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

from app.db.mongodb import db_instance
from app.websockets.ws_manager import ws_manager
from app.services.ai_service import get_coze_workflow_feedback # 导入大脑

router = APIRouter()

class DraftReq(BaseModel):
    student_id: str
    img_url: str

@router.post("/stage3/submit-draft-ai")
async def handle_ai_feedback(req: DraftReq):
    # 1. 查找学生
    student = await db_instance.db.students.find_one({"student_id": req.student_id})
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 2. 调用服务获取 AI 评语
    feedback = await get_coze_workflow_feedback(req.img_url, student.get("student_name"))
    
    # 3. 兜底策略
    if not feedback:
        feedback = "你的植物观察非常细致，继续加油哦！"

    # 4. 更新数据库
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "draft_img": req.img_url,
            "ai_feedback_text": feedback,
            "has_completed_ai": True,
            "last_active_time": datetime.now()
        }}
    )

    # 5. 通知大屏实时刷新
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})

    return {"status": "success", "feedback": feedback}