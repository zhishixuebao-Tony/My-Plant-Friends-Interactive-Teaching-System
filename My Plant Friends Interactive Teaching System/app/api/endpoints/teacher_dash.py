from fastapi import APIRouter
from app.db.mongodb import db_instance
from datetime import datetime, timedelta
from pydantic import BaseModel

class PasswordReq(BaseModel):
    password: str

router = APIRouter()

@router.get("/dashboard/statistics")
async def get_dashboard_stats():
     # 1. 【核心逻辑】自动清理离线学生 (超过 20 秒没发心跳，视为断线)
    timeout_threshold = datetime.now() - timedelta(seconds=20)
    await db_instance.db.students.update_many(
        {"is_logged_in": True, "last_active_time": {"$lt": timeout_threshold}},
        {"$set": {"is_logged_in": False}}  # 强行置为离线，但不清空进度
    )

    """大屏核心数据：登录人数、四大数据统计表格、全班矩阵列表"""
    
    # 1. 获取全班基础列表
    cursor = db_instance.db.students.find({}, {"_id": 0}).sort("student_id", 1)
    all_students = await cursor.to_list(length=100)
    
    # 2. 统计一：环节1的感官勾选人数 (看了看, 摸了摸等)
    sensory_pipeline = [
        {"$unwind": "$sensory_evaluations"},
        {"$group": {"_id": "$sensory_evaluations", "count": {"$sum": 1}}}
    ]
    s_cursor = db_instance.db.students.aggregate(sensory_pipeline)
    sensory_stats = {item["_id"]: item["count"] async for item in s_cursor}
    
    # 3. 统计二：环节2的记录卡评价维度 (评价一, 评价二等)
    dim_pipeline = [
        {"$unwind": "$dimension_evaluations"},
        {"$group": {"_id": "$dimension_evaluations", "count": {"$sum": 1}}}
    ]
    d_cursor = db_instance.db.students.aggregate(dim_pipeline)
    dim_stats = {item["_id"]: item["count"] async for item in d_cursor}

    # 4. 统计三：魔法资源包点击量 (资源1, 资源2)
    res_pipeline = [
        {"$project": {"stats": {"$objectToArray": "$resource_click_stats"}}},
        {"$unwind": "$stats"},
        {"$group": {"_id": "$stats.k", "count": {"$sum": "$stats.v"}}}
    ]
    r_cursor = db_instance.db.students.aggregate(res_pipeline)
    resource_stats = {item["_id"]: item["count"] async for item in r_cursor}

    # 5. 统计四：AI评价使用人数
    ai_used_count = len([s for s in all_students if s.get("has_completed_ai", False)])

     # 统计五：魔法资源包完成人数
    res_completed_count = len([s for s in all_students if s.get("has_viewed_resources") == True])   

    # 4. 汇总返回
    return {
        "logged_in_count": len([s for s in all_students if s.get("is_logged_in")]),
        "total_students": len(all_students),
        "table1_sensory": sensory_stats,
        "table2_dimension": dim_stats,
        "table3_resource": resource_stats,
        "table4_ai_count": len([s for s in all_students if s.get("has_completed_ai")]),
        # 确保这个 key 名简单明确
        "resource_completed_count": res_completed_count, 
        "students_list": all_students
    }

@router.get("/dashboard/student-detail/{student_id}")
async def get_one_student_detail(student_id: str):
    """当老师点击某人时，单独获取该生的详情档案"""
    student = await db_instance.db.students.find_one({"student_id": student_id}, {"_id": 0})
    if not student:
        return {"error": "not found"}
    return student

@router.post("/verify-password")
async def verify_teacher_password(req: PasswordReq):
    admin_col = db_instance.db.admin_config
    config = await admin_col.find_one({"key": "teacher_password"})
    
    if config and req.password == config["value"]:
        return {"success": True}
    else:
        return {"success": False, "message": "密码错误，请重新输入"}