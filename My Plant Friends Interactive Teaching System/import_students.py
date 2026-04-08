import asyncio
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# MongoDB 配置（与 reset_class.py 一致）
MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "composition_db"


def validate_student_data(row):
    """
    验证学生数据，确保必需字段存在
    返回验证结果和清理后的数据
    
    注意：
    - student_id 和 student_name 是必需字段，缺少则跳过该行
    - pre_record_card, pre_plant_1, pre_plant_2, pre_plant_3 是可选字段
      如果Excel中为空，则存入数据库时为 None
    """
    # 必需字段：student_id 和 student_name
    student_id = row.get('student_id')
    student_name = row.get('student_name')
    
    if pd.isna(student_id) or pd.isna(student_name):
        return False, None, f"缺少必需字段，跳过该行: student_id={student_id}, student_name={student_name}"
    
    # 清理数据：将NaN转换为None，去除字符串空格
    clean_data = {
        'student_id': str(student_id).strip(),
        'student_name': str(student_name).strip(),
    }
    
    # 可选字段：课前素材 - 如果Excel中为空，则存入 None
    optional_fields = ['pre_record_card', 'pre_plant_1', 'pre_plant_2', 'pre_plant_3']
    for field in optional_fields:
        value = row.get(field)
        if pd.isna(value):
            clean_data[field] = None  # 缺失的字段设为空值
        else:
            clean_data[field] = str(value).strip()
    
    return True, clean_data, "数据有效"


async def import_students_from_excel(file_path):
    """
    从Excel文件导入学生数据到MongoDB
    
    Args:
        file_path: Excel文件路径
        
    Excel文件应包含以下列（列名需完全匹配）：
    - student_id: 学生ID（必需）
    - student_name: 学生姓名（必需）
    - pre_record_card: 课前记录卡图片URL（可选）
    - pre_plant_1: 课前植物照片1 URL（可选）
    - pre_plant_2: 课前植物照片2 URL（可选）
    - pre_plant_3: 课前植物照片3 URL（可选）
    """
    print("正在连接数据库...")
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]
    
    try:
        # 读取Excel文件
        print(f"正在读取Excel文件: {file_path}")
        df = pd.read_excel(file_path)
        
        # 检查必需列是否存在
        required_columns = ['student_id', 'student_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"错误：Excel文件中缺少以下必需列: {missing_columns}")
            print(f"文件中的列: {list(df.columns)}")
            return
        
        # 去除重复的学生ID，防止重复导入
        print("正在检查并去除重复的学生ID...")
        seen_ids = set()
        unique_rows = []
        
        for idx, row in df.iterrows():
            student_id = row.get('student_id')
            if pd.isna(student_id):
                continue
            
            student_id_str = str(student_id).strip()
            if student_id_str not in seen_ids:
                seen_ids.add(student_id_str)
                unique_rows.append(row)
            else:
                print(f"警告：跳过重复的学生ID: {student_id_str} (第 {idx+2} 行)")
        
        df_unique = pd.DataFrame(unique_rows)
        total_rows = len(df_unique)
        print(f"去除重复后，找到 {total_rows} 行唯一数据")
        
        # 询问用户确认
        confirm = input(
            f"\n准备导入 {total_rows} 名学生数据到数据库 {DB_NAME}\n"
            "确认执行请输入 'yes': "
        )
        if confirm.strip().lower() != "yes":
            print("已取消导入。")
            return
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        # 存储前5名学生的数据，用于创建评委位
        first_five_students = []
        
        print("\n开始导入学生数据...")
        for idx, row in df_unique.iterrows():
            try:
                # 验证数据
                is_valid, clean_data, message = validate_student_data(row)
                
                if not is_valid:
                    print(f"第 {idx+2} 行跳过: {message}")
                    skip_count += 1
                    continue
                
                student_id = clean_data['student_id']
                
                # 如果是前5名学生，保存数据用于评委位
                if len(first_five_students) < 5:
                    first_five_students.append(clean_data.copy())
                
                # 构建完整的学生文档
                student_doc = {
                    **clean_data,
                    # 初始化过程数据字段（与reset_class.py保持一致）
                    'is_logged_in': False,
                    'current_stage': '0',
                    'sensory_evaluations': [],
                    'stage1_stars': 0,
                    'dimension_evaluations': [],
                    'stage3_stars': 0,
                    'has_viewed_resources': False,
                    'resource_click_stats': {},
                    'stage5_checks': [],
                    'stage5_stars': 0,
                    'total_stars': 0,
                    'has_claimed_certificate': False,
                    'has_completed_ai': False,
                    'ai_feedback_text': '',
                    'last_active_time': None,
                }
                
                # 检查是否已存在相同student_id的学生
                existing = await db.students.find_one({'student_id': student_id})
                
                if existing:
                    # 更新现有记录，只更新基础信息和课前素材，保留过程数据
                    update_data = {
                        'student_name': clean_data['student_name']
                    }
                    # 只更新非空的课前素材字段
                    for field in ['pre_record_card', 'pre_plant_1', 'pre_plant_2', 'pre_plant_3']:
                        if clean_data[field] is not None:
                            update_data[field] = clean_data[field]
                    
                    await db.students.update_one(
                        {'student_id': student_id},
                        {'$set': update_data}
                    )
                    print(f"第 {idx+2} 行更新: 学生 {student_id} - {clean_data['student_name']}")
                else:
                    # 插入新记录
                    await db.students.insert_one(student_doc)
                    print(f"第 {idx+2} 行新增: 学生 {student_id} - {clean_data['student_name']}")
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"第 {idx+2} 行错误: {str(e)}")
                continue
        
        # 创建评委位（student_id: 51-55）
        print("\n正在创建评委位（student_id: 51-55）...")
        judge_count = 0
        for i, student_data in enumerate(first_five_students):
            if i >= 5:  # 确保最多5个评委位
                break
                
            try:
                judge_id = str(51 + i)  # 51, 52, 53, 54, 55
                judge_name = f"评委{i+1} ({student_data['student_name']})"
                
                # 构建评委文档（使用对应学生的课前素材）
                judge_doc = {
                    'student_id': judge_id,
                    'student_name': judge_name,
                    'pre_record_card': student_data.get('pre_record_card'),
                    'pre_plant_1': student_data.get('pre_plant_1'),
                    'pre_plant_2': student_data.get('pre_plant_2'),
                    'pre_plant_3': student_data.get('pre_plant_3'),
                    # 初始化过程数据字段
                    'is_logged_in': False,
                    'current_stage': '0',
                    'sensory_evaluations': [],
                    'stage1_stars': 0,
                    'dimension_evaluations': [],
                    'stage3_stars': 0,
                    'has_viewed_resources': False,
                    'resource_click_stats': {},
                    'stage5_checks': [],
                    'stage5_stars': 0,
                    'total_stars': 0,
                    'has_claimed_certificate': False,
                    'has_completed_ai': False,
                    'ai_feedback_text': '',
                    'last_active_time': None,
                }
                
                # 检查评委位是否已存在
                existing_judge = await db.students.find_one({'student_id': judge_id})
                
                if existing_judge:
                    # 更新现有评委位
                    await db.students.update_one(
                        {'student_id': judge_id},
                        {'$set': {
                            'student_name': judge_name,
                            'pre_record_card': student_data.get('pre_record_card'),
                            'pre_plant_1': student_data.get('pre_plant_1'),
                            'pre_plant_2': student_data.get('pre_plant_2'),
                            'pre_plant_3': student_data.get('pre_plant_3'),
                        }}
                    )
                    print(f"评委位更新: {judge_id} - {judge_name}")
                else:
                    # 插入新评委位
                    await db.students.insert_one(judge_doc)
                    print(f"评委位新增: {judge_id} - {judge_name}")
                
                judge_count += 1
                
            except Exception as e:
                print(f"创建评委位 {51+i} 时出错: {str(e)}")
                continue
        
        # 输出统计结果
        print(f"\n导入完成！")
        print(f"成功导入学生数据: {success_count} 行")
        print(f"跳过: {skip_count} 行（数据无效）")
        print(f"错误: {error_count} 行")
        print(f"创建评委位: {judge_count} 个（ID: 51-55）")
        
        total_imported = success_count + judge_count
        print(f"总计新增/更新记录: {total_imported} 条")
        
        if success_count > 0 or judge_count > 0:
            print(f"\n可以运行以下命令查看导入的学生数据:")
            print(f"1. 进入MongoDB shell: mongosh composition_db")
            print(f"2. 查看所有学生数据: db.students.find().sort({{'student_id': 1}}).pretty()")
            print(f"3. 查看评委位数据: db.students.find({{student_id: {{$in: ['51','52','53','54','55']}}}}).pretty()")
            print(f"4. 统计学生数量: db.students.countDocuments()")
            print(f"\n注意：评委位（51-55）使用前5名学生的课前素材数据创建")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
    except pd.errors.EmptyDataError:
        print("错误：Excel文件为空")
    except Exception as e:
        print(f"导入过程中发生错误: {str(e)}")
    finally:
        client.close()


def main():
    """主函数，处理命令行参数"""
    if len(sys.argv) != 2:
        print("使用方法: python import_students.py <Excel文件路径>")
        print("例如: python import_students.py students.xlsx")
        print("\nExcel文件应放在项目根目录下（与import_students.py同一目录）")
        print("或者提供完整路径")
        return
    
    file_path = sys.argv[1]
    
    # 如果是相对路径，转换为绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.path.dirname(__file__), file_path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在")
        print("请将Excel文件放在正确位置，或提供完整路径")
        return
    
    # 运行导入任务
    asyncio.run(import_students_from_excel(file_path))


if __name__ == "__main__":
    main()