from fastapi import APIRouter
from pydantic import BaseModel

from app.db.mongodb import db_instance


class PasswordReq(BaseModel):
    password: str


router = APIRouter()


SENSORY_ALIAS_MAP = {
    '???': '???',
    '???': '???',
    '???': '???',
    '???': '???',
    '???': '???',
    '???': '???',
    '???': '???',
    '???': '???',
    '???': '???',
    '??': '??',
}

DIMENSION_ALIAS_MAP = {
    '我暂时没有新的发现': '我暂时没有新的发现',
    '我暂时没有新的发现。': '我暂时没有新的发现',
    '我已经有了新的发现：（1）有以前没观察到的': '我已经有了新的发现：（1）有以前没观察到的',
    '评价一：能真实记录植物特点': '我已经有了新的发现：（1）有以前没观察到的',
    '评价一': '我已经有了新的发现：（1）有以前没观察到的',
    '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价二：能描写自己的感受': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价二：能描写出自己的感受': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价二': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价三：书写认真、字迹工整': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价三': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
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


@router.get('/dashboard/statistics')
async def get_dashboard_stats():
    cursor = db_instance.db.students.find({}, {'_id': 0}).sort('student_id', 1)
    all_students = await cursor.to_list(length=100)

    sensory_pipeline = [
        {'$unwind': '$sensory_evaluations'},
        {'$group': {'_id': '$sensory_evaluations', 'count': {'$sum': 1}}},
    ]
    s_cursor = db_instance.db.students.aggregate(sensory_pipeline)
    raw_sensory_stats = {item['_id']: item['count'] async for item in s_cursor}
    sensory_stats = _normalize_stats(raw_sensory_stats, SENSORY_ALIAS_MAP)

    dim_pipeline = [
        {'$unwind': '$dimension_evaluations'},
        {'$group': {'_id': '$dimension_evaluations', 'count': {'$sum': 1}}},
    ]
    d_cursor = db_instance.db.students.aggregate(dim_pipeline)
    raw_dim_stats = {item['_id']: item['count'] async for item in d_cursor}
    dim_stats = _normalize_stats(raw_dim_stats, DIMENSION_ALIAS_MAP)

    res_pipeline = [
        {'$project': {'stats': {'$objectToArray': '$resource_click_stats'}}},
        {'$unwind': '$stats'},
        {'$group': {'_id': '$stats.k', 'count': {'$sum': '$stats.v'}}},
    ]
    r_cursor = db_instance.db.students.aggregate(res_pipeline)
    resource_stats = {item['_id']: item['count'] async for item in r_cursor}

    # 添加写作目标统计
    writing_pipeline = [
        {'$unwind': '$stage5_checks'},
        {'$group': {'_id': '$stage5_checks', 'count': {'$sum': 1}}},
    ]
    w_cursor = db_instance.db.students.aggregate(writing_pipeline)
    raw_writing_stats = {item['_id']: item['count'] async for item in w_cursor}
    writing_stats = _normalize_stats(raw_writing_stats, WRITING_ALIAS_MAP)

    res_completed_count = len([s for s in all_students if s.get('has_viewed_resources') is True])

    return {
        'logged_in_count': len([s for s in all_students if s.get('is_logged_in')]),
        'total_students': len(all_students),
        'table1_sensory': sensory_stats,
        'table2_dimension': dim_stats,
        'table3_resource': resource_stats,
        'table4_writing': writing_stats,
        'table5_ai_count': len([s for s in all_students if s.get('has_completed_ai')]),
        'resource_completed_count': res_completed_count,
        'students_list': all_students,
    }


@router.get('/dashboard/student-detail/{student_id}')
async def get_one_student_detail(student_id: str):
    student = await db_instance.db.students.find_one(_student_id_query(student_id), {'_id': 0})
    if not student:
        return {'error': 'not found'}

    return {
        'student_id': student.get('student_id'),
        'student_name': student.get('student_name'),
        'has_completed_ai': student.get('has_completed_ai', False),
        'has_viewed_resources': student.get('has_viewed_resources', False),
        'ai_feedback_text': student.get('ai_feedback_text', ''),
        'pre_record_card': student.get('pre_record_card', ''),
        'pre_plant_1': student.get('pre_plant_1', ''),
        'pre_plant_2': student.get('pre_plant_2', ''),
        'pre_plant_3': student.get('pre_plant_3', ''),
        'record_card_img': student.get('record_card_img', ''),
        'draft_img': student.get('draft_img', ''),
        'final_img': student.get('final_img', ''),
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
    return {'success': False, 'message': '??????????'}
