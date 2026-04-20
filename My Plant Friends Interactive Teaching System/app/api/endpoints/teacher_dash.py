from fastapi import APIRouter
from pydantic import BaseModel

from app.db.mongodb import db_instance
from app.utils.role_rules import is_judge_student_id


class PasswordReq(BaseModel):
    password: str


router = APIRouter()


SENSORY_ALIAS_MAP = {
    '看了看': '看一看',
    '看一看': '看一看',
    '闻了闻': '闻一闻',
    '闻一闻': '闻一闻',
    '摸了摸': '摸一摸',
    '摸一摸': '摸一摸',
    '听一听': '听一听',
    '尝了尝': '尝一尝',
    '尝一尝': '尝一尝',
    '其他': '其他',
}

DIMENSION_ALIAS_MAP = {
    '我暂时没有新的发现': '我暂时没有新的发现',
    '我暂时没有新的发现。': '我暂时没有新的发现',
    '我已经有了新的发现：（1）有以前没观察到的': '我已经有了新的发现：（1）有以前没观察到的',
    '评价一：能真实记录植物特点': '我已经有了新的发现：（1）有以前没观察到的',
    '评价一': '我已经有了新的发现：（1）有以前没观察到的',
    '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价二：能描写出自己的感受': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价二': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
}

WRITING_ALIAS_MAP = {
    '（1）我能从多方面介绍': '（1）我能从多方面介绍',
    '（1）我能从多方面介绍。（√）': '（1）我能从多方面介绍',
    '（2）我能有顺序介绍': '（2）我能有顺序介绍',
    '（2）我能有顺序介绍。（√）': '（2）我能有顺序介绍',
    '2.我分享了我的习作': '2.我分享了我的习作',
    '我分享了我的习作': '2.我分享了我的习作',
}


def _normalize_stats(raw_stats: dict, alias_map: dict) -> dict:
    normalized = {}
    for key, count in raw_stats.items():
        norm_key = str(key).strip()
        mapped = alias_map.get(norm_key, norm_key)
        normalized[mapped] = normalized.get(mapped, 0) + int(count)
    return normalized


def _student_id_query(raw_student_id: str) -> dict:
    sid_text = str(raw_student_id).strip()
    if not sid_text:
        return {'student_id': sid_text}

    sid_zfill = sid_text.zfill(2)
    query_values = {sid_text, sid_zfill}
    try:
        sid_int = int(sid_text)
        query_values.add(sid_int)
        query_values.add(str(sid_int))
    except ValueError:
        pass

    return {'student_id': {'$in': list(query_values)}}


def _to_clean_list(values):
    if not isinstance(values, list):
        return []
    return [str(v or '').strip() for v in values if str(v or '').strip()]


def _calc_stage1_from_sensory(sensory_values: list) -> int:
    return 1 if len(_to_clean_list(sensory_values)) > 0 else 0


def _calc_stage3_from_dimension(dimension_values: list) -> int:
    values = _to_clean_list(dimension_values)
    has_discovery = any(
        ('（1）' in v)
        or ('(1)' in v)
        or ('（2）' in v)
        or ('(2)' in v)
        or ('以前没观察到' in v)
        or ('有了点儿感受' in v)
        or ('感受' in v)
        for v in values
    )
    return 1 if has_discovery else 0


def _calc_stage5_from_checks(stage5_checks: list) -> int:
    values = _to_clean_list(stage5_checks)
    has_multiaspect = any(('（1）' in v) or ('(1)' in v) or ('多方面' in v) for v in values)
    has_orderly = any(('（2）' in v) or ('(2)' in v) or ('顺序' in v) for v in values)
    has_shared = any(('分享' in v) or ('愿意把习作分享' in v) for v in values)
    return int(has_multiaspect) + int(has_orderly) + int(has_shared)


@router.get('/dashboard/statistics')
async def get_dashboard_stats():
    cursor = db_instance.db.students.find({}, {'_id': 0}).sort('student_id', 1)
    all_students = await cursor.to_list(length=500)
    real_students = [s for s in all_students if not is_judge_student_id(s.get('student_id'))]

    raw_sensory_stats = {}
    raw_dim_stats = {}
    raw_writing_stats = {}
    resource_stats = {}

    for student in real_students:
        for item in student.get('sensory_evaluations') or []:
            raw_sensory_stats[item] = raw_sensory_stats.get(item, 0) + 1

        for item in student.get('dimension_evaluations') or []:
            raw_dim_stats[item] = raw_dim_stats.get(item, 0) + 1

        for key, count in (student.get('resource_click_stats') or {}).items():
            resource_stats[key] = resource_stats.get(key, 0) + int(count or 0)

        for item in student.get('stage5_checks') or []:
            raw_writing_stats[item] = raw_writing_stats.get(item, 0) + 1

    sensory_stats = _normalize_stats(raw_sensory_stats, SENSORY_ALIAS_MAP)
    dim_stats = _normalize_stats(raw_dim_stats, DIMENSION_ALIAS_MAP)
    writing_stats = _normalize_stats(raw_writing_stats, WRITING_ALIAS_MAP)

    return {
        'logged_in_count': len([s for s in real_students if s.get('is_logged_in')]),
        'total_students': len(real_students),
        'table1_sensory': sensory_stats,
        'table2_dimension': dim_stats,
        'table3_resource': resource_stats,
        'table4_writing': writing_stats,
        'resource_completed_count': len([s for s in real_students if s.get('has_viewed_resources') is True]),
        'students_list': real_students,
    }


@router.get('/dashboard/student-detail/{student_id}')
async def get_one_student_detail(student_id: str):
    student = await db_instance.db.students.find_one(_student_id_query(student_id), {'_id': 0})
    if not student:
        return {'error': 'not found'}

    sensory_values = student.get('sensory_evaluations', []) or []
    dimension_values = student.get('dimension_evaluations', []) or []
    stage5_checks = student.get('stage5_checks', []) or []

    stage1_stars = int(student.get('stage1_stars', 0) or 0)
    stage3_stars = int(student.get('stage3_stars', 0) or 0)
    stage5_stars = int(student.get('stage5_stars', 0) or 0)

    # 兜底：历史数据或异常写入时，按当前规则反推每环节星星
    if stage1_stars <= 0:
        stage1_stars = _calc_stage1_from_sensory(sensory_values)
    if stage3_stars <= 0:
        stage3_stars = _calc_stage3_from_dimension(dimension_values)
    if stage5_stars <= 0:
        stage5_stars = _calc_stage5_from_checks(stage5_checks)

    total_stars = int(student.get('total_stars', 0) or 0)
    computed_total = stage1_stars + stage3_stars + stage5_stars
    if total_stars <= 0 or total_stars != computed_total:
        total_stars = computed_total

    return {
        'student_id': student.get('student_id'),
        'student_name': student.get('student_name'),
        'has_viewed_resources': student.get('has_viewed_resources', False),
        'has_claimed_certificate': student.get('has_claimed_certificate', False),
        'pre_plant_1': student.get('pre_plant_1', ''),
        'pre_plant_2': student.get('pre_plant_2', ''),
        'pre_plant_3': student.get('pre_plant_3', ''),
        'pre_record_card': student.get('pre_record_card', ''),
        'sensory_evaluations': sensory_values,
        'dimension_evaluations': dimension_values,
        'stage5_checks': stage5_checks,
        'stage1_stars': stage1_stars,
        'stage3_stars': stage3_stars,
        'stage5_stars': stage5_stars,
        'total_stars': total_stars,
    }


@router.post('/verify-password')
async def verify_teacher_password(req: PasswordReq):
    admin_col = db_instance.db.admin_config
    config = await admin_col.find_one({'key': 'teacher_password'})

    if not config:
        await admin_col.insert_one({'key': 'teacher_password', 'value': '123456'})
        config = await admin_col.find_one({'key': 'teacher_password'})

    input_password = str(req.password).strip()
    stored_password = str(config.get('value', '')).strip()

    if config.get('value') != stored_password:
        await admin_col.update_one({'_id': config['_id']}, {'$set': {'value': stored_password}})

    if input_password == stored_password:
        return {'success': True}
    return {'success': False, 'message': '密码错误'}
