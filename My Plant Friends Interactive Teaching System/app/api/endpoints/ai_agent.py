from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.db.mongodb import db_instance
from app.websockets.ws_manager import ws_manager
from app.services.ai_service import get_coze_workflow_feedback # 导入大脑

router = APIRouter()

logger = logging.getLogger(__name__)

class DraftReq(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=10)
    img_url: str = Field(..., min_length=1)

@router.post("/stage3/submit-draft-ai")
async def handle_ai_feedback(req: DraftReq):
    # 记录收到的请求
    logger.info(f"收到AI评价请求: student_id={req.student_id}, img_url_length={len(req.img_url)}")
    
    # 1. 标准化学号格式（与student_flow.py保持一致）
    sid = req.student_id.zfill(2)
    logger.info(f"标准化学号: {req.student_id} -> {sid}")
    
    # 2. 查找学生
    student = await db_instance.db.students.find_one({"student_id": sid})
    if not student:
        logger.warning(f"学生不存在: {sid}")
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 3. 调用服务获取 AI 评语
    try:
        feedback = await get_coze_workflow_feedback(req.img_url, student.get("student_name"))
    except Exception as e:
        logger.error(f"AI服务调用失败: {e}")
        feedback = None
    
    # 4. 兜底策略
    if not feedback:
        feedback = f"{student.get('student_name', '同学')}的植物观察非常细致，描写生动！继续加油哦！"
    
    logger.info(f"AI评语生成: {feedback[:50]}...")

    # 5. 更新数据库
    await db_instance.db.students.update_one(
        {"student_id": sid},
        {"$set": {
            "draft_img": req.img_url,
            "ai_feedback_text": feedback,
            "has_completed_ai": True,
            "last_active_time": datetime.now()
        }}
    )

    # 6. 通知大屏实时刷新
    try:
        await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    except Exception as e:
        logger.warning(f"WebSocket通知失败: {e}")

    return {"status": "success", "feedback": feedback}
