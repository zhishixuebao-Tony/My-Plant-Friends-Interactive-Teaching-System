<template>
  <div class="stage-container">
    <van-nav-bar title="环节 2：我的记录卡观察与修改" fixed placeholder border />

    <div class="grid-layout">
      <!-- ================= 左上：课前记录卡展示区 ================= -->
      <div class="record-card-section pre-record">
        <div class="section-header">
          <van-icon name="photo-o" color="#07c160" /> 
          课前上传的记录卡
          <span class="record-hint">(课前已上传)</span>
        </div>
        
        <div class="record-content">
          <div v-if="preRecordCardUrl" class="pre-record-image">
            <div class="record-card-wrapper">
              <van-image 
                :src="preRecordCardUrl" 
                fit="contain" 
                class="record-card-img" 
                @click="openPreRecordCardPreview" 
                radius="8"
              />
              <div class="record-card-label">
                <span class="record-index">课前记录卡</span>
                <span class="record-hint-small">点击放大查看</span>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-record">
            <van-icon name="photo-fail" size="60" color="#ebedf0" />
            <p>暂无课前记录卡</p>
          </div>
        </div>
      </div>

      <!-- ================= 右上：修改后记录卡上传区 ================= -->
      <div class="record-card-section new-record">
        <div class="section-header">
          <van-icon name="camera-o" color="#1989fa" /> 
          修改后的记录卡
          <span class="record-hint">(先拍照，再上传)</span>
        </div>
        
        <div class="record-content">
          <div class="upload-area">
            <!-- 第一步：拍照按钮 -->
            <div class="capture-step" v-if="!capturedImage">
              <div class="capture-hint">
                <van-icon name="camera" color="#1989fa" size="24" />
                <span>第一步：点击拍照按钮拍摄记录卡</span>
              </div>
              <van-button 
                type="primary" 
                size="large" 
                block 
                round 
                @click="openCamera"
                class="capture-btn"
              >
                <van-icon name="photograph" size="20" style="margin-right: 8px;" />
                点击拍照
              </van-button>
            </div>
            
            <!-- 第二步：预览和上传 -->
            <div v-if="capturedImage" class="preview-upload-step">
              <div class="step-hint">
                <van-icon name="eye" color="#07c160" size="20" />
                <span>第二步：预览照片并上传</span>
              </div>
              
              <!-- 预览图片 -->
              <div class="captured-preview">
                <van-image 
                  :src="capturedImage" 
                  fit="contain" 
                  class="captured-img"
                  radius="8"
                />
                <div class="preview-actions">
                  <van-button 
                    type="default" 
                    size="small" 
                    @click="recapturePhoto"
                    class="recapture-btn"
                  >
                    <van-icon name="replay" />
                    重新拍照
                  </van-button>
                  <van-button 
                    type="warning" 
                    size="small" 
                    @click="uploadPhoto"
                    :loading="isUploading"
                    class="upload-btn"
                  >
                    <van-icon name="cloud-upload" />
                    上传图片
                  </van-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= 下方：评价与提交板块 ================= -->
      <div class="evaluation-submit-section">
        <div class="section-header">
          <van-icon name="comment-o" color="#f2bd27" /> 
          记录卡自我评价与提交
        </div>
        
        <div class="evaluation-submit-content">
          <!-- 评价部分 -->
          <div class="evaluation-part">
            <div class="evaluation-description">
              <p>请根据以下标准评价你的记录卡：</p>
            </div>
            
            <van-checkbox-group v-model="evalChecks" shape="square">
              <div 
                class="eval-card" 
                v-for="(item, index) in evalOptions" 
                :key="index"
                @click="toggleEval(item)"
                :class="{ 'is-active': evalChecks.includes(item) }"
              >
                <van-checkbox :name="item" @click.stop>
                  <div class="eval-label">
                    <span class="eval-index">评价 {{ index + 1 }}</span>
                    <span class="eval-text">{{ item }}</span>
                  </div>
                </van-checkbox>
              </div>
            </van-checkbox-group>
          </div>
          
          <!-- 提交部分 -->
          <div class="submit-part">
            <van-button 
              type="primary" 
              block 
              round 
              size="large" 
              @click="onFinalSubmit"
              :loading="isSubmitting"
              :disabled="!isUploadSuccess"
              loading-text="正在提交数据..."
              class="next-step-btn"
            >
              <van-icon name="arrow" style="transform: rotate(90deg); margin-right: 8px;" />
              提交并进入环节 3
            </van-button>
            
            <div class="progress-hint" v-if="isUploadSuccess">
              <van-icon name="success" color="#07c160" />
              <span>记录卡已上传，请完成评价后提交</span>
            </div>
            
            <div class="progress-hint" v-else>
              <van-icon name="info" color="#999" />
              <span>请先拍照上传记录卡并完成评价</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { uploadImageFlow } from '../api/student'; 
import axios from 'axios';
import { showToast, showImagePreview } from 'vant';

const userStore = useUserStore();

// 状态控制
const evalChecks = ref([]);
const fileList = ref([]);
const isSubmitting = ref(false);
const isUploadSuccess = ref(false);
const isUploading = ref(false);
const capturedImage = ref(null); // 拍照后的图片数据
const preRecordCardUrl = ref(''); // 课前记录卡URL
const uploadedUrl = ref(''); // 上传后的图片URL

// 评价选项
const evalOptions = [
  '评价一：能真实记录植物特点',
  '评价二：能描写出自己的感受'
];

  // 加载课前记录卡数据
onMounted(async () => {
  try {
    // 使用教师端接口获取学生详情，其中包含课前记录卡信息
    console.log('正在获取课前记录卡，学生ID:', userStore.studentId);
    const response = await axios.get(`/api/teacher/dashboard/student-detail/${userStore.studentId}`);
    
    if (response.data) {
      const data = response.data;
      console.log('获取到的学生详情数据:', data);
      
      // 从教师面板接口获取课前记录卡URL
      if (data.pre_record_card) {
        preRecordCardUrl.value = data.pre_record_card;
        console.log('成功获取课前记录卡URL:', preRecordCardUrl.value);
      } else {
        console.warn('教师端接口返回的数据中没有pre_record_card字段:', data);
        // 尝试其他可能的字段名
        if (data.preRecordCard) {
          preRecordCardUrl.value = data.preRecordCard;
        } else if (data.record_card_pre) {
          preRecordCardUrl.value = data.record_card_pre;
        }
      }
    }
  } catch (error) {
    console.warn('获取课前记录卡失败:', error);
    
    // 使用备用方案：尝试从学生信息接口获取
    try {
      const studentResponse = await axios.get(`/api/student/student/info/${userStore.studentId}`);
      if (studentResponse.data && studentResponse.data.pre_record_card) {
        preRecordCardUrl.value = studentResponse.data.pre_record_card;
        console.log('通过学生信息接口获取课前记录卡成功');
      }
    } catch (studentError) {
      console.warn('学生信息接口也失败，使用本地缓存:', studentError);
      
      // 最后尝试从userStore中获取（如果之前有缓存）
      if (userStore.preRecordCard) {
        preRecordCardUrl.value = userStore.preRecordCard;
        console.log('使用本地缓存的课前记录卡');
      }
    }
  }
});

// --- 课前记录卡预览 ---
const openPreRecordCardPreview = () => {
  if (!preRecordCardUrl.value) return;
  showImagePreview({
    images: [preRecordCardUrl.value],
    startPosition: 0,
    closeable: true,
  });
};

// --- 评价逻辑 ---
const toggleEval = (val) => {
  if (evalChecks.value.includes(val)) {
    evalChecks.value = evalChecks.value.filter(i => i !== val);
  } else {
    evalChecks.value.push(val);
  }
};

// --- 拍照上传逻辑 ---
// 打开相机（使用隐藏的文件输入）
let fileInputRef = null;

const openCamera = () => {
  // 创建隐藏的文件输入元素
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.capture = 'camera'; // 移动设备上调用摄像头
  
  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // 预览图片
      const reader = new FileReader();
      reader.onload = (event) => {
        capturedImage.value = event.target.result;
      };
      reader.readAsDataURL(file);
    }
  };
  
  input.click();
};

// 重新拍照
const recapturePhoto = () => {
  capturedImage.value = null;
};

// 上传图片
const uploadPhoto = async () => {
  if (!capturedImage.value) return;
  
  isUploading.value = true;
  try {
    // 将base64转换为文件对象
    const base64Data = capturedImage.value.split(',')[1];
    const binaryData = atob(base64Data);
    const array = [];
    for (let i = 0; i < binaryData.length; i++) {
      array.push(binaryData.charCodeAt(i));
    }
    const file = new File([new Uint8Array(array)], 'record_card.jpg', { type: 'image/jpeg' });
    
    // 调用阿里云 OSS 直传工具
    const url = await uploadImageFlow(userStore.studentId, 'stage2_record', file);
    
    uploadedUrl.value = url;
    isUploadSuccess.value = true;
    fileList.value = [{ content: capturedImage.value, status: 'done' }];
    showToast({ message: '记录卡已成功存入云端', type: 'success' });
  } catch (err) {
    console.error('上传失败:', err);
    showToast('上传失败，请检查网络或重试');
  } finally {
    isUploading.value = false;
  }
};

// 删除已上传图片
const onDelete = () => {
  isUploadSuccess.value = false;
  uploadedUrl.value = '';
  capturedImage.value = null;
  fileList.value = [];
};

// --- 最终提交逻辑 ---
const onFinalSubmit = async () => {
  if (!isUploadSuccess.value) return showToast('请先拍照上传记录卡哦');

  const randomDelay = Math.floor(Math.random() * 2000);
  await new Promise(resolve => setTimeout(resolve, randomDelay));
  
  isSubmitting.value = true;
  try {
    await axios.post('/api/student/stage2/record-card', {
      student_id: userStore.studentId,
      checks: evalChecks.value,
      img_url: uploadedUrl.value
    });
    
    showToast({ message: '记录卡提交成功！', type: 'success' });
    userStore.setStage('3');
  } catch (err) {
    console.error(err);
    showToast('提交失败，请重试');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* ================= 整体布局 - 平板优化 v4 (高度优化) ================= */
.stage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
  overflow: hidden;
}

.grid-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: minmax(150px, 30vh) minmax(150px, auto); /* 进一步降低行高 */
  gap: 6px; /* 进一步减少间隙 */
  padding: 6px; /* 进一步减少内边距 */
  overflow: hidden;
  max-height: calc(100vh - 120px); /* 考虑导航栏和地址栏空间 */
}

/* 平板适配 - 极限紧凑布局 */
@media (max-width: 1024px) {
  .grid-layout {
    max-height: calc(100vh - 100px);
    gap: 5px;
    padding: 5px;
    grid-template-rows: minmax(130px, 28vh) minmax(130px, auto);
  }
}

/* 平板横向模式优化 - 给下方更多空间 */
@media (max-width: 1024px) and (orientation: landscape) {
  .grid-layout {
    grid-template-rows: minmax(110px, 25vh) minmax(140px, auto);
  }
}

@media (max-width: 768px) {
  .grid-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto; /* 手机端恢复自动高度 */
    gap: 10px;
    padding: 10px;
  }
}

/* 横向平板优化 - 进一步压缩上方空间 */
@media (max-width: 1366px) and (min-height: 1024px) and (orientation: portrait) {
  .grid-layout {
    max-height: calc(100vh - 140px);
    gap: 8px;
    padding: 8px;
    grid-template-rows: minmax(150px, 28vh) minmax(150px, auto);
  }
}

/* 小尺寸平板优化 */
@media (max-width: 768px) and (min-height: 1024px) {
  .grid-layout {
    grid-template-rows: minmax(120px, 25vh) minmax(120px, auto);
  }
}

/* 超小平板优化 - 极度压缩 */
@media (max-height: 768px) and (orientation: portrait) {
  .grid-layout {
    grid-template-rows: minmax(100px, 22vh) minmax(100px, auto);
  }
}

/* 确保内容区域可滚动而不是被遮盖 */
.record-card-section {
  min-height: 0; /* 重要：允许内容区域收缩 */
}

.pre-record-image,
.upload-area {
  overflow-y: auto;
  max-height: 100%;
}

/* ================= 通用区块样式 - 平板优化 ================= */
.record-card-section,
.evaluation-submit-section {
  background: #fff;
  border-radius: 12px; /* 减少圆角 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06); /* 减少阴影 */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  font-size: 16px; /* 减小字体 */
  font-weight: bold;
  color: #333;
  padding: 12px 14px; /* 减少padding */
  border-bottom: 1px solid #f2f3f5;
  display: flex;
  align-items: center;
  gap: 6px; /* 减少间隙 */
  flex-shrink: 0;
}

.record-hint {
  font-size: 12px; /* 减小字体 */
  color: #999;
  margin-left: 6px; /* 减少间距 */
  font-weight: normal;
}

.record-content,
.evaluation-submit-content {
  flex: 1;
  padding: 12px; /* 减少padding */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ================= 左上：课前记录卡展示区 ================= */
.pre-record {
  border-top: 4px solid #07c160;
}

.pre-record-image {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.record-card-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 280px;
  margin: 0 auto;
}

.record-card-img {
  width: 100%;
  height: 240px;
  object-fit: contain;
  background: #f8f9fa;
  cursor: pointer;
  transition: transform 0.2s;
  border-radius: 8px 8px 0 0;
}

.record-card-img:hover {
  transform: scale(1.02);
}

.record-card-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 0 0 8px 8px;
}

.record-index {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.record-hint-small {
  font-size: 12px;
  color: #999;
}

.empty-record {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
  padding: 40px;
}

.empty-record p {
  margin-top: 12px;
  font-size: 14px;
}

/* ================= 右上：修改后记录卡上传区 ================= */
.new-record {
  border-top: 4px solid #1989fa;
}

.upload-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 第一步：拍照按钮区域 */
.capture-step {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
}

.capture-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.capture-btn {
  width: 80%;
  max-width: 280px;
  height: 56px;
  font-size: 18px;
  font-weight: bold;
}

/* 第二步：预览和上传区域 */
.preview-upload-step {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: bold;
  color: #07c160;
  padding: 10px;
  background: #f0f9eb;
  border-radius: 8px;
}

.captured-preview {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.captured-img {
  width: 200px;
  height: 200px;
  object-fit: contain;
  background: #f8f9fa;
  border: 2px solid #ebedf0;
  border-radius: 12px;
}

.preview-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  width: 100%;
}

.recapture-btn, .upload-btn {
  min-width: 120px;
}

.uploaded-preview {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-top: 16px;
}

.preview-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.preview-image-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.preview-img {
  width: 180px;
  height: 180px;
  object-fit: contain;
  background: #fff;
  border: 1px solid #ebedf0;
  border-radius: 8px;
}

.upload-actions {
  display: flex;
  justify-content: center;
}

.delete-btn {
  min-width: 140px;
}

.comparison-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: linear-gradient(135deg, #fff9e6 0%, #fff1c1 100%);
  border-radius: 8px;
  font-size: 14px;
  color: #856404;
  margin-top: 16px;
  text-align: center;
}

/* ================= 评价与提交板块 ================= */
.evaluation-submit-section {
  grid-column: span 2;
  border-top: 4px solid #f2bd27;
}

.evaluation-submit-content {
  display: flex;
  flex-direction: column;
  gap: 16px; /* 减少间隙 */
  padding: 14px; /* 减少padding */
}

/* 评价部分 - 左右并排布局 */
.evaluation-part {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.evaluation-description {
  margin-bottom: 8px;
}

.evaluation-description p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 评价卡片容器 - 左右并排 */
.van-checkbox-group {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 两列并排 */
  gap: 10px; /* 卡片之间的间隙 */
  margin-bottom: 8px;
}

.eval-card {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.2s;
  cursor: pointer;
  margin: 0; /* 移除垂直间距，由grid gap控制 */
  min-height: 100px; /* 固定最小高度 */
  display: flex;
  align-items: center;
}

.eval-card:active {
  transform: scale(0.98);
}

.eval-card.is-active {
  background-color: #f0f9eb;
  border-color: #07c160;
}

.eval-label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-left: 10px;
  flex: 1;
}

.eval-index {
  font-size: 13px;
  font-weight: bold;
  color: #1989fa;
}

.eval-text {
  font-size: 15px;
  color: #323233;
  font-weight: 500;
  line-height: 1.4;
}

/* 平板优化 */
@media (max-width: 1024px) {
  .van-checkbox-group {
    gap: 8px;
  }
  
  .eval-card {
    padding: 14px;
    min-height: 90px;
  }
  
  .eval-text {
    font-size: 14px;
  }
}

/* 手机端恢复垂直布局 */
@media (max-width: 768px) {
  .van-checkbox-group {
    grid-template-columns: 1fr; /* 单列垂直布局 */
    gap: 12px;
  }
  
  .eval-card {
    min-height: auto;
  }
}

:deep(.van-checkbox__icon) {
  font-size: 24px;
}

/* 提交部分 */
.submit-part {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebedf0;
}

.next-step-btn {
  margin: 0;
}

.progress-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}

.progress-hint:first-of-type {
  background: #f0f9eb;
  color: #07c160;
}

.progress-hint:last-of-type {
  background: #f8f9fa;
  color: #999;
}

/* ================= 响应式调整 ================= */
@media (max-width: 768px) {
  .grid-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    gap: 12px;
    padding: 12px;
  }
  
  .record-card-img {
    max-height: 200px;
  }
  
  .captured-img, .preview-img {
    width: 140px;
    height: 140px;
  }
  
  .capture-btn {
    width: 90%;
  }
  
  .evaluation-submit-section {
    margin-top: 8px;
  }
  
  .evaluation-submit-content {
    padding: 16px;
  }
}
</style>