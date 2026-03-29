🌱 《我的植物朋友》互动课堂系统 (My Plant Friends)

![alt text](https://img.shields.io/badge/Vue%203-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)![alt text](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)

![alt text](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)![alt text](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=socketdotio&logoColor=white)

![alt text](https://img.shields.io/badge/Aliyun%20OSS-FF6A00?style=for-the-badge&logo=alibabacloud&logoColor=white)
本项目是专为小学三年级语文习作课《我的植物朋友》量身定制的 50 人高并发线下课堂互动教学系统。
系统采用“推拉结合 (WebSocket + 轮询)”的实时架构，支持教师端大屏零延迟监控全班学情，学生端通过平板/手机完成闯关式写作任务，并无缝对接阿里云 OSS 与大语言模型（AI 批改）。
✨ 核心功能亮点
👨‍🏫 教师端指挥中心 (Teacher Dashboard)
50人实时状态矩阵：全班学生在线/离线状态实时变色，完成最终定稿的学生自动点亮 🏆 奖杯。
四大实时学情看板：感官观察统计、记录卡自评统计、资源包热度、AI 批改覆盖率，数据随学生提交瞬间跳动。
写作成长轨迹抽屉：点击任意学生，即可同屏对比：课前植物实物图 -> 原始记录卡 -> 课中修改记录卡 -> 习作初稿 -> 最终定稿，成长轨迹一目了然。
一键重置课堂：内置独立运维脚本，一键清空课堂过程数据，保留课前预置资源，方便多次彩排与授课。
🧑‍🎓 学生端闯关式学习 (Student Flow)
防错登录：输入两位数学号自动映射姓名，拉取专属的课前植物照片与观察视频。
环节 1：感官观察：高级轮播卡片 + 沉浸式视频弹窗，支持多选感官体验（看了看、闻了闻等）。
环节 2：记录卡修改：超大触控拍照框，直接调用移动端摄像头，照片直传阿里云 OSS。
环节 3：AI 老师指导：提交初稿后召唤 AI 老师，带有 Q 弹动画的 AI 专属评语框（支持断网智能降级）。
环节 4：魔法资源包：静默统计资源点击热度，完成知识小闯关后解锁下一环节。
环节 5：荣誉时刻：提交定稿后，触发全屏 canvas-confetti 撒花特效，并生成精美的“小小植物学家”电子奖状。
🛠️ 技术栈架构
前端：Vue 3 (Composition API) + Vite + Vant 4 + Pinia + Axios
后端：Python 3.12 + FastAPI + Uvicorn
数据库：MongoDB (使用 Motor 异步引擎)
实时通讯：原生 WebSockets (带断线自动重连机制)
云端服务：
阿里云 OSS：采用后端中转签名（Server-side Proxy）彻底解决跨域上传问题。
阿里云通义千问：DashScope API 接入（用于环节 3 作文批改）。
内网穿透：适配 cpolar，解决真实课堂局域网/广域网平板访问限制。
🚀 快速开始
1. 环境准备
Node.js 18+
Python 3.12
MongoDB 服务端 (默认运行在 localhost:27017)
2. 后端部署 (Backend)
code
Bash
# 1. 进入后端目录
cd backend

# 2. 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库 (生成 50 名学生与测试账号)
python init_db.py

# 5. 启动 FastAPI 服务
python run.py
后端服务将运行在：http://127.0.0.1:8000
3. 前端部署 (Frontend)
code
Bash
# 1. 进入前端目录
cd plant-friend-client

# 2. 安装依赖
npm install

# 3. 启动 Vite 开发服务器
npm run dev
前端服务将运行在：http://localhost:5173
📚 核心运维脚本说明
项目根目录提供了两个极其重要的数据库脚本：
python init_db.py：首次建库使用。自动生成 01-50 号学生档案，初始化教师密码（123456），并预留 pre_plant_1 等阿里云 OSS 资源字段。
python reset_class.py：课前重置使用。一键清空上一次测试产生的进度、照片和 AI 评语，但会完美保留老师辛苦填入的课前植物照片，让系统瞬间恢复到上课前的干净状态。
🌐 局域网/穿透测试指南
由于移动端调用摄像头强制要求 HTTPS 协议，建议在真实课堂测试时使用 cpolar 进行内网穿透：
终端运行 cpolar http 8000 获取后端公网 HTTPS 地址。
将前端 src/main.js 中的 axios.defaults.baseURL 修改为该地址。
终端运行 cpolar http 5173 获取前端地址，生成二维码供全班学生平板扫码接入。
（注：Vite 6+ 穿透时，需在 vite.config.js 中设置 hmr: false 以防止 WebSocket 协议冲突报错）。
📸 界面预览
<img width="2552" height="1354" alt="msedge_1QwTAiAUgO(1)" src="https://github.com/user-attachments/assets/be12bae7-e401-4eab-a3f2-a857327799d1" />
<img width="2552" height="1354" alt="image" src="https://github.com/user-attachments/assets/51059e0e-8864-44aa-9039-29a5ffb02789" />
<img width="2552" height="1354" alt="image" src="https://github.com/user-attachments/assets/c516ddda-7438-4eb0-a1b6-7316fb61e40d" />
📄 License
MIT License.
本项目为教育技术探索与赛课专属定制，欢迎交流与 Fork！
(End of README)
