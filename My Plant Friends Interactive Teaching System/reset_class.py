import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# --- 配置区 ---
MONGO_DETAILS = "mongodb://localhost:27017" 
DB_NAME = "composition_db"                       

async def reset_class_data():
    """
    运维级脚本：一键清空全班上课产生的过程数据和状态。
    保留：学号、姓名、教师密码、课前预置的照片和视频。
    """
    print("⚠️ 正在连接数据库...")
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]
    
    # 确认是否真的要重置
    confirm = input("🚨 危险操作：即将清空全班提交的作业、评价和通关记录！\n确认执行请输入 'yes'：")
    if confirm.lower() != 'yes':
        print("已取消重置操作。")
        client.close()
        return

    print("正在清空课堂数据...")
    
    # 执行批量更新
    result = await db.students.update_many(
        {}, # 空条件，代表更新集合中的所有文档
        {"$set": {
            # 1. 状态归零
            "is_logged_in": False,          # 全部强制下线 (大屏格子变灰)
            "current_stage": "0",           # 进度回到起点
            
            # 2. 环节 1-2 数据清空
            "sensory_evaluations": [],      # 清空感官勾选
            "dimension_evaluations": [],    # 清空评价维度勾选
            "record_card_img": "",          # 清空课中修改的记录卡照片
            
            # 3. 环节 3 数据清空
            "draft_img": "",                # 清空初稿照片
            "has_completed_ai": False,      # 清空 AI 批改状态 (大屏环形图归零)
            "ai_feedback_text": "",         # 清空 AI 评语
            
            # 4. 环节 4 数据清空
            "has_viewed_resources": False,  # 清空资源包通关状态 (大屏通关人数归零)
            "resource_click_stats": {},     # 清空资源点击热度
            
            # 5. 环节 5 数据清空 (🏆 奖杯消失的关键)
            "final_img": "",                # 清空最终定稿照片
            
            # --- 注意：绝不触碰 pre_plant_1 等课前预置字段 ---
        }
        }
    )

    print(f"✅ 成功重置了 {result.modified_count} 位学生的课堂数据！")
    print("🎉 大屏上的奖杯、在线状态和统计表格已全部归零。")
    
    

    client.close()

if __name__ == "__main__":
    # 运行异步函数
    asyncio.run(reset_class_data())