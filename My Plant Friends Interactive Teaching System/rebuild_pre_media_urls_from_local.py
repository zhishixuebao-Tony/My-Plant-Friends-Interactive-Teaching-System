import argparse
import asyncio
import re
from pathlib import Path
from urllib.parse import quote

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "composition_db"
LOCAL_MEDIA_DIR = Path(__file__).resolve().parent / "local_media"

PRE_FIELDS = ["pre_plant_1", "pre_plant_2", "pre_plant_3", "pre_record_card"]
WINDOWS_INVALID_CHARS_RE = re.compile(r'[\\/:*?"<>|]+')
SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def safe_student_id(raw: str) -> str:
    return SAFE_ID_RE.sub("_", str(raw or "").strip()) or "unknown"


def safe_folder_name(raw: str, fallback: str) -> str:
    value = WINDOWS_INVALID_CHARS_RE.sub("_", str(raw or "").strip())
    value = re.sub(r"\s+", " ", value).strip()
    return value or fallback


def sid_norm(raw_sid: str) -> str:
    return str(raw_sid or "").strip().zfill(2)


def sid_query_values(sid_text: str) -> list:
    sid = sid_norm(sid_text)
    return [sid, str(int(sid)), int(sid)]


def is_non_judge_sid(sid: str) -> bool:
    return sid.isdigit() and int(sid) < 51


def default_student_doc(student_id: str, student_name: str) -> dict:
    return {
        "student_id": sid_norm(student_id),
        "student_name": student_name,
        "is_logged_in": False,
        "current_stage": "0",
        "sensory_evaluations": [],
        "stage1_stars": 0,
        "dimension_evaluations": [],
        "stage3_stars": 0,
        "has_viewed_resources": False,
        "resource_click_stats": {},
        "stage5_checks": [],
        "stage5_stars": 0,
        "total_stars": 0,
        "has_claimed_certificate": False,
        "last_active_time": None,
        "pre_plant_1": "",
        "pre_plant_2": "",
        "pre_plant_3": "",
        "pre_record_card": "",
    }


def student_folder(student_id: str, student_name: str) -> str:
    sid = safe_student_id(student_id)
    name = safe_folder_name(student_name, "unnamed")
    return safe_folder_name(f"{sid}_{name}", sid)


def resolve_student_folder_path(student_id: str, student_name: str) -> tuple[str, Path]:
    exact_folder = student_folder(student_id, student_name)
    exact_path = LOCAL_MEDIA_DIR / exact_folder
    if exact_path.exists() and exact_path.is_dir():
        return exact_folder, exact_path

    sid = safe_student_id(student_id)
    candidates = sorted([p for p in LOCAL_MEDIA_DIR.glob(f"{sid}_*") if p.is_dir()], key=lambda p: p.name)
    if candidates:
        picked = candidates[0]
        return picked.name, picked

    return exact_folder, exact_path


def find_file(folder_path: Path, stem: str) -> Path | None:
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = folder_path / f"{stem}.{ext}"
        if p.exists() and p.is_file():
            return p
    return None


def to_media_url(folder: str, file_name: str) -> str:
    return f"/local-media/{quote(folder)}/{quote(file_name)}"


def collect_local_name_map() -> dict[str, str]:
    result = {}
    if not LOCAL_MEDIA_DIR.exists():
        return result

    for p in LOCAL_MEDIA_DIR.iterdir():
        if not p.is_dir() or "_" not in p.name:
            continue
        sid_part, stu_name = p.name.split("_", 1)
        sid = sid_norm(sid_part)
        stu_name = str(stu_name).strip()
        if sid.isdigit() and stu_name:
            result.setdefault(sid, stu_name)
    return result


async def load_non_judge_map(db) -> dict[str, dict]:
    docs = await db.students.find({}, {"_id": 0}).to_list(length=5000)
    result = {}
    for d in docs:
        sid = sid_norm(d.get("student_id", ""))
        if is_non_judge_sid(sid):
            result[sid] = d
    return result


async def rebuild(dry_run: bool, sync_student_names: bool, student_max: int | None) -> None:
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]

    local_name_map = collect_local_name_map()
    non_judge_map = await load_non_judge_map(db)

    max_from_local = max([int(k) for k in local_name_map.keys()], default=0)
    max_from_db = max([int(k) for k in non_judge_map.keys()], default=0)
    max_sid = student_max if student_max and student_max > 0 else max(max_from_local, max_from_db, 1)

    updated_docs = 0
    inserted_slots = 0
    renamed_students = 0
    found_files = 0
    missing_files = 0

    for sid_int in range(1, max_sid + 1):
        sid = str(sid_int).zfill(2)
        current = non_judge_map.get(sid)
        current_name = str((current or {}).get("student_name") or "").strip()
        local_name = local_name_map.get(sid)

        # Name policy:
        # - If local folder exists, use local folder name.
        # - If local folder is missing, use placeholder "学生+学号".
        target_name = local_name or f"学生{sid_int}"

        changes = {}
        if sync_student_names and target_name and target_name != current_name:
            changes["student_name"] = target_name
            if current_name:
                renamed_students += 1

        folder, folder_path = resolve_student_folder_path(sid, target_name)

        final_doc = dict(current or default_student_doc(sid, target_name))
        if "student_name" in changes:
            final_doc["student_name"] = changes["student_name"]

        for field in PRE_FIELDS:
            file_path = find_file(folder_path, field)
            if file_path:
                new_url = to_media_url(folder, file_path.name)
                if str((current or {}).get(field) or "").strip() != new_url:
                    changes[field] = new_url
                final_doc[field] = new_url
                found_files += 1
            else:
                missing_files += 1
                # Pure LAN mode rule: any missing pre-file should map to empty value,
                # so stale historical URLs are always cleaned.
                if str((current or {}).get(field) or "").strip():
                    changes[field] = ""
                final_doc[field] = ""

        if current is None:
            inserted_slots += 1
            if dry_run:
                print(f"[INSERT SLOT] sid={sid} name={target_name}")
            else:
                payload = default_student_doc(sid, target_name)
                payload.update({k: final_doc.get(k, "") for k in PRE_FIELDS})
                await db.students.insert_one(payload)
            updated_docs += 1
        elif changes:
            print(f"[UPDATE] sid={sid} name={current_name or target_name} fields={list(changes.keys())}")
            if not dry_run:
                await db.students.update_many({"student_id": {"$in": sid_query_values(sid)}}, {"$set": changes})
            updated_docs += 1

    print("==== Rebuild Summary ====")
    print(f"Total non-judge slots (01..{str(max_sid).zfill(2)}): {max_sid}")
    print(f"Updated/inserted documents: {updated_docs}")
    print(f"Inserted missing slots: {inserted_slots}")
    print(f"Renamed students from local folders: {renamed_students}")
    print(f"Found local pre-files: {found_files}")
    print(f"Missing pre-files: {missing_files}")
    print(f"Dry run: {dry_run}")
    print("Clear missing: True (default in pure LAN mode)")
    print(f"Sync student names: {sync_student_names}")

    client.close()


def main():
    parser = argparse.ArgumentParser(description="Rebuild pre media URLs from local_media folder structure.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing DB.")
    parser.add_argument("--sync-student-names", action="store_true", help="Sync student_name from local_media folder names.")
    parser.add_argument("--clear-missing", action="store_true", help="Deprecated. Missing pre_* files are always cleared.")
    parser.add_argument("--student-max", type=int, default=None, help="Force non-judge slots range 01..N.")
    args = parser.parse_args()

    asyncio.run(
        rebuild(
            dry_run=args.dry_run,
            sync_student_names=args.sync_student_names,
            student_max=args.student_max,
        )
    )


if __name__ == "__main__":
    main()
