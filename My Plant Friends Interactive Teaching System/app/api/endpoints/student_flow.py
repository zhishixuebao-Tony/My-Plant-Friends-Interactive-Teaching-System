from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import httpx
from pydantic import BaseModel

from app.db.mongodb import db_instance
from app.services.oss_service import get_presigned_url
from app.websockets.ws_manager import ws_manager

router = APIRouter()


class LoginReq(BaseModel):
    student_id: str


class RecordCardReq(BaseModel):
    student_id: str
    checks: List[str]


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


class Stage5SubmitReq(BaseModel):
    student_id: str
    stage5_checks: List[str] = []
    total_stars: int = 0


class StageSyncReq(BaseModel):
    student_id: str
    current_stage: str


SENSORY_ALIAS_MAP = {
    '\u770b\u4e86\u770b': '\u770b\u4e00\u770b',
    '\u770b\u4e00\u770b': '\u770b\u4e00\u770b',
    '\u95fb\u4e86\u95fb': '\u95fb\u4e00\u95fb',
    '\u95fb\u4e00\u95fb': '\u95fb\u4e00\u95fb',
    '\u6478\u4e86\u6478': '\u6478\u4e00\u6478',
    '\u6478\u4e00\u6478': '\u6478\u4e00\u6478',
    '\u542c\u4e00\u542c': '\u542c\u4e00\u542c',
    '\u5c1d\u4e86\u5c1d': '\u5c1d\u4e00\u5c1d',
    '\u5c1d\u4e00\u5c1d': '\u5c1d\u4e00\u5c1d',
    '\u5176\u4ed6': '\u5176\u4ed6',
}


def _normalize_sensory_checks(checks: List[str]) -> List[str]:
    normalized = []
    seen = set()

    for item in checks:
        if item is None:
            continue
        key = str(item).strip()
        if not key:
            continue
        mapped = SENSORY_ALIAS_MAP.get(key, key)
        if mapped not in seen:
            normalized.append(mapped)
            seen.add(mapped)

    return normalized


def _student_id_query(raw_student_id: str) -> dict:
    sid = str(raw_student_id).strip().zfill(2)
    candidates = {sid}
    try:
        sid_int = int(sid)
        candidates.add(str(sid_int))
        candidates.add(sid_int)
    except ValueError:
        pass
    return {'student_id': {'$in': list(candidates)}}


def _student_id_text(raw_student_id: str) -> str:
    return str(raw_student_id).strip().zfill(2)


def _normalize_text_items(items: List[str]) -> List[str]:
    normalized = []
    seen = set()
    for item in items or []:
        key = str(item or '').strip()
        if not key:
            continue
        if key not in seen:
            normalized.append(key)
            seen.add(key)
    return normalized


def _calc_stage3_stars(checks: List[str]) -> int:
    values = _normalize_text_items(checks)
    has_unseen = any(('（1）' in v) or ('(1)' in v) or ('以前没观察到' in v) for v in values)
    has_feeling = any(('（2）' in v) or ('(2)' in v) or ('有了点儿感受' in v) or ('有了点儿感受' in v) for v in values)
    return int(has_unseen) + int(has_feeling)


def _calc_stage5_stars(checks: List[str]) -> int:
    values = _normalize_text_items(checks)
    has_clear = any(('我能写清楚' in v) for v in values)
    has_share = any(('我愿意分享我的习作' in v) for v in values)
    return int(has_clear) + int(has_share)


@router.post('/stage0/login')
async def student_login(req: LoginReq):
    sid = _student_id_text(req.student_id)
    query = _student_id_query(sid)

    student = await db_instance.db.students.find_one(query)
    if not student:
        raise HTTPException(status_code=404, detail=f'student {sid} not found')

    await db_instance.db.students.update_one(
        query,
        {'$set': {'is_logged_in': True, 'last_active_time': datetime.now()}},
    )

    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})

    return {
        'status': 'success',
        'data': {
            'student_id': _student_id_text(str(student.get('student_id', sid))),
            'student_name': student.get('student_name', ''),
            'pre_record_card': student.get('pre_record_card', ''),
            'pre_plant_1': student.get('pre_plant_1', ''),
            'pre_plant_2': student.get('pre_plant_2', ''),
            'pre_plant_3': student.get('pre_plant_3', ''),
        },
    }


@router.post('/stage/sync')
async def sync_student_stage(req: StageSyncReq):
    query = _student_id_query(req.student_id)
    stage_text = str(req.current_stage).strip()
    result = await db_instance.db.students.update_one(
        query,
        {
            '$set': {
                'current_stage': stage_text,
                'last_active_time': datetime.now(),
            }
        },
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='student not found')

    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    return {'status': 'success'}


@router.post('/stage1/sensory')
async def submit_stage1(req: SensoryReq):
    stage1_stars = 1 if len(_normalize_sensory_checks(req.checks)) > 0 else 0
    await db_instance.db.students.update_one(
        _student_id_query(req.student_id),
        {
            '$set': {
                'sensory_evaluations': _normalize_sensory_checks(req.checks),
                'stage1_stars': stage1_stars,
                'current_stage': '1',
                'last_active_time': datetime.now(),
            }
        },
    )
    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    return {'status': 'success'}


@router.post('/stage2/record-card')
async def submit_stage2(req: RecordCardReq):
    stage3_stars = _calc_stage3_stars(req.checks)
    student = await db_instance.db.students.find_one(_student_id_query(req.student_id), {'_id': 0})
    stage1_stars = int((student or {}).get('stage1_stars', 0) or 0)
    stage5_stars = int((student or {}).get('stage5_stars', 0) or 0)
    total_stars = stage1_stars + stage3_stars + stage5_stars
    await db_instance.db.students.update_one(
        _student_id_query(req.student_id),
        {
            '$set': {
                'dimension_evaluations': req.checks,
                'stage3_stars': stage3_stars,
                'total_stars': total_stars,
                'record_card_img': '',
                'current_stage': '3',
                'last_active_time': datetime.now(),
            }
        },
    )
    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    return {'status': 'success'}


@router.post('/stage3/save-draft')
async def save_draft_only(req: DraftSubmitReq):
    await db_instance.db.students.update_one(
        _student_id_query(req.student_id),
        {
            '$set': {
                'draft_img': req.img_url,
                'current_stage': '3',
                'last_active_time': datetime.now(),
            }
        },
    )
    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    return {'status': 'success', 'message': 'draft saved'}


@router.post('/stage4/complete-resources')
async def complete_stage4(req: ResourceCompleteReq):
    await db_instance.db.students.update_one(
        _student_id_query(req.student_id),
        {
            '$set': {
                'has_viewed_resources': True,
                'current_stage': '4',
                'last_active_time': datetime.now(),
            }
        },
    )
    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    return {'status': 'success', 'message': 'resources completed'}


@router.post('/track-resource-click/{student_id}/{res_id}')
async def track_resource_click(student_id: str, res_id: str):
    await db_instance.db.students.update_one(
        _student_id_query(student_id),
        {
            '$inc': {f'resource_click_stats.{res_id}': 1},
            '$set': {'last_active_time': datetime.now()},
        },
    )
    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    return {'status': 'recorded'}


@router.post('/stage5/final')
async def submit_stage5(req: FinalSubmitReq):
    student = await db_instance.db.students.find_one(_student_id_query(req.student_id), {'_id': 0})
    stage1_stars = int((student or {}).get('stage1_stars', 0) or 0)
    stage3_stars = int((student or {}).get('stage3_stars', 0) or 0)
    stage5_stars = int((student or {}).get('stage5_stars', 0) or 0)
    total_stars = stage1_stars + stage3_stars + stage5_stars

    await db_instance.db.students.update_one(
        _student_id_query(req.student_id),
        {
            '$set': {
                'has_claimed_certificate': True,
                'total_stars': total_stars,
                'current_stage': '5',
                'last_active_time': datetime.now(),
            }
        },
    )
    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    return {'status': 'success', 'message': 'final submitted'}


@router.post('/stage5/submit')
async def submit_stage5_with_checks(req: Stage5SubmitReq):
    stage5_checks = _normalize_text_items(req.stage5_checks)
    stage5_stars = _calc_stage5_stars(stage5_checks)
    student = await db_instance.db.students.find_one(_student_id_query(req.student_id), {'_id': 0})
    stage1_stars = int((student or {}).get('stage1_stars', 0) or 0)
    stage3_stars = int((student or {}).get('stage3_stars', 0) or 0)
    total_stars = stage1_stars + stage3_stars + stage5_stars

    await db_instance.db.students.update_one(
        _student_id_query(req.student_id),
        {
            '$set': {
                'stage5_checks': stage5_checks,
                'stage5_stars': stage5_stars,
                'total_stars': total_stars,
                'has_claimed_certificate': True,
                'current_stage': '5',
                'last_active_time': datetime.now(),
            }
        },
    )
    await ws_manager.notify_teacher({'action': 'REFRESH_DASHBOARD'})
    return {'status': 'success', 'message': 'stage5 submitted', 'total_stars': total_stars}


@router.get('/student/info/{student_id}')
async def get_student_info(student_id: str):
    student = await db_instance.db.students.find_one(_student_id_query(student_id))
    if not student:
        raise HTTPException(status_code=404, detail='student not found')

    return {
        'student_id': _student_id_text(str(student.get('student_id', student_id))),
        'student_name': student.get('student_name', ''),
        'pre_record_card': student.get('pre_record_card', ''),
        'pre_plant_1': student.get('pre_plant_1', ''),
        'pre_plant_2': student.get('pre_plant_2', ''),
        'pre_plant_3': student.get('pre_plant_3', ''),
    }


@router.post('/get-oss-ticket')
async def generate_oss_upload_ticket(req: OssSignReq):
    try:
        urls = get_presigned_url(req.student_id, req.file_extension, req.module_name)
        return {'status': 'success', 'data': urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'failed to sign oss url: {str(e)}')


@router.get('/proxy-image')
async def proxy_image(url: str):
    safe_url = str(url or '').strip()
    if not safe_url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail='invalid url')
    if 'aliyuncs.com' not in safe_url:
        raise HTTPException(status_code=400, detail='unsupported host')

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(safe_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'proxy fetch failed: {str(e)}')

    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail='upstream image error')

    content_type = resp.headers.get('content-type', 'image/jpeg')
    return Response(content=resp.content, media_type=content_type)
