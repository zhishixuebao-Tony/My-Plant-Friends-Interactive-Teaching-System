<template>
  <div class="stage-container">
    <van-nav-bar title="环节 5：习作定稿与荣誉证书" />

    <div class="final-layout">
      <!-- 1. 引导文字 -->
      <div class="header-section">
        <van-icon name="medal-o" size="60" color="#ee0a24" />
        <h2>恭喜你完成学习！</h2>
        <p>请拍下你修改后的【定稿作文】，领取你的专属奖状吧！</p>
      </div>

      <!-- 2. 拍照上传区 -->
      <div class="upload-section">
        <van-uploader 
          v-model="fileList" 
          :max-count="1" 
          capture="camera" 
          :after-read="afterRead"
          @delete="onDelete"
        >
          <template #default>
            <div class="final-upload-btn">
              <van-icon name="plus" size="40" />
              <span>拍摄定稿照片</span>
            </div>
          </template>
        </van-uploader>
      </div>

      <!-- 3. 提交按钮 -->
      <div class="footer">
        <van-button 
          type="danger" 
          block 
          round 
          size="large" 
          :disabled="!uploadedUrl"
          :loading="loading"
          @click="submitFinal"
        >
          完成并领取奖状
        </van-button>
      </div>
    </div>

    <!-- 4. 电子奖状弹窗 (仪式感核心) -->
    <van-popup v-model:show="showCertificate" round closeable class="cert-popup">
      <div class="certificate" id="cert">
        <div class="cert-border">
          <div class="cert-content">
            <h1>荣誉证书</h1>
            <p class="award-text">亲爱的 <b>{{ userStore.studentName }}</b> 同学：</p>
            <p class="main-text">
              你在《我的植物朋友》习作课程中，通过细致的观察和认心的修改，创作出了优秀的习作作品。
            </p>
            <p class="main-text">特授予你：</p>
            <h2 class="title-text">“自然小作家”</h2>
            <p class="date-text">202X年 X月 X日</p>
          </div>
        </div>
      </div>
      <div style="padding: 20px;">
        <van-button type="primary" block round @click="finishAll">结束学习</van-button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { uploadImageFlow, submitFinalApi } from '../api/student';
import { showToast } from 'vant';
import confetti from 'canvas-confetti'; // 引入撒花效果

const userStore = useUserStore();
const fileList = ref([]);
const uploadedUrl = ref('');
const loading = ref(false);
const showCertificate = ref(false);

const afterRead = async (file) => {
  file.status = 'uploading';
  try {
    const url = await uploadImageFlow(userStore.studentId, 'stage5_final', file.file);
    file.status = 'done';
    uploadedUrl.value = url;
    showToast('定稿照片已保存！');
  } catch (err) {
    file.status = 'failed';
    showToast('上传失败');
  }
};

const onDelete = () => {
  uploadedUrl.value = '';
};

const submitFinal = async () => {
  loading.value = true;
  try {
    await submitFinalApi(userStore.studentId, uploadedUrl.value);
    
    // 成功后触发特效
    confetti({
      particleCount: 150,
      spread: 70,
      origin: { y: 0.6 }
    });

    showCertificate.value = true; // 弹出奖状
  } catch (err) {
    showToast('网络请求失败');
  } finally {
    loading.value = false;
  }
};

const finishAll = () => {
  showToast('课程圆满结束！');
  userStore.reset(); // 重置状态回到登录页
};
</script>

<style scoped>
.final-layout { padding: 40px 20px; text-align: center; background: #fff; min-height: 90vh; }
.header-section { margin-bottom: 40px; }
.header-section h2 { color: #2c3e50; margin-top: 15px; }
.header-section p { color: #7f8c8d; font-size: 16px; }

.upload-section { margin: 40px 0; display: flex; justify-content: center; }
.final-upload-btn {
  width: 280px; height: 180px; border: 3px dashed #ebedf0;
  border-radius: 16px; display: flex; flex-direction: column;
  justify-content: center; align-items: center; color: #969799;
}

.cert-popup { width: 90%; background: transparent; }
.certificate {
  background: #fff; padding: 15px; border-radius: 8px;
  background-image: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
}
.cert-border { border: 6px double #d4af37; padding: 20px; }
.cert-content { text-align: center; font-family: "SimSun", "STSong", serif; }
.cert-content h1 { color: #b8860b; font-size: 36px; margin-bottom: 20px; border-bottom: 2px solid #d4af37; padding-bottom: 10px; }
.award-text { text-align: left; font-size: 20px; margin-bottom: 20px; }
.main-text { font-size: 18px; line-height: 1.8; text-indent: 2em; text-align: left; }
.title-text { color: #ee0a24; font-size: 32px; margin: 30px 0; }
.date-text { text-align: right; margin-top: 30px; font-size: 16px; color: #666; }

.footer { margin-top: 50px; }
</style>