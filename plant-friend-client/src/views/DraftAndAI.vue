<template>
  <div class="stage-container">
    <van-nav-bar title="环节 3：我的习作初稿与 AI 老师" />

    <div class="split-layout">
      <!-- 左侧：拍照上传 -->
      <div class="left-panel">
        <div class="panel-header">📸 拍摄我的习作初稿</div>
        <div class="upload-box">
          <van-uploader 
            v-model="fileList" 
            :max-count="1" 
            capture="camera" 
            :after-read="afterRead"
          >
            <template #default>
              <div class="big-upload-btn">
                <van-icon name="photograph" size="50" />
                <p>点击拍照上传初稿</p>
              </div>
            </template>
          </van-uploader>
        </div>
      </div>

      <!-- 右侧：AI 老师反馈 -->
      <div class="right-panel">
        <div class="panel-header">🤖 AI 老师的修改建议</div>
        
        <div class="ai-content">
          <!-- 没上传时提示 -->
          <div v-if="!uploadedUrl" class="empty-tip">请先在左侧拍照上传作文哦！</div>
          
          <!-- 上传后显示 AI 按钮 -->
          <van-button 
            v-if="uploadedUrl && !aiFeedback" 
            type="success" 
            block 
            round 
            icon="gem-o"
            @click="getAiFeedback"
            :loading="aiLoading"
            loading-text="AI 老师正在认真阅读..."
          >
            获取 AI 作文评价
          </van-button>

          <!-- 展示评语 -->
          <div v-if="aiFeedback" class="paper-feedback">
            <div class="paper-title">批改建议：</div>
            <p class="paper-text">{{ aiFeedback }}</p>
          </div>
        </div>

        <div class="footer" v-if="aiFeedback">
          <van-button type="primary" block round size="large" @click="goNext">
            看懂了，去学习魔法资源包
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { uploadImageFlow, submitDraftAiApi } from '../api/student';
import { showToast } from 'vant';

const userStore = useUserStore();
const fileList = ref([]);
const uploadedUrl = ref('');
const aiFeedback = ref('');
const aiLoading = ref(false);

const afterRead = async (file) => {
  file.status = 'uploading';
  try {
    const url = await uploadImageFlow(userStore.studentId, 'stage3_draft', file.file);
    file.status = 'done';
    uploadedUrl.value = url;
    showToast('初稿上传成功！');
  } catch (err) {
    file.status = 'failed';
    showToast('上传失败');
  }
};

const getAiFeedback = async () => {
  aiLoading.value = true;
  try {
    const res = await submitDraftAiApi(userStore.studentId, uploadedUrl.value);
    aiFeedback.value = res.data.ai_feedback;
  } catch (err) {
    showToast('AI 老师开小差了，请重试');
  } finally {
    aiLoading.value = false;
  }
};

const goNext = () => {
  userStore.currentStage = '4';
};
</script>

<style scoped>
.split-layout { display: flex; flex: 1; height: 90vh; }
.left-panel { flex: 1; padding: 20px; background: #fdfdfd; border-right: 1px solid #eee; display: flex; flex-direction: column; }
.upload-box { flex: 1; display: flex; justify-content: center; align-items: center; }
.big-upload-btn { width: 260px; height: 350px; border: 3px dashed #ddd; border-radius: 15px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #999; }
.right-panel { flex: 1; padding: 30px; display: flex; flex-direction: column; background: #fff; }
.ai-content { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.empty-tip { text-align: center; color: #999; font-size: 18px; }
.paper-feedback { background: #fffef0; padding: 25px; border-radius: 4px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); border-left: 5px solid #ffcd3c; min-height: 200px; }
.paper-title { font-weight: bold; font-size: 18px; margin-bottom: 10px; color: #b8860b; }
.paper-text { font-size: 20px; line-height: 1.6; color: #444; }
.footer { margin-top: 20px; }
</style>