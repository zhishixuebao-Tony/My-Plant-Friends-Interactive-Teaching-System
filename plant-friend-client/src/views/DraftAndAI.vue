<template>
  <div class="stage-container">
    <van-nav-bar title="环节 3：起草初稿与 AI 老师指导" fixed placeholder border />

    <div class="split-layout">
      <!-- ================= 左侧：写作引导与课前照片 ================= -->
      <div class="left-panel">
        <!-- 上方：课前植物照片展示 -->
        <div class="photo-section">
          <div class="photo-header">
            <van-icon name="photo-o" color="#07c160" />
            <span>课前上传的植物照片</span>
          </div>
          <div class="photo-gallery">
            <div v-if="prePlantPhotos.length > 0" class="photos-container">
              <div class="photo-item" v-for="(photo, index) in prePlantPhotos" :key="index">
                <van-image 
                  :src="photo" 
                  fit="cover" 
                  radius="8"
                  class="plant-photo"
                  @click="previewPhoto(photo)"
                />
                <div class="photo-label">课前照片 {{ index + 1 }}</div>
              </div>
            </div>
            <div v-else class="empty-photos">
              <van-icon name="photo-fail" size="40" color="#ebedf0" />
              <p>暂无课前植物照片</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= 右侧：上传初稿区 ================= -->
      <div class="right-panel">
        <div class="panel-header">📸 上传作文初稿</div>
        
        <div class="scroll-content">
          
          <!-- 1. 拍照上传区 -->
          <div class="upload-wrapper">
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

          <!-- 2. 上传成功提示 (AI自动评价) -->
          <div class="upload-success-box" v-if="isUploadSuccess">
            <div class="success-message">
              <van-icon name="success" color="#07c160" size="24" />
              <span>初稿已上传成功！</span>
            </div>
            <div class="ai-hint">
              <van-icon name="magic" color="#1989fa" />
              <span>AI老师正在自动评价你的作文，评语将在最后环节显示</span>
            </div>
          </div>

        </div>

        <!-- 3. 底部进入下一环节按钮 -->
        <div class="action-footer">
          <van-button 
            type="primary" 
            block 
            round 
            size="large" 
            @click="goToStage4"
            :disabled="!isUploadSuccess"
          >
            初稿已上传，进入魔法资源包
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { uploadImageFlow, saveDraftApi, submitDraftAiApi } from '../api/student'; 
import axios from 'axios';
import { showToast, showImagePreview } from 'vant';

const userStore = useUserStore();

// 状态变量
const fileList = ref([]);
const isUploadSuccess = ref(false);
const uploadedUrl = ref('');

// 课前植物照片
const prePlantPhotos = ref([]);

// 页面加载时获取课前植物照片
onMounted(async () => {
  try {
    // 调用教师端接口获取学生详情，从中获取课前植物照片
    const response = await axios.get(`/api/teacher/dashboard/student-detail/${userStore.studentId}`);
    
    if (response.data) {
      const data = response.data;
      // 从教师面板接口获取课前植物照片
      const photos = [];
      if (data.pre_plant_1) photos.push(data.pre_plant_1);
      if (data.pre_plant_2) photos.push(data.pre_plant_2);
      if (data.pre_plant_3) photos.push(data.pre_plant_3);
      
      if (photos.length > 0) {
        prePlantPhotos.value = photos;
      }
    }
  } catch (error) {
    console.warn('获取课前植物照片失败:', error);
  }
});

// --- 1. 预览课前照片 ---
const previewPhoto = (photoUrl) => {
  if (!photoUrl) return;
  showImagePreview({
    images: [photoUrl],
    startPosition: 0,
    closeable: true,
    closeOnClickImage: true,
    closeOnClickOverlay: true,
    teleport: 'body'
  });
};

// --- 2. 拍照上传云端并自动触发AI评价 ---
const afterRead = async (file) => {
  const randomDelay = Math.floor(Math.random() * 2000);
  await new Promise(resolve => setTimeout(resolve, randomDelay));

  file.status = 'uploading';
  file.message = '正在上传...';
  
  try {
    const url = await uploadImageFlow(userStore.studentId, 'stage3_draft', file.file);
    file.status = 'done';
    uploadedUrl.value = url;
    isUploadSuccess.value = true;
    
    // 自动触发AI评价（后台处理，不阻塞用户操作）
    triggerAIFeedback(url);
  } catch (err) {
    file.status = 'failed';
    showToast('云端连接失败，请检查网络');
  }
};

const onDelete = () => {
  isUploadSuccess.value = false;
  uploadedUrl.value = '';
};

// --- 3. 自动触发AI评价（后台静默处理） ---
const triggerAIFeedback = async (imgUrl) => {
  try {
    // 1. 保存初稿到数据库
    await saveDraftApi(userStore.studentId, imgUrl);

    // 2. 触发AI批改（后台异步处理）
    await submitDraftAiApi(userStore.studentId, imgUrl);
    
    console.log('AI评价已自动触发，评语将在最后环节显示');
    
  } catch (err) {
    console.warn("AI评价触发失败，但用户可继续:", err);
    // 失败不影响用户继续操作
  }
};

// --- 4. 进入环节 4 ---
const goToStage4 = () => {
  userStore.setStage('4');
};
</script>

<style scoped>
.stage-container { 
  height: 100%; 
  display: flex; 
  flex-direction: column; 
  background-color: #f7f8fa; 
  overflow: hidden;
}
.split-layout { 
  flex: 1; 
  display: flex; 
  overflow: hidden; 
  max-height: calc(100vh - 120px); /* 考虑导航栏和地址栏空间 */
}

/* 平板适配 */
@media (max-width: 1024px) {
  .split-layout {
    max-height: calc(100vh - 100px);
  }
}

@media (max-width: 1024px) and (orientation: portrait) {
  .split-layout {
    flex-direction: column;
  }
}

/* 横向平板优化 */
@media (max-width: 1366px) and (min-height: 1024px) and (orientation: portrait) {
  .split-layout {
    max-height: calc(100vh - 140px);
  }
}

/* ================= 左侧：写作引导与课前照片 ================= */
.left-panel { 
  flex: 1; 
  background-color: #f0f7ff; 
  display: flex; 
  flex-direction: column; 
  padding: 20px; 
  gap: 20px; 
  overflow: hidden;
}

/* 照片展示区 */
.photo-section {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.photo-header {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  padding: 16px;
  border-bottom: 1px solid #f2f3f5;
  display: flex;
  align-items: center;
  gap: 8px;
}

.photo-gallery {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.photos-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.photo-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.plant-photo {
  width: 100%;
  height: 120px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s;
  border: 2px solid #ebedf0;
}

.plant-photo:hover {
  transform: scale(1.02);
}

.photo-label {
  font-size: 12px;
  color: #666;
  text-align: center;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 6px;
  width: 100%;
}

.empty-photos {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
  padding: 40px 20px;
}

.empty-photos p {
  margin-top: 10px;
  font-size: 14px;
}

/* 写作引导区 */
.guide-section {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.guide-box {
  flex: 1;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.guide-icon { 
  animation: float 3s ease-in-out infinite; 
  margin-bottom: 16px; 
}
@keyframes float { 
  0%, 100% { transform: translateY(0); } 
  50% { transform: translateY(-15px); } 
}

.guide-title { 
  font-size: 22px; 
  color: #333; 
  margin: 0 0 16px 0; 
}

.guide-desc {
  text-align: left;
  width: 100%;
}

.guide-desc p {
  font-size: 16px;
  color: #333;
  margin: 0 0 12px 0;
  font-weight: 500;
}

.guide-tips {
  list-style: none;
  padding: 0;
  margin: 0;
}

.guide-tips li {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ================= 右侧：上传初稿区 ================= */
.right-panel { 
  flex: 1; 
  background-color: #fff; 
  display: flex; 
  flex-direction: column; 
  border-left: 1px solid #ebedf0; 
}

.panel-header { 
  font-size: 20px; 
  font-weight: bold; 
  padding: 20px; 
  color: #323233; 
  border-bottom: 1px solid #f2f3f5; 
  flex-shrink: 0; 
}

.scroll-content { 
  flex: 1; 
  padding: 20px; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  overflow-y: auto; 
}

/* 拍照框 */
.upload-wrapper { 
  width: 100%; 
  max-width: 450px; 
  margin-bottom: 20px; 
}

.custom-uploader { 
  width: 100%; 
}

.upload-trigger {
  width: 100%; 
  height: 220px; 
  border: 3px dashed #dcdee0;
  display: flex; 
  flex-direction: column; 
  justify-content: center; 
  align-items: center;
  background-color: #f7f8fa; 
  border-radius: 16px; 
  transition: all 0.3s; 
  cursor: pointer;
}

.upload-trigger:active { 
  transform: scale(0.98); 
}

.upload-trigger.has-file { 
  border: 3px solid #1989fa; 
  background-color: #f0f7ff; 
}

.upload-text { 
  margin-top: 15px; 
  font-size: 18px; 
  color: #969799; 
  font-weight: bold; 
}

.upload-trigger.has-file .upload-text { 
  color: #1989fa; 
}

.success-text { 
  color: #07c160; 
  font-size: 15px; 
  font-weight: bold; 
  margin-top: 15px; 
  text-align: center; 
}

/* 上传成功提示框 */
.upload-success-box {
  width: 100%;
  max-width: 450px;
  margin-top: 20px;
  animation: fadeIn 0.5s;
  background: #f0f9ff;
  border-radius: 12px;
  padding: 20px;
  border: 2px solid #1989fa;
}

.success-message {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.success-message span {
  font-size: 18px;
  font-weight: bold;
  color: #07c160;
}

.ai-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #e8f5e8;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  color: #1989fa;
  line-height: 1.5;
}

.action-footer { 
  padding: 25px; 
  background-color: #fff; 
  box-shadow: 0 -4px 15px rgba(0,0,0,0.03); 
  flex-shrink: 0;
}

/* 动画 */
@keyframes fadeIn { 
  from { opacity: 0; } 
  to { opacity: 1; } 
}

:deep(.van-uploader__preview-image) { 
  width: 100%; 
  height: 220px; 
  border-radius: 16px; 
  object-fit: cover; 
}

:deep(.van-uploader__preview) { 
  margin: 0; 
  width: 100%; 
}

/* 响应式调整 */
@media (max-width: 768px) {
  .split-layout {
    flex-direction: column;
  }
  
  .left-panel {
    flex-direction: row;
    gap: 12px;
  }
  
  .photo-section, .guide-section {
    flex: 1;
  }
  
  .photos-container {
    grid-template-columns: 1fr;
  }
  
  .plant-photo {
    height: 100px;
  }
}
</style>
