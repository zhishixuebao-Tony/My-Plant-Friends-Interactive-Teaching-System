import argparse
import asyncio
import re
from pathlib import Path
from urllib.parse import quote

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "composition_db"
LOCAL_MEDIA_DIR = Path(__file__).resolve().parent / "local_media"

PRE_FIELDS = ["pre_record_card", "pre_plant_1", "pre_plant_2", "pre_plant_3"]
WINDOWS_INVALID_CHARS_RE = re.compile(r'[\\/:*?"<>|]+')
SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def safe_student_id(raw: str) -> str:
    return SAFE_ID_RE.sub("_", str(raw or "").strip()) or "unknown"


def safe_folder_name(raw: str, fallback: str) -> str:
    value = WINDOWS_INVALID_CHARS_RE.sub("_", str(raw or "").strip())
    value = re.sub(r"\s+", " ", value).strip()
    return value or fallback


def student_folder(student_id: str, student_name: str) -> str:
    sid = safe_student_id(student_id)
    name = safe_folder_name(student_name, "未命名")
    return safe_folder_name(f"{sid}_{name}", sid)


def find_file(folder_path: Path, stem: str) -> Path | None:
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = folder_path / f"{stem}.{ext}"
        if p.exists() and p.is_file():
            return p
    return None


def to_media_url(folder: str, file_name: str) -> str:
    return f"/local-media/{quote(folder)}/{quote(file_name)}"


async def rebuild(dry_run: bool, clear_missing: bool) -> None:
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]
    students = await db.students.find({}, {"_id": 0, "student_id": 1, "student_name": 1, **{k: 1 for k in PRE_FIELDS}}).to_list(length=5000)

    total = len(students)
    updated_docs = 0
    found_files = 0
    missing_files = 0

    for stu in students:
        sid = str(stu.get("student_id", "")).strip()
        name = str(stu.get("student_name", "")).strip()
        if not sid or not name:
            continue

        folder = student_folder(sid, name)
        folder_path = LOCAL_MEDIA_DIR / folder
        changes = {}

        for field in PRE_FIELDS:
            file_path = find_file(folder_path, field)
            if file_path:
                new_url = to_media_url(folder, file_path.name)
                if str(stu.get(field) or "").strip() != new_url:
                    changes[field] = new_url
                found_files += 1
            else:
                missing_files += 1
                if clear_missing and str(stu.get(field) or "").strip():
                    changes[field] = ""

        if changes:
            print(f"[UPDATE] sid={sid} name={name} fields={list(changes.keys())}")
            if not dry_run:
                sid_norm = sid.zfill(2)
                query = {"student_id": {"$in": [sid, sid_norm, str(int(sid_norm)), int(sid_norm)]}}
                await db.students.update_many(query, {"$set": changes})
            updated_docs += 1

    print("==== Rebuild Summary ====")
    print(f"Total students: {total}")
    print(f"Updated documents: {updated_docs}")
    print(f"Found local pre-files: {found_files}")
    print(f"Missing pre-files: {missing_files}")
    print(f"Dry run: {dry_run}")
    print(f"Clear missing: {clear_missing}")
    client.close()


def main():
    parser = argparse.ArgumentParser(description="Rebuild pre media URLs from local_media folder structure.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing DB.")
    parser.add_argument("--clear-missing", action="store_true", help="Clear DB fields when local file is missing.")
    args = parser.parse_args()
    asyncio.run(rebuild(dry_run=args.dry_run, clear_missing=args.clear_missing))


if __name__ == "__main__":
    main()
