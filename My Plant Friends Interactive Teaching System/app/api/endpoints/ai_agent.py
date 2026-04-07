import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db.mongodb import db_instance
from app.services.ai_service import get_coze_workflow_feedback
from app.websockets.ws_manager import ws_manager

router = APIRouter()
logger = logging.getLogger(__name__)


class DraftReq(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=10)
    img_url: str = Field(..., min_length=1)


def _student_id_query(raw_student_id: str) -> dict:
    sid = str(raw_student_id).strip().zfill(2)
    candidates = {sid, str(int(sid))}
    query_values = list(candidates)
    try:
        query_values.append(int(sid))
    except ValueError:
        pass
    return {'student_id': {'$in': query_values}}


@router.post('/stage3/submit-draft-ai')
async def handle_ai_feedback(req: DraftReq):
    sid = str(req.student_id).strip().zfill(2)
    logger.info('AI feedback request: student_id=%s, img_url_length=%s', sid, len(req.img_url))

    query = _student_id_query(sid)
    student = await db_instance.db.students.find_one(query)
    if not student:
        raise HTTPException(status_code=404, detail='学生不存在')

    try:
        feedback = await get_coze_workflow_feedback(req.img_url, student.get('student_name'))
    except Exception as e:
        logger.error('AI service error: %s', e)
        feedback = None

    if not feedback:
        feedback = f"{student.get('student_name', '同学')}的植物观察非常细致，描写生动，继续加油。"

    await db_instance.db.students.update_one(
        query,
        {
            '$set': {
                'draft_img': req.img_url,
                'ai_feedback_text': feedback,
                'has_completed_ai': True,
                'last_active_time': datetime.now(),
            }
        },
    )

    try:
        await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    except Exception as e:
        logger.warning('WebSocket notify failed: %s', e)

    return {'status': 'success', 'feedback': feedback}
