JUDGE_MIN_ID = 51
JUDGE_MAX_ID = 70
# Configure the 6 source students used by judge slots (51-70), in cycle order.
# Example: 51->first, 52->second ... 56->sixth, 57->first ...
# Update this list to the 6 students you selected.
JUDGE_SOURCE_CYCLE_IDS = ['08', '23', '26', '30', '35', '39']


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

    cycle = [to_student_id_text(v) for v in JUDGE_SOURCE_CYCLE_IDS if str(v or '').strip()]
    if not cycle:
        return sid

    value = int(sid)
    idx = (value - JUDGE_MIN_ID) % len(cycle)
    return cycle[idx]
