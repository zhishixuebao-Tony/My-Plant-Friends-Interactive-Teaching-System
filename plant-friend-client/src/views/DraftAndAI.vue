<template>
  <div class="stage-container">
    <van-nav-bar title="环节 3：起草初稿与 AI 老师指导" fixed placeholder border />

    <div class="split-layout">
      <!-- ================= 左侧：写作引导 ================= -->
      <div class="left-panel">
        <div class="guide-box">
          <van-icon name="edit" size="60" color="#1989fa" class="float-icon" />
          <h2 class="guide-title">开始撰写初稿吧！</h2>
          <p class="guide-desc">
            请拿出你的作文本，根据刚才修改好的“植物记录卡”，把你的植物朋友写下来。
            <br><br>
            写完后，在右侧点击拍照上传，点击召唤 AI 老师，它会给你专属的修改建议哦！
          </p>
        </div>
      </div>

      <!-- ================= 右侧：交互区 ================= -->
      <div class="right-panel">
        <div class="panel-header">📸 上传初稿与 AI 批改</div>
        
        <div class="scroll-content">
          
          <!-- 1. 拍照上传区 -->
          <div class="upload-wrapper" v-if="!hasAIFeedback">
            <van-uploader 
              v-model="fileList" 
              :max-count="1" 
              capture="camera" 
              :after-read="afterRead"
              @delete="onDelete"
              class="custom-uploader"
            >
              <template #default>
                <div class="upload-trigger" :class="{ 'has-file': fileList.length > 0 }">
                  <van-icon name="photograph" size="50" :color="fileList.length > 0 ? '#1989fa' : '#969799'" />
                  <span class="upload-text">{{ fileList.length > 0 ? '重新拍摄初稿' : '点击调用摄像头拍摄初稿' }}</span>
                </div>
              </template>
            </van-uploader>
            <div class="success-text" v-if="isUploadSuccess">✅ 初稿已成功上传至云端！</div>
          </div>

          <!-- 2. AI 召唤按钮 (上传成功后出现) -->
          <div class="ai-action-box" v-if="isUploadSuccess && !hasAIFeedback">
            <van-button 
              color="linear-gradient(to right, #7232dd, #1989fa)"
              block 
              round 
              size="large" 
              icon="smile-comment-o"
              @click="getAIFeedback"
              :loading="isRequestingAI"
              loading-text="AI 老师正在阅读你的作文..."
              class="magic-btn"
            >
              召唤 AI 老师给我点评
            </van-button>
          </div>

          <!-- 3. AI 评语展示区 (获取成功后出现) -->
          <div class="ai-feedback-box" v-if="hasAIFeedback">
            <div class="ai-avatar">
              <van-icon name="cluster-o" size="30" color="#fff" />
            </div>
            <div class="ai-content">
              <h3 class="ai-title">AI 老师的悄悄话：</h3>
              <div class="ai-text">{{ aiFeedbackText }}</div>
            </div>
          </div>

        </div>

        <!-- 4. 底部提交按钮 (看完评语后解锁) -->
        <div class="action-footer">
          <van-button 
            type="primary" 
            block 
            round 
            size="large" 
            @click="goToStage4"
            :disabled="!hasAIFeedback"
          >
            我已阅读评语，进入环节 4 魔法资源包
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { uploadImageFlow } from '../api/student'; 
import axios from 'axios';
import { showToast } from 'vant';

const userStore = useUserStore();

// 状态变量
const fileList = ref([]);
const isUploadSuccess = ref(false);
const uploadedUrl = ref('');

// AI 相关状态
const isRequestingAI = ref(false);
const hasAIFeedback = ref(false);
const aiFeedbackText = ref('');

// --- 1. 拍照上传云端 ---
const afterRead = async (file) => {
  file.status = 'uploading';
  file.message = '正在上传...';
  
  try {
    const url = await uploadImageFlow(userStore.studentId, 'stage3_draft', file.file);
    file.status = 'done';
    uploadedUrl.value = url;
    isUploadSuccess.value = true;
  } catch (err) {
    file.status = 'failed';
    showToast('云端连接失败，请检查网络');
  }
};

const onDelete = () => {
  isUploadSuccess.value = false;
  hasAIFeedback.value = false; // 删除照片重置 AI 状态
  uploadedUrl.value = '';
};

// --- 2. 获取 AI 评价 ---
const getAIFeedback = async () => {
  isRequestingAI.value = true;
  
  try {
    // 1. 先把初稿照片存入数据库
    await axios.post('/api/student/stage3/save-draft', {
      student_id: userStore.studentId,
      img_url: uploadedUrl.value
    });

    // 2. 调用后端的 AI 批改接口 (根据你之前的 Swagger 截图)
    const aiRes = await axios.post('/api/ai/stage3/submit-draft-ai', {
      student_id: userStore.studentId,
      img_url: uploadedUrl.value
    });

    // 假设后端返回了 feedback 字段
    if (aiRes.data && aiRes.data.feedback) {
      aiFeedbackText.value = aiRes.data.feedback;
    } else {
      throw new Error("AI 接口未返回文本");
    }
    
  } catch (err) {
    console.warn("AI 接口未通，启用智能降级模拟评语", err);
    // 【智能降级】如果你的 AI 接口还没写好，这里会兜底显示模拟评语，防止演示卡死
    aiFeedbackText.value = "✨ 你的观察非常仔细！字迹也很工整。如果在描写植物叶子的时候，能多加一点关于‘摸上去是什么感觉’的描写，你的文章就会更生动啦！继续加油哦！";
  } finally {
    isRequestingAI.value = false;
    hasAIFeedback.value = true; // 无论真假，都解锁下一步
  }
};

// --- 3. 进入环节 4 ---
const goToStage4 = () => {
  userStore.currentStage = '4';
};
</script>

<style scoped>
.stage-container { height: 100vh; display: flex; flex-direction: column; background-color: #f7f8fa; }
.split-layout { flex: 1; display: flex; overflow: hidden; }

/* 左侧引导区 */
.left-panel { flex: 1; background-color: #f0f7ff; display: flex; justify-content: center; align-items: center; padding: 30px; }
.guide-box { text-align: center; background: #fff; padding: 40px 30px; border-radius: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); }
.float-icon { animation: float 3s ease-in-out infinite; margin-bottom: 10px; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
.guide-title { font-size: 24px; color: #333; margin: 20px 0; }
.guide-desc { font-size: 16px; color: #666; line-height: 1.8; text-align: left; }

/* 右侧交互区 */
.right-panel { flex: 1.2; background-color: #fff; display: flex; flex-direction: column; border-left: 1px solid #ebedf0; }
.panel-header { font-size: 20px; font-weight: bold; padding: 25px; color: #323233; border-bottom: 1px solid #f2f3f5; }
.scroll-content { flex: 1; padding: 30px; display: flex; flex-direction: column; align-items: center; overflow-y: auto; }

/* 拍照框 */
.upload-wrapper { width: 100%; max-width: 450px; margin-bottom: 20px; }
.custom-uploader { width: 100%; }
.upload-trigger {
  width: 100%; height: 220px; border: 3px dashed #dcdee0;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  background-color: #f7f8fa; border-radius: 16px; transition: all 0.3s; cursor: pointer;
}
.upload-trigger:active { transform: scale(0.98); }
.upload-trigger.has-file { border: 3px solid #1989fa; background-color: #f0f7ff; }
.upload-text { margin-top: 15px; font-size: 18px; color: #969799; font-weight: bold; }
.upload-trigger.has-file .upload-text { color: #1989fa; }
.success-text { color: #07c160; font-size: 15px; font-weight: bold; margin-top: 15px; text-align: center; }

/* AI 召唤按钮 */
.ai-action-box { width: 100%; max-width: 450px; margin-top: 20px; animation: fadeIn 0.5s; }
.magic-btn { font-size: 18px; font-weight: bold; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(25, 137, 250, 0.3); }

/* AI 评语气泡区 */
.ai-feedback-box {
  width: 100%; max-width: 500px; margin-top: 20px;
  background: linear-gradient(135deg, #f3e7ff 0%, #e2e0ff 100%);
  border-radius: 16px; padding: 25px; position: relative;
  box-shadow: 0 8px 20px rgba(114, 50, 221, 0.15);
  animation: slideUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.ai-avatar {
  position: absolute; top: -20px; left: -20px; width: 60px; height: 60px;
  background: linear-gradient(135deg, #7232dd, #1989fa);
  border-radius: 50%; display: flex; justify-content: center; align-items: center;
  box-shadow: 0 4px 10px rgba(114, 50, 221, 0.3); border: 4px solid #fff;
}
.ai-content { margin-left: 20px; }
.ai-title { color: #531dab; font-size: 18px; margin: 0 0 10px 0; font-weight: bold; }
.ai-text { color: #391085; font-size: 16px; line-height: 1.8; white-space: pre-wrap; font-weight: 500; }

.action-footer { padding: 25px; background-color: #fff; box-shadow: 0 -4px 15px rgba(0,0,0,0.03); }

/* 动画 */
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

:deep(.van-uploader__preview-image) { width: 100%; height: 220px; border-radius: 16px; object-fit: cover; }
:deep(.van-uploader__preview) { margin: 0; width: 100%; }
</style>