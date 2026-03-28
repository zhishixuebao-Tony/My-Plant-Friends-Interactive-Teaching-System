import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def create_mock_class():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["composition_db"]
    
    print("正在清理并初始化全班 50 名学生数据...")
    await db.students.delete_many({}) # 清空旧数据

    for i in range(1, 51):
        sid = f"{i:02d}"
        # 模拟不同的学生进度
        stage = "0_login"
        if i < 10: stage = "6_completed" # 前10名已完成
        elif i < 25: stage = "3_draft_ai" # 中间在写初稿
        
        student = {
            "student_id": sid,
            "student_name": f"学生{sid}",
            "is_logged_in": True if i < 40 else False,
            "current_stage": stage,
            "sensory_evaluations": ["看了看", "摸了摸"] if i < 30 else [],
            "record_card_img": "https://via.placeholder.com/300" if i < 15 else None,
            "final_img": "https://via.placeholder.com/400" if i < 10 else None,
            "ai_feedback_text": "写得真不错！" if i < 10 else ""
        }
        await db.students.insert_one(student)
    
    print("✅ 50名学生模拟数据创建成功！")

if __name__ == "__main__":
    asyncio.run(create_mock_class())