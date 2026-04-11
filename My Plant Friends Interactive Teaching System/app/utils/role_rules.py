JUDGE_MIN_ID = 51
JUDGE_MAX_ID = 70
JUDGE_MAP_SOURCE_MIN_ID = 1


def to_student_id_text(raw_student_id: str) -> str:
    return str(raw_student_id or '').strip().zfill(2)


def is_judge_student_id(raw_student_id) -> bool:
    sid = to_student_id_text(raw_student_id)
    if not sid.isdigit():
        return False
    value = int(sid)
    return JUDGE_MIN_ID <= value <= JUDGE_MAX_ID


def map_judge_to_source_student_id(raw_student_id: str) -> str:
    sid = to_student_id_text(raw_student_id)
    if not sid.isdigit():
        return sid
    if not is_judge_student_id(sid):
        return sid

    value = int(sid)
    mapped = JUDGE_MAP_SOURCE_MIN_ID + (value - JUDGE_MIN_ID)
    return str(mapped).zfill(2)