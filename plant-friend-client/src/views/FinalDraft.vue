<template>
  <div class="stage-container">
    <van-nav-bar title="环节 5：定稿上传与荣誉时刻" fixed placeholder border />

    <div class="split-layout" v-if="!isAllDone">
      <!-- ================= 左侧：最后鼓励 ================= -->
      <div class="left-panel">
        <div class="reward-guide">
          <van-icon name="award" size="80" color="#f2bd27" class="award-icon" />
          <h2 class="guide-title">恭喜你，小作家！</h2>
          <p class="guide-desc">
            你已经完成了对植物朋友的全部观察与写作。
            <br><br>
            请将你**最满意、字迹最工整**的定稿作文拍照上传。
            <br><br>
            完成后，你将获得属于你的<b>“小小植物学家”</b>荣誉奖状！
          </p>
        </div>
      </div>

      <!-- ================= 右侧：定稿拍照上传区 ================= -->
      <div class="right-panel">
        <div class="panel-header">📸 拍摄定稿作文</div>
        
        <div class="scroll-content">
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
                  <van-icon name="medal-o" size="50" :color="fileList.length > 0 ? '#f2bd27' : '#969799'" />
                  <span class="upload-text">{{ fileList.length > 0 ? '重新拍摄定稿' : '点击拍摄定稿照片' }}</span>
                </div>
              </template>
            </van-uploader>
          </div>
          <div class="success-text" v-if="isUploadSuccess">✨ 太棒了！定稿已就绪</div>
        </div>

        <div class="action-footer">
          <van-button 
            type="warning" 
            block 
            round 
            size="large" 
            @click="onFinalSubmit"
            :loading="isSubmitting"
            :disabled="!isUploadSuccess"
            loading-text="正在领取奖状..."
          >
            完成写作，领取奖状
          </van-button>
        </div>
      </div>
    </div>

    <!-- ================= 核心：电子奖状与撒花展示区 ================= -->
    <div class="certificate-container" v-if="isAllDone">
      <div class="certificate-card">
        <div class="cert-border">
          <div class="cert-content">
            <div class="cert-header">荣 誉 奖 状</div>
            <div class="cert-body">
              <p class="cert-name"><span>{{ userStore.studentName }}</span> 同学：</p>
              <p class="cert-text">
                在《我的植物朋友》互动课堂中，你通过细致的观察和生动的描写，成功完成了一篇优秀的习作。表现出色，特发此证，以资鼓励！
              </p>
              <p class="cert-title">小小植物学家</p>
            </div>
            <div class="cert-footer">
              <p>语文互动课堂项目组</p>
              <p>{{ currentDate }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="final-actions">
        <van-button icon="share-o" type="primary" round plain @click="shareCert">分享我的荣誉</van-button>
        <p class="final-tip">老师在大屏上也能看到你的作品哦！</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { uploadImageFlow } from '../api/student'; 
import axios from 'axios';
import { showToast } from 'vant';
import confetti from 'canvas-confetti'; // 导入撒花插件

const userStore = useUserStore();
const fileList = ref([]);
const isSubmitting = ref(false);
const isUploadSuccess = ref(false);
const uploadedUrl = ref('');
const isAllDone = ref(false); // 是否展示奖状
const currentDate = new Date().toLocaleDateString();

const afterRead = async (file) => {
  file.status = 'uploading';
  try {
    const url = await uploadImageFlow(userStore.studentId, 'stage5_final', file.file);
    file.status = 'done';
    uploadedUrl.value = url;
    isUploadSuccess.value = true;
    showToast({ message: '定稿已存入云端', type: 'success' });
  } catch (err) {
    file.status = 'failed';
    showToast('上传失败');
  }
};

const onDelete = () => { isUploadSuccess.value = false; uploadedUrl.value = ''; };

// --- 最终提交并触发撒花 ---
const onFinalSubmit = async () => {
  isSubmitting.value = true;
  try {
    await axios.post('/api/student/stage5/final', {
      student_id: userStore.studentId,
      img_url: uploadedUrl.value
    });

    // 1. 切换状态显示奖状
    isAllDone.value = true;

    // 2. 触发撒花特效 (循环撒三次，更震撼)
    triggerConfetti();
    
    showToast({ message: '太棒了！你真了不起！', type: 'success' });
  } catch (err) {
    showToast('提交失败');
  } finally {
    isSubmitting.value = false;
  }
};

// 撒花函数
const triggerConfetti = () => {
  const duration = 3 * 1000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

  const interval = setInterval(function() {
    const timeLeft = animationEnd - Date.now();
    if (timeLeft <= 0) return clearInterval(interval);

    const particleCount = 50 * (timeLeft / duration);
    confetti({ ...defaults, particleCount, origin: { x: Math.random(), y: Math.random() - 0.2 } });
  }, 250);
};

const shareCert = () => showToast('老师已在主屏幕展示你的荣誉！');
</script>

<style scoped>
.stage-container { height: 100vh; display: flex; flex-direction: column; background-color: #f7f8fa; }
.split-layout { flex: 1; display: flex; overflow: hidden; }

/* 左侧奖励引导 */
.left-panel { flex: 1; background: linear-gradient(135deg, #fff9e6 0%, #fff1c1 100%); display: flex; justify-content: center; align-items: center; padding: 30px; }
.reward-guide { text-align: center; }
.award-icon { filter: drop-shadow(0 4px 10px rgba(242,189,39,0.3)); animation: float 3s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
.guide-title { font-size: 26px; color: #856404; margin: 20px 0; }
.guide-desc { font-size: 16px; color: #856404; line-height: 1.8; opacity: 0.8; }

/* 右侧上传区 */
.right-panel { flex: 1.2; background-color: #fff; display: flex; flex-direction: column; border-left: 1px solid #ebedf0; }
.panel-header { font-size: 20px; font-weight: bold; padding: 25px; color: #323233; }
.scroll-content { flex: 1; padding: 40px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.upload-trigger { width: 100%; height: 260px; border: 3px dashed #dcdee0; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #f7f8fa; border-radius: 16px; }
.upload-trigger.has-file { border-color: #f2bd27; background-color: #fffdf5; }
.upload-text { margin-top: 15px; font-size: 18px; color: #969799; font-weight: bold; }
.upload-trigger.has-file .upload-text { color: #f2bd27; }

/* ================= 奖状样式 ================= */
.certificate-container { flex: 1; background: #555; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
.certificate-card { width: 90%; max-width: 600px; background: #fff; padding: 15px; border-radius: 4px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); transform: rotate(-1deg); }
.cert-border { border: 10px double #f2bd27; padding: 20px; height: 100%; }
.cert-content { border: 2px solid #f2bd27; padding: 30px; background: #fffcf5; text-align: center; position: relative; }
.cert-header { font-size: 40px; color: #d4237a; font-family: "SimSun", serif; font-weight: bold; margin-bottom: 30px; letter-spacing: 10px; }
.cert-body { text-align: left; line-height: 2; color: #333; }
.cert-name { font-size: 22px; margin-bottom: 15px; }
.cert-name span { text-decoration: underline; font-weight: bold; padding: 0 10px; }
.cert-text { text-indent: 2em; font-size: 18px; margin-bottom: 30px; }
.cert-title { text-align: center; font-size: 32px; color: #f2bd27; font-weight: bold; margin-top: 40px; font-family: "KaiTi"; }
.cert-footer { text-align: right; margin-top: 40px; font-size: 16px; }

.final-actions { margin-top: 30px; text-align: center; color: #fff; }
.final-tip { margin-top: 15px; opacity: 0.7; font-size: 14px; }
</style>