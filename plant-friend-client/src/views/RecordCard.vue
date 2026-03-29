<template>
  <div class="stage-container">
    <van-nav-bar title="环节 2：我的记录卡观察与修改" fixed placeholder border />

    <div class="split-layout">
      <!-- ================= 左侧：多媒体回顾区 ================= -->
      <div class="left-panel">
        <div class="media-container">
          
          <div class="panel-header-simple">对照植物实物，修改记录卡</div>

          <!-- 上方：植物照片轮播卡片 (复用环节 1 设计) -->
          <div class="media-card" v-if="userStore.prePlantPhotos && userStore.prePlantPhotos.length > 0">
            <div class="card-title">
              <van-icon name="photo-o" color="#07c160" /> 我的植物档案
            </div>
            
            <van-swipe class="photo-swipe" :autoplay="3500" indicator-color="white">
              <van-swipe-item v-for="(img, index) in userStore.prePlantPhotos" :key="index">
                <van-image 
                  :src="img" 
                  fit="cover" 
                  class="swipe-img" 
                  @click="openImagePreview(index)" 
                />
                <div class="swipe-hint">🔍 点击放大观察细节 ({{ index + 1 }}/{{ userStore.prePlantPhotos.length }})</div>
              </van-swipe-item>
            </van-swipe>
          </div>

          <!-- 下方：观察视频卡片 -->
          <div class="media-card" v-if="userStore.preVideoUrl">
            <div class="card-title">
              <van-icon name="video-o" color="#ff976a" /> 动态观察记录
            </div>
            
            <div class="video-cover" @click="showVideoModal = true">
              <div class="play-button">
                <van-icon name="play" size="40" color="#fff" />
              </div>
              <span class="cover-text">点击播放高清视频</span>
            </div>
          </div>

        </div>
      </div>

      <!-- ================= 右侧：评价与上传区 ================= -->
      <div class="right-panel">
        <div class="panel-header">自评与记录卡定稿</div>
        
        <div class="scroll-content">
          <!-- 1. 评价维度勾选 (大卡片设计) -->
          <div class="card-section">
            <div class="section-title">✨ 请对自己的记录卡进行评价：</div>
            <van-checkbox-group v-model="evalChecks" shape="square">
              <div 
                class="custom-check-card" 
                v-for="(item, index) in evalOptions" 
                :key="index"
                @click="toggleEval(item)"
                :class="{ 'is-active': evalChecks.includes(item) }"
              >
                <van-checkbox :name="item" @click.stop>
                  <div class="check-label">
                    <span class="text">{{ item }}</span>
                  </div>
                </van-checkbox>
              </div>
            </van-checkbox-group>
          </div>

          <!-- 2. 拍照上传区域 (美化版) -->
          <div class="card-section">
            <div class="section-title">📸 拍照上传修改后的记录卡：</div>
            
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
                    <van-icon name="photograph" size="48" :color="fileList.length > 0 ? '#07c160' : '#969799'" />
                    <span class="upload-text">{{ fileList.length > 0 ? '点击重新拍照' : '点击调用摄像头拍照' }}</span>
                  </div>
                </template>
              </van-uploader>
            </div>
          </div>
        </div>

        <!-- 3. 底部固定提交按钮 -->
        <div class="action-footer">
          <van-button 
            type="primary" 
            block 
            round 
            size="large" 
            @click="onFinalSubmit"
            :loading="isSubmitting"
            :disabled="!isUploadSuccess"
            loading-text="正在提交数据..."
          >
            提交并进入环节 3
          </van-button>
        </div>
      </div>
    </div>

    <!-- ================= 视频专属全屏弹窗 ================= -->
    <van-popup 
      v-model:show="showVideoModal" 
      closeable 
      round 
      class="video-popup"
      @closed="onVideoClose"
      teleport="body"
    >
      <div class="popup-header">植物观察视频</div>
      <video
        ref="videoPlayer"
        :src="userStore.preVideoUrl"
        controls
        playsinline
        preload="metadata"
        class="full-video"
      ></video>
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue';
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
const uploadedUrl = ref('');

// 视频弹窗控制
const showVideoModal = ref(false);
const videoPlayer = ref(null);

// 评价选项
const evalOptions = [
  '评价一：能真实记录植物特点',
  '评价二：能描写出自己的感受',
  '评价三：书写认真、字迹工整'
];

// --- 动作逻辑 ---
const openImagePreview = (startIndex) => {
  if (!userStore.prePlantPhotos || userStore.prePlantPhotos.length === 0) return;
  showImagePreview({
    images: userStore.prePlantPhotos,
    startPosition: startIndex,
    closeable: true,
  });
};

const onVideoClose = () => {
  if (videoPlayer.value) {
    videoPlayer.value.pause();
  }
};

const toggleEval = (val) => {
  if (evalChecks.value.includes(val)) {
    evalChecks.value = evalChecks.value.filter(i => i !== val);
  } else {
    evalChecks.value.push(val);
  }
};

// --- 上传与提交逻辑 ---
const afterRead = async (file) => {
  file.status = 'uploading';
  file.message = '正在上传云端...';
  
  try {
    // 调用阿里云 OSS 直传工具 (参数：学号, 环节名, 文件对象)
    const url = await uploadImageFlow(userStore.studentId, 'stage2_record', file.file);
    
    file.status = 'done';
    file.message = '上传成功';
    uploadedUrl.value = url;
    isUploadSuccess.value = true;
    showToast({ message: '记录卡已成功存入云端', type: 'success' });
  } catch (err) {
    file.status = 'failed';
    file.message = '上传失败';
    showToast('云端连接失败，请检查网络或配置');
  }
};

const onDelete = () => {
  isUploadSuccess.value = false;
  uploadedUrl.value = '';
};

const onFinalSubmit = async () => {
  if (!isUploadSuccess.value) return showToast('请先拍照上传记录卡哦');
  
  isSubmitting.value = true;
  try {
    await axios.post('/api/student/stage2/record-card', {
      student_id: userStore.studentId,
      checks: evalChecks.value,
      img_url: uploadedUrl.value
    });
    
    showToast({ message: '记录卡提交成功！', type: 'success' });
    userStore.currentStage = '3'; 
  } catch (err) {
    console.error(err);
    showToast('提交失败，请重试');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* ================= 整体布局 ================= */
.stage-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
}

.split-layout {
  flex: 1;
  display: flex;
  overflow: hidden; 
}

/* ================= 左侧：多媒体面板 ================= */
.left-panel {
  flex: 1.1;
  background-color: #f2f3f5; 
  padding: 20px;
  overflow-y: auto;
}

.panel-header-simple {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
  font-weight: bold;
}

.media-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.media-card {
  background: #fff;
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.card-title {
  font-size: 17px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 轮播图样式 */
.photo-swipe { border-radius: 12px; overflow: hidden; position: relative; height: 240px; }
.swipe-img { width: 100%; height: 100%; display: block; cursor: pointer; }
.swipe-hint {
  position: absolute; bottom: 0; left: 0; width: 100%;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  color: white; font-size: 13px; padding: 20px 10px 10px; text-align: center; pointer-events: none; 
}

/* 视频封面样式 */
.video-cover {
  width: 100%; height: 180px;
  background: linear-gradient(135deg, #3a3a3a 0%, #121212 100%);
  border-radius: 12px; display: flex; flex-direction: column;
  justify-content: center; align-items: center; cursor: pointer;
  transition: transform 0.15s; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
}
.video-cover:active { transform: scale(0.98); }
.play-button {
  width: 64px; height: 64px; border: 2px solid rgba(255,255,255,0.9);
  border-radius: 50%; display: flex; justify-content: center; align-items: center;
  margin-bottom: 12px; background: rgba(0,0,0,0.4);
}
.cover-text { color: #fff; font-size: 14px; letter-spacing: 1px; }

/* ================= 右侧：交互面板 ================= */
.right-panel {
  flex: 1; background-color: #fff; display: flex; flex-direction: column;
  border-left: 1px solid #ebedf0; box-shadow: -4px 0 15px rgba(0,0,0,0.02);
}

.panel-header {
  font-size: 18px; font-weight: bold; padding: 20px; color: #323233;
  border-bottom: 1px solid #f2f3f5;
}

.scroll-content { flex: 1; overflow-y: auto; padding: 20px; }
.scroll-content::-webkit-scrollbar, .left-panel::-webkit-scrollbar { display: none; }

.section-title { font-size: 16px; font-weight: bold; margin-bottom: 15px; color: #333; }
.card-section { margin-bottom: 30px; }

/* 评价选项卡片 */
.custom-check-card {
  margin-bottom: 12px; padding: 16px; background-color: #f7f8fa;
  border-radius: 12px; border: 2px solid transparent; transition: all 0.2s; cursor: pointer;
}
.custom-check-card:active { transform: scale(0.98); }
.custom-check-card.is-active { background-color: #f0f9eb; border-color: #07c160; }
.check-label { display: flex; align-items: center; margin-left: 12px; }
.text { font-size: 16px; color: #323233; font-weight: 500; }
:deep(.van-checkbox__icon) { font-size: 24px; }

/* 拍照上传美化 */
.upload-wrapper { display: flex; justify-content: center; margin-top: 10px; }
.custom-uploader { width: 100%; }
.upload-trigger {
  width: 100%; height: 160px; border: 2px dashed #dcdee0;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  background-color: #f7f8fa; border-radius: 12px; transition: all 0.3s;
}
.upload-trigger:active { background-color: #f2f3f5; }
.upload-trigger.has-file { border: 2px solid #07c160; background-color: #f0f9eb; }
.upload-text { margin-top: 12px; font-size: 15px; color: #969799; font-weight: 500; }
.upload-trigger.has-file .upload-text { color: #07c160; }

.action-footer {
  padding: 20px; background-color: #fff; box-shadow: 0 -4px 15px rgba(0,0,0,0.03);
}

/* 视频弹窗 */
.video-popup { width: 90%; max-width: 500px; background: #000; border-radius: 16px; overflow: hidden; }
.popup-header { text-align: center; font-size: 16px; color: #fff; padding: 16px; background: #222; }
.full-video { width: 100%; max-height: 70vh; display: block; }

/* Vant 上传图片预览的圆角处理 */
:deep(.van-uploader__preview-image) { border-radius: 12px; width: 160px; height: 160px; object-fit: cover; }
:deep(.van-uploader__preview) { margin: 0 auto; }
</style>