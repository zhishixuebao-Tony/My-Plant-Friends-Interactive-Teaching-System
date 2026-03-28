'''import dashscope
from app.core.config import settings

dashscope.api_key = settings.DASHSCOPE_API_KEY

def generate_ai_evaluation(student_data: dict) -> str:
    """生成模块五的个性化 AI 评价"""
    prompt = f"""
    你是一位小学科学老师。根据该学生本节课的数据，写一段50字左右的鼓励性个性化评价。
    数据如下：共上传了{student_data['uploads']}份记录，获得了{student_data['flowers']}朵花/星星，
    互评活跃度为{student_data['interactions']}次。
    请用活泼可爱、充满鼓励的语气。
    """
    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_turbo,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.output.choices[0]['message']['content']'''
# 测试版：移除 dashscope 的真实调用
# import dashscope
from app.core.config import settings

def generate_ai_evaluation(student_data: dict) -> str:
    """[本地测试版 Mock] 模拟生成 AI 个性化评价"""
    
    print(f"🤖 [Mock AI] 正在为学生生成假评语，参考数据: {student_data}")
    
    # 直接返回一句固定的话，让前端能展示出效果即可
    mock_comment = (
        f"【AI模拟评语】这位同学太棒啦！"
        f"你上传了 {student_data.get('uploads', 0)} 份记录，"
        f"获得了 {student_data.get('flowers', 0)} 朵小红花，"
        f"继续保持对大自然的好奇心哦！"
    )
    return mock_comment