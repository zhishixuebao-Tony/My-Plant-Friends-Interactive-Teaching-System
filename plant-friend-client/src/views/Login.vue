<template>
  <div class="login-page">
    <div class="top-nav">我的植物朋友 - 课堂系统</div>
    <div class="login-body">
      <div class="center-panel">
        <div class="header-box">
          <van-icon name="flower-o" size="80" />
          <h1>你好，小朋友</h1>
          <p>请选择你的学号开始学习</p>
        </div>

        <div class="form-card">
          <button type="button" class="id-picker-trigger large-input" @click="showIdPicker = true">
            <span class="picker-label">学号</span>
            <span class="picker-value">{{ inputId ? `${Number(inputId)}号` : '点击选择学号' }}</span>
          </button>
          <van-button type="primary" block round size="large" @click="onPreLogin" :loading="loading" class="btn-primary-3d">
            确定学号
          </van-button>
        </div>
      </div>

      <div class="teacher-entrance" @click="showPwdDialog = true">[ 教师端入口 ]</div>
    </div>

    <van-dialog
      v-model:show="showConfirm"
      title="身份确认"
      show-cancel-button
      confirm-button-text="是我，开始学习"
      cancel-button-text="重新选择"
      @confirm="onFinalConfirm"
      class="handbook-dialog"
    >
      <div class="confirm-box">
        <p>你是 <b>{{ Number(inputId) }}号</b> 的</p>
        <h2 class="name-display">{{ tempName }}</h2>
        <p>同学吗？</p>
      </div>
    </van-dialog>

    <van-dialog v-model:show="showPwdDialog" title="教师身份验证" show-cancel-button @confirm="handleTeacherLogin" class="handbook-dialog">
      <div style="padding: 20px;">
        <van-field v-model="adminPassword" type="password" placeholder="请输入教师管理密码" border autofocus />
      </div>
    </van-dialog>

    <van-popup v-model:show="showIdPicker" round position="bottom" :style="{ height: '78vh' }">
      <div class="id-picker-panel">
        <div class="id-picker-title">请选择学号</div>
        <div class="id-picker-subtitle">1-50 为学生，51-70 为评委</div>

        <div class="id-group-title">学生学号（1-50）</div>
        <div class="id-grid">
          <button
            v-for="id in studentIds"
            :key="`student-${id}`"
            type="button"
            class="id-chip"
            :class="{ active: Number(inputId) === id }"
            @click="selectId(id)"
          >
            {{ id }}
          </button>
        </div>

        <div class="id-group-title judge">评委学号（51-70）</div>
        <div class="id-grid">
          <button
            v-for="id in judgeIds"
            :key="`judge-${id}`"
            type="button"
            class="id-chip judge-chip"
            :class="{ active: Number(inputId) === id }"
            @click="selectId(id)"
          >
            {{ id }}
          </button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useUserStore } from '../store/user';
import { showToast } from 'vant';
import axios from 'axios';
import { scheduleStudentPreloadAfterWelcome } from '../utils/imagePreloader';

const userStore = useUserStore();
const inputId = ref('');
const tempName = ref('');
const loading = ref(false);
const showConfirm = ref(false);
const showPwdDialog = ref(false);
const adminPassword = ref('');
const studentFullData = ref(null);
const showIdPicker = ref(false);
const studentIds = computed(() => Array.from({ length: 50 }, (_, i) => i + 1));
const judgeIds = computed(() => Array.from({ length: 20 }, (_, i) => i + 51));

const selectId = (id) => {
  inputId.value = String(id).padStart(2, '0');
  showIdPicker.value = false;
};

const onPreLogin = async () => {
  if (!inputId.value) return showToast('请先选择学号');

  let sid = inputId.value.trim();
  if (sid.length === 1) sid = `0${sid}`;
  inputId.value = sid;

  loading.value = true;
  try {
    const res = await axios.post('/api/student/stage0/login', { student_id: sid });

    if (res.data?.status === 'success') {
      studentFullData.value = res.data.data;
      tempName.value = studentFullData.value.student_name || '';
      showConfirm.value = true;
    } else {
      showToast('学号不存在，请联系老师');
    }
  } catch (err) {
    console.error('登录接口报错详情:', err);
    showToast('网络请求失败，请重试');
  } finally {
    loading.value = false;
  }
};

const onFinalConfirm = async () => {
  if (!studentFullData.value) return;

  if (document.fullscreenElement !== document.documentElement) {
    document.documentElement.requestFullscreen({ navigationUI: 'hide' }).catch((error) => {
      console.warn('Fullscreen request failed on login confirm:', error);
    });
  }

  userStore.setUserInfo({
    student_id: studentFullData.value.student_id,
    student_name: studentFullData.value.student_name,
    pre_plant_1: studentFullData.value.pre_plant_1,
    pre_plant_2: studentFullData.value.pre_plant_2,
    pre_plant_3: studentFullData.value.pre_plant_3,
    pre_record_card: studentFullData.value.pre_record_card,
  });

  try {
    await axios.post('/api/student/stage0/confirm-login', {
      student_id: studentFullData.value.student_id,
    });
  } catch (err) {
    console.error('确认登录失败:', err);
  }

  userStore.setStage('welcome');
  scheduleStudentPreloadAfterWelcome(studentFullData.value, { delayMs: 120 });
  window.dispatchEvent(new Event('student-login-success'));
  showToast('登录成功');
};

const handleTeacherLogin = async () => {
  const password = (adminPassword.value || '').trim();
  if (!password) return showToast('请输入密码');

  try {
    const res = await axios.post('/api/teacher/verify-password', { password });
    if (res.data?.success) {
      showToast({ message: '验证通过', type: 'success' });
      window.location.href = '/?role=teacher';
    } else {
      showToast({ message: res.data?.message || '密码错误', type: 'fail' });
    }
  } catch (err) {
    showToast('服务器连接失败');
  } finally {
    adminPassword.value = '';
  }
};
</script>

<style scoped>
/* =========== 全局背景不变 =========== */
.login-page {
  height: 100dvh;
  background-image:
    linear-gradient(180deg, rgba(0, 0, 0, 0.34) 0%, rgba(0, 0, 0, 0.34) 100%),
    url('/login/background.jpg');
  background-color: #f7f8fa;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.login-body {
  flex: 1;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* =========== 手账风：主面板 =========== */
.center-panel {
  width: min(92vw, 560px);
  padding: 32px 24px;
  border-radius: 20px;
  background: #FDFBF2; /* 护眼暖米黄（道林纸色） */
  border: 2px dashed #D4CBB3; /* 手账虚线边框 */
  box-shadow: 4px 12px 30px rgba(90, 76, 67, 0.12); /* 偏棕色的柔和阴影，取代冷黑色阴影 */
  position: relative;
  margin-top: 15px;
}

/* 纯CSS装饰：手账顶部的半透明绿胶带 */
.center-panel::before {
  content: '';
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%) rotate(-2deg);
  width: 140px;
  height: 28px;
  background-color: rgba(135, 179, 146, 0.65); /* 半透明森系绿 */
  box-shadow: 1px 2px 4px rgba(0,0,0,0.06);
  border-radius: 2px;
  z-index: 10;
  backdrop-filter: blur(2px);
}

.header-box {
  text-align: center;
  margin-bottom: 25px;
}

/* 强制覆盖图标颜色为森绿 */
:deep(.van-icon) {
  color: #5C8D6D !important; 
}

.header-box h1 {
  font-size: 28px;
  margin: 15px 0 8px;
  color: #5A4C43; /* 深灰棕色（代替刺眼的纯黑） */
  font-weight: 800;
  letter-spacing: 2px;
}

.header-box p {
  font-size: 16px;
  color: #8A7C73; /* 次要文字变柔和 */
  margin: 0;
}

/* =========== 手账风：内部表单区 =========== */
.form-card {
  background: #F6F4E8; /* 比外层底色稍深一点，制造叠纸层级感 */
  padding: 25px 20px;
  border-radius: 16px;
  border: 1px solid #EBE4D5;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.9), 0 4px 10px rgba(0, 0, 0, 0.03); /* 微内阴影 */
  max-width: 500px;
  margin: 20px auto 0;
  width: 100%;
}

.large-input {
  margin-bottom: 25px;
}

/* 立体感输入框（贴纸感） */
.id-picker-trigger {
  width: 100%;
  border: 2px solid #E3DBC7;
  border-radius: 14px;
  background: #FDFBF2;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  box-shadow: 0 4px 0 #E3DBC7; /* 坚实的底部阴影 */
  transition: all 0.1s ease;
}

/* 模拟按压的物理反馈 */
.id-picker-trigger:active {
  transform: translateY(4px);
  box-shadow: 0 0 0 #E3DBC7;
}

.picker-label {
  color: #8A7C73;
  font-size: 16px;
  font-weight: bold;
}

.picker-value {
  color: #5C8D6D; /* 绿色高亮选中的数值 */
  font-size: 19px;
  font-weight: 900;
  font-family: monospace, sans-serif;
}

/* =========== 3D立体大按钮 =========== */
:deep(.van-button--primary) {
  background-color: #5C8D6D !important;
  border-color: #5C8D6D !important;
  box-shadow: 0 5px 0 #3A664A !important; /* 墨绿色阴影 */
  font-size: 18px !important;
  font-weight: bold !important;
  letter-spacing: 2px;
  transition: all 0.1s !important;
}

:deep(.van-button--primary:active) {
  transform: translateY(5px) !important;
  box-shadow: 0 0 0 #3A664A !important;
}


/* =========== 教师入口（手绘下划线风格） =========== */
.teacher-entrance {
  margin-top: 24px;
  text-align: center;
  color: #A3968C;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  text-decoration: underline dashed #A3968C;
  text-underline-offset: 6px;
}


/* =========== 确认弹窗手账化 =========== */
:deep(.handbook-dialog) {
  background-color: #FDFBF2;
  border-radius: 20px;
  border: 2px dashed #D4CBB3;
}
:deep(.van-dialog__header) {
  color: #5A4C43;
  font-weight: bold;
}

.confirm-box {
  padding: 25px;
  text-align: center;
}

.confirm-box p {
  color: #5A4C43;
  font-size: 16px;
}

.name-display {
  color: #5C8D6D;
  font-size: 34px;
  margin: 15px 0;
  font-weight: 900;
  text-shadow: 1px 1px 0 #E3DBC7; /* 文字厚度感 */
}


/* =========== 顶部导航（保留原始） =========== */
.top-nav {
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border-bottom: 1px solid #ebedf0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  font-size: 16px;
  font-weight: 700;
  color: #323233;
  flex-shrink: 0;
}

.top-nav {
  min-height: 56px !important;
  padding: max(0px, env(safe-area-inset-top)) 16px 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
  border-bottom: 1px solid #dfe6f3;
  box-shadow: 0 3px 10px rgba(30, 60, 120, 0.08);
  font-size: 17px;
  font-weight: 700;
  color: #1f2d3d;
  letter-spacing: 0.2px;
  flex-shrink: 0;
}


/* =========== 底部抽屉面板（学号选择器） =========== */
.id-picker-panel {
  height: 100%;
  overflow-y: auto;
  padding: 24px 20px 30px;
  box-sizing: border-box;
  background-color: #FDFBF2; /* 抽屉背景纸张化 */
}

.id-picker-title {
  font-size: 22px;
  font-weight: 800;
  color: #5A4C43;
  text-align: center;
}

.id-picker-subtitle {
  margin-top: 6px;
  margin-bottom: 16px;
  text-align: center;
  font-size: 14px;
  color: #8A7C73;
}

.id-group-title {
  margin-top: 16px;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 800;
  color: #5C8D6D;
  display: inline-block;
  border-bottom: 2px dashed #D4CBB3; /* 标题底部加虚线，像笔记本 */
  padding-bottom: 4px;
}

.id-group-title.judge {
  color: #C07953; /* 评委色改为温和陶土橘 */
}

.id-grid {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 12px;
}

/* 学号小标签 - 贴纸风格 */
.id-chip {
  border: 1px solid #D4CBB3;
  border-radius: 10px; /* 方正一点更像贴纸 */
  background: #F6F4E8;
  color: #5A4C43;
  font-size: 19px;
  font-weight: 800;
  min-height: 52px;
  padding: 10px 0;
  cursor: pointer;
  box-shadow: 2px 2px 0 rgba(212, 203, 179, 0.6); /* 立体投影 */
  transition: all 0.15s ease;
}

.id-chip.judge-chip {
  background: #FBF4F1;
  border-color: #E6D0C5;
  color: #9C654D;
  box-shadow: 2px 2px 0 rgba(230, 208, 197, 0.6);
}

/* 选中状态：按下去变成绿贴纸/橘贴纸 */
.id-chip.active {
  background: #5C8D6D !important;
  color: #FDFBF2 !important;
  border-color: #3A664A !important;
  box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.2) !important; /* 内阴影模拟按压 */
  transform: translateY(2px) translateX(2px); /* 按下去的位置偏移 */
}

.id-chip.judge-chip.active {
  background: #C07953 !important;
  border-color: #A35C36 !important;
}

@media (max-width: 900px) {
  .id-grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}
</style>
