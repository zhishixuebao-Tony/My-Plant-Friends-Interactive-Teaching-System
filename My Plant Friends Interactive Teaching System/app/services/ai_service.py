import httpx
import json

# 配置你的真实 Token 和 ID
COZE_PAT_TOKEN = "pat_AYkP1iVcd7M1Wib2v2CzDFMAdQrYHXqHpK8gN9fkTBiTTjd9KOuuMYCFuIUKaCsy"
WORKFLOW_ID = "7622502061725253673"
COZE_API_URL = "https://api.coze.cn/v1/workflow/run"

async def get_coze_workflow_feedback(img_url: str, student_name: str):
    """
    专门调用 Coze 工作流获取批改建议
    """
    headers = {
        "Authorization": f"Bearer {COZE_PAT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "workflow_id": WORKFLOW_ID,
        "parameters": {
            "IMG": img_url,
            "user_name": student_name
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(COZE_API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    # 返回的是工作流的 data 结果
                    return str(res_json.get("data"))
            print(f"❌ AI 接口返回异常: {response.text}")
            return None
        except Exception as e:
            print(f"❌ AI 请求发生异常: {e}")
            return None