# Coze 智能体集成指南

本文档说明如何将 Coze 智能体集成到"我的植物朋友互动教学系统"中，用于生成 AI 作文批改评语。

## 已完成的修改

1. **配置扩展** (`app/core/config.py`)
   - 新增 `COZE_API_KEY`、`COZE_AGENT_ID`、`COZE_API_ENDPOINT` 配置项
   - 支持从环境变量读取配置

2. **Coze 服务层** (`app/services/coze_service.py`)
   - 实现了 `call_coze_agent()` 函数，用于调用 Coze API
   - 支持异步 HTTP 请求（使用 httpx）
   - 内置优雅降级：配置不完整或 API 调用失败时使用模拟评语
   - 提供默认提示词模板，可根据学生数据生成个性化评语

3. **AI 端点更新** (`app/api/endpoints/ai_agent.py`)
   - 修改 `/stage3/submit-draft-ai` 接口，集成 Coze 智能体
   - 新增健康检查接口 `/health`
   - 优化错误处理和数据准备逻辑

4. **依赖更新** (`requirements.txt`)
   - 添加 `httpx>=0.24.0` 依赖

## 配置步骤

### 步骤 1：获取 Coze API 凭证

1. 登录 [Coze 开放平台](https://www.coze.cn/open)
2. 创建应用或使用现有应用
3. 获取以下信息：
   - **API Key**: 在应用设置中生成
   - **Agent ID**: 智能体的唯一标识符

### 步骤 2：配置环境变量

在 `.env` 文件中添加以下配置：

```env
# Coze API 配置
COZE_API_KEY="your-coze-api-key-here"
COZE_AGENT_ID="your-agent-id-here"
# 可选：自定义 API 端点（默认为官方端点）
# COZE_API_ENDPOINT="https://api.coze.cn/v1/chat/completions"
```

### 步骤 3：安装依赖

```bash
# 安装新增依赖
pip install httpx>=0.24.0

# 或使用 requirements.txt 更新所有依赖
pip install -r requirements.txt
```

## API 接口说明

### 1. 提交初稿并获取 AI 评语

**端点**: `POST /api/ai/stage3/submit-draft-ai`

**请求体**:
```json
{
  "student_id": "01",
  "img_url": "https://oss.example.com/01_draft.jpg"
}
```

**响应**:
```json
{
  "status": "success",
  "feedback": "【AI老师批改】张三同学，你的作文结构清晰，语言生动...",
  "message": "AI评语生成完成"
}
```

**工作流程**:
1. 接收学生 ID 和初稿图片 URL
2. 从数据库获取学生完整信息
3. 调用 Coze 智能体生成评语
4. 更新数据库中的 AI 评语和状态
5. 通知教师端刷新数据
6. 返回评语给前端

### 2. 健康检查

**端点**: `GET /api/ai/health`

**响应**:
```json
{
  "status": "healthy",
  "coze_configured": true,
  "service": "coze_ai_agent"
}
```

## 提示词定制

Coze 服务使用默认提示词模板，可根据需要修改 `app/services/coze_service.py` 中的 `build_default_prompt()` 函数。

默认提示词包含：
- 学生基本信息（学号、姓名、当前阶段）
- 观察记录（感官评价、维度评价）
- 作文提交状态
- 批改要求（总体评价、优点、改进建议、鼓励性语言）

## 故障排除

### 1. 配置不完整
**现象**: 系统使用模拟评语而非真实 AI 评语
**检查**:
- `.env` 文件中是否配置了 `COZE_API_KEY` 和 `COZE_AGENT_ID`
- 配置项名称是否正确

### 2. API 调用失败
**现象**: 日志中出现"调用 Coze API 失败"错误
**检查**:
- API Key 和 Agent ID 是否有效
- 网络连接是否正常
- Coze API 服务状态

### 3. 依赖安装问题
**现象**: 导入 httpx 失败
**解决**:
```bash
python -m pip install httpx --upgrade
```

## 测试方法

### 1. 健康检查测试
```bash
curl http://localhost:8000/api/ai/health
```

### 2. 模拟提交测试
使用 Postman 或 curl 测试接口：
```bash
curl -X POST http://localhost:8000/api/ai/stage3/submit-draft-ai \
  -H "Content-Type: application/json" \
  -d '{"student_id": "01", "img_url": "https://example.com/draft.jpg"}'
```

### 3. 配置验证测试
检查配置是否正确加载：
```bash
python -c "from app.core.config import settings; print('Coze配置:', hasattr(settings, 'COZE_API_KEY'))"
```

## 扩展功能

### 1. 自定义提示词模板
修改 `call_coze_agent()` 函数的 `prompt_template` 参数，传入自定义模板。

### 2. 多智能体支持
可在配置中添加多个 Agent ID，根据场景选择不同的智能体。

### 3. 评语缓存
考虑添加 Redis 缓存，对相似的学生评语进行缓存，减少 API 调用。

## 注意事项

1. **API 调用频率**: Coze API 可能有调用频率限制，请合理设计调用策略
2. **错误处理**: 系统已实现优雅降级，API 失败时会返回模拟评语
3. **数据隐私**: 确保学生数据符合隐私保护要求
4. **成本控制**: 监控 API 调用量，控制成本

## 版本历史

- **v1.0.0** (2026-03-31): 初始集成版本
  - 基础 Coze API 集成
  - 优雅降级机制
  - 完整的配置和文档