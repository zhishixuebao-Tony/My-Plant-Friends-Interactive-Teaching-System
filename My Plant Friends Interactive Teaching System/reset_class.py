import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB 配置
MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "composition_db"


async def reset_class_data():
    """
    一键重置课堂过程数据（不删除学生基础资料）。

    会保留：
    - student_id, student_name
    - pre_record_card, pre_plant_1, pre_plant_2, pre_plant_3（课前素材）
    - admin_config（教师密码配置）

    会重置（保留字段不动）：
    - 登录状态与进度
    - 环节 1（感官观察）的勾选与星数
    - 环节 3（记录卡）的勾选与星数
    - 环节 5（试写环节）的勾选与星数
    - 资源包点击统计与完成状态
    - 证书领取状态与总星数
    - 课堂过程状态与统计字段（AI 兼容字段）
    - 旧的拍照上传产物字段会直接删除
    """
    print("正在连接数据库...")
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]

    confirm = input(
        "危险操作：将重置全班课堂过程数据（保留学号姓名与课前素材）。\n"
        "确认执行请输入 'yes'："
    )
    if confirm.strip().lower() != "yes":
        print("已取消重置。")
        client.close()
        return

    print("正在重置 students 集合中的课堂数据...")

    set_fields = {
        # 0. 登录与进度
        "is_logged_in": False,
        "current_stage": "0",

        # 1. 环节 1：感官观察（观察方法统计）
        "sensory_evaluations": [],
        "stage1_stars": 0,

        # 2. 环节 3：记录卡（新发现统计）
        "dimension_evaluations": [],
        "stage3_stars": 0,

        # 3. 资源包与相关统计（资源点击统计）
        "has_viewed_resources": False,
        "resource_click_stats": {},

        # 4. 环节 5：试写与证书（写作目标达成统计）
        "stage5_checks": [],
        "stage5_stars": 0,
        "total_stars": 0,
        "has_claimed_certificate": False,

        # 5. 兼容历史字段（如仍存在则一起清空）
        "has_completed_ai": False,
        "ai_feedback_text": "",
        "last_active_time": None,
    }

    # 历史残留字段与已停用字段：直接删除
    unset_fields = {
        "stage_total_stars": "",
        "finalStars": "",
        "totalStars": "",
        "final_stars": "",
        "record_card_img": "",
        "draft_img": "",
        "final_img": "",
    }

    result = await db.students.update_many({}, {"$set": set_fields, "$unset": unset_fields})

    print(f"重置完成：共更新 {result.modified_count} 位学生。")
    print("说明：学号、姓名、课前记录卡与课前植物照片均已保留。")

    client.close()


if __name__ == "__main__":
    asyncio.run(reset_class_data())
