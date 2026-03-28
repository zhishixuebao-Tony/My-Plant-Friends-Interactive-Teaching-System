from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
import random
from app.db.mongodb import db_instance
from app.websockets.ws_manager import ws_manager

router = APIRouter()

class DraftReq(BaseModel): student_id: str; img_url: str

@router.post("/stage3/submit-draft-ai")
async def submit_draft_and_ai(req: DraftReq):
    """环节3：上传初稿并获取 AI 评价 (Mock测试版)"""
    
    # 模拟大模型思考 2 秒
    await asyncio.sleep(2)
    
    mock_feedback = "【AI老师批改】这段写得很好，抓住了植物的颜色特点。如果在结尾加上你的感受就更好啦！"
    
    await db_instance.db.students.update_one(
        {"student_id": req.student_id},
        {"$set": {
            "draft_img": req.img_url,
            "ai_feedback_text": mock_feedback,
            "has_completed_ai": True,
            "current_stage": "4_resources"
        }}
    )
    await ws_manager.notify_teacher({"action": "REFRESH_DASHBOARD"})
    
    return {"feedback": mock_feedback}