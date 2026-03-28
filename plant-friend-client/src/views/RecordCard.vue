<template>
  <div class="stage-container">
    <van-nav-bar title="环节 2：我的记录卡观察与修改" />

    <div class="split-layout">
      <!-- 左侧：回顾课前素材 (图片+视频) -->
      <div class="left-panel">
        <div class="panel-header">我的植物朋友档案</div>
        <div class="media-list">
          <!-- 图片展示 -->
          <div class="media-item">
            <p class="label">📸 观察照片</p>
            <van-image :src="userStore.prePhotoUrl" fit="contain" radius="8" @click="showImagePreview" />
          </div>
          <!-- 视频展示 (如果是真实视频地址，可换成 <video>) -->
          <div class="media-item">
            <p class="label">🎥 观察视频</p>
            <div class="video-mock">
              <van-icon name="play-circle-o" size="40" color="#999" />
              <span>点击播放植物视频</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：评价与上传 -->
      <div class="right-panel">
        <div class="panel-header">自评与修改记录卡上传</div>
        
        <div class="scroll-content">
          <!-- 1. 评价维度勾选 -->
          <div class="card-section">
            <div class="section-title">评价维度：</div>
            <van-checkbox-group v-model="evalChecks">
              <van-checkbox name="评价一" class="custom-check">评价一：能真实记录特点</van-checkbox>
              <van-checkbox name="评价二" class="custom-check">评价二：能描写出植物感受</van-checkbox>
              <van-checkbox name="评价三" class="custom-check">评价三：书写认真工整</van-checkbox>
            </van-checkbox-group>
          </div>

          <!-- 2. 拍照上传 -->
          <div class="card-section">
            <div class="section-title">拍照上传修改后的记录卡：</div>
            <van-uploader 
              v-model="fileList" 
              :max-count="1" 
              capture="camera" 
              :after-read="afterRead"
              @delete="onDelete"
            >
              <template #default>
                <div class="upload-trigger">
                  <van-icon name="photograph" size="30" />
                  <span>点击拍照</span>
                </div>
              </template>
            </van-uploader>
          </div>
        </div>

        <!-- 3. 下一步按钮 -->
        <div class="footer">
          <van-button 
            type="primary" 
            block 
            round 
            size="large" 
            @click="onFinalSubmit"
            :loading="isSubmitting"
            :disabled="!isUploadSuccess"
          >
            提交并进入环节 3
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { uploadImageFlow } from '../api/student'; // 确保你之前封装了这个函数
import axios from 'axios';
import { showToast, showImagePreview as vantPreview } from 'vant';

const userStore = useUserStore();
const evalChecks = ref([]);
const fileList = ref([]);
const isSubmitting = ref(false);
const isUploadSuccess = ref(false);
const uploadedUrl = ref('');

// 放大查看图片
const showImagePreview = () => {
  vantPreview([userStore.prePhotoUrl]);
};

// 核心逻辑：拍照后自动触发直传 OSS
const afterRead = async (file) => {
  file.status = 'uploading';
  file.message = '正在上传云端...';
  
  try {
    // 调用 OSS 直传工具 (参数：学号, 环节名, 文件对象)
    const url = await uploadImageFlow(userStore.studentId, 'stage2_record', file.file);
    
    file.status = 'done';
    file.message = '上传成功';
    uploadedUrl.value = url;
    isUploadSuccess.value = true;
    showToast('记录卡已成功存入云端');
  } catch (err) {
    file.status = 'failed';
    file.message = '上传失败';
    showToast('云端连接失败，请检查网络');
  }
};

const onDelete = () => {
  isUploadSuccess.value = false;
  uploadedUrl.value = '';
};

// 提交最终数据到后端 MongoDB
const onFinalSubmit = async () => {
  if (!isUploadSuccess.value) return showToast('请先拍照上传记录卡');
  
  isSubmitting.value = true;
  try {
    await axios.post('/api/student/stage2/record-card', {
      student_id: userStore.studentId,
      checks: evalChecks.value,
      img_url: uploadedUrl.value
    });
    
    showToast('提交成功！');
    userStore.currentStage = '3'; // 进入环节 3
  } catch (err) {
    showToast('提交失败，请重试');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.split-layout { display: flex; flex: 1; overflow: hidden; background: #fff; }
.left-panel { flex: 1; padding: 20px; background: #f0f2f5; border-right: 1px solid #ddd; }
.right-panel { flex: 1; display: flex; flex-direction: column; }
.scroll-content { flex: 1; overflow-y: auto; padding: 25px; }

.panel-header { font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #2c3e50; }
.media-item { margin-bottom: 20px; }
.label { color: #666; margin-bottom: 8px; font-size: 14px; }
.video-mock { 
  height: 120px; background: #d1d4d9; border-radius: 8px;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
}

.card-section { margin-bottom: 30px; }
.section-title { font-size: 16px; font-weight: bold; margin-bottom: 15px; }
.custom-check { margin-bottom: 12px; font-size: 18px; }

.upload-trigger {
  width: 120px; height: 120px; border: 2px dashed #ccc;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  color: #999; border-radius: 8px;
}
.footer { padding: 20px; border-top: 1px solid #eee; }
</style>