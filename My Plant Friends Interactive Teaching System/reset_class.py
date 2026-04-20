import asyncio
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB config
MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "composition_db"

# Local media directory (offline mode)
LOCAL_MEDIA_DIR = Path(__file__).resolve().parent / "local_media"
PROCESS_MEDIA_STEMS = {"record_card", "draft", "final"}


def clear_process_media_files() -> int:
    """
    Delete only classroom process images in local_media:
    - delete: record_card.*, draft.*, final.*
    - keep:   pre_plant_1/2/3.*
    """
    if not LOCAL_MEDIA_DIR.exists():
        return 0

    removed = 0
    for student_dir in LOCAL_MEDIA_DIR.iterdir():
        if not student_dir.is_dir():
            continue

        for file_path in student_dir.iterdir():
            if not file_path.is_file():
                continue

            if file_path.stem.lower() in PROCESS_MEDIA_STEMS:
                try:
                    file_path.unlink()
                    removed += 1
                except Exception:
                    # Keep reset robust even when a file is locked.
                    pass

    return removed


async def reset_class_data() -> None:
    """
    Reset classroom process data for offline/LAN mode.

    Keep:
    - student_id, student_name
    - pre_plant_1, pre_plant_2, pre_plant_3
    - admin_config

    Reset:
    - login state and stage
    - stage1/stage3/stage5 selections and stars
    - resource click stats and completion flags
    - total stars and certificate flags
    - remove legacy process image URL fields (record_card_img/draft_img/final_img)

    Optional:
    - clear process image files under local_media
    """
    print("Connecting database...")
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]

    confirm = input(
        "Danger: this will reset class process data (keep student basic info and pre-media).\n"
        "Type 'yes' to continue: "
    )
    if confirm.strip().lower() != "yes":
        print("Cancelled.")
        client.close()
        return

    clear_media = (
        input(
            "Also clear local_media process images (record_card/draft/final)?\n"
            "pre_* files will be kept. Type 'yes' to continue: "
        )
        .strip()
        .lower()
        == "yes"
    )

    print("Resetting students process fields...")

    set_fields = {
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
    }

    result = await db.students.update_many({}, {"$set": set_fields})

    print(f"Done. Updated students: {result.modified_count}")
    print("Kept: student_id/student_name and pre_* media fields.")

    if clear_media:
        removed = clear_process_media_files()
        print(f"Cleared local process image files: {removed}")

    client.close()


if __name__ == "__main__":
    asyncio.run(reset_class_data())
