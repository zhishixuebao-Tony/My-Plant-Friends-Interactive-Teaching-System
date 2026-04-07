<template>
  <div class="login-page">
    <div class="top-nav">我的植物朋友 - 课堂系统</div>
    <div class="login-body">
      <div class="center-panel">
        <div class="header-box">
          <van-icon name="flower-o" size="80" color="#07c160" />
          <h1>你好，小朋友</h1>
          <p>请输入你的学号开始学习</p>
        </div>

        <div class="form-card">
          <van-field
            v-model="inputId"
            label="学号"
            placeholder="请输入两位学号，如 01"
            type="digit"
            maxlength="2"
            input-align="center"
            class="large-input"
          />
          <van-button type="primary" block round size="large" @click="onPreLogin" :loading="loading">
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
      cancel-button-text="重新输入"
      @confirm="onFinalConfirm"
    >
      <div class="confirm-box">
        <p>你是 <b>{{ inputId }}号</b> 的</p>
        <h2 class="name-display">{{ tempName }}</h2>
        <p>同学吗？</p>
      </div>
    </van-dialog>

    <van-dialog v-model:show="showPwdDialog" title="教师身份验证" show-cancel-button @confirm="handleTeacherLogin">
      <div style="padding: 20px;">
        <van-field v-model="adminPassword" type="password" placeholder="请输入教师管理密码" border autofocus />
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { showToast } from 'vant';
import axios from 'axios';

const userStore = useUserStore();
const inputId = ref('');
const tempName = ref('');
const loading = ref(false);
const showConfirm = ref(false);
const showPwdDialog = ref(false);
const adminPassword = ref('');
const studentFullData = ref(null);

const onPreLogin = async () => {
  if (!inputId.value) return showToast('请先输入学号');

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

const onFinalConfirm = () => {
  if (!studentFullData.value) return;

  // Request fullscreen inside the click-confirm gesture context.
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
  });

  userStore.setStage('welcome');
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
.login-page {
  height: 100dvh;
  background-image:
    linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(240, 251, 240, 0.2) 100%),
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

.center-panel {
  width: min(92vw, 560px);
  padding: 24px 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.65);
  box-shadow: 0 18px 34px rgba(23, 69, 38, 0.15);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.header-box {
  text-align: center;
  margin-bottom: 25px;
}

.header-box h1 {
  font-size: 28px;
  margin: 15px 0 8px;
  color: #333;
}

.header-box p {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.form-card {
  background: rgba(255, 255, 255, 0.85);
  padding: 25px 20px;
  border-radius: 16px;
  box-shadow: 0 8px 18px rgba(22, 84, 45, 0.1);
  max-width: 500px;
  margin: 20px auto 0;
  width: 100%;
}

.large-input {
  margin-bottom: 25px;
}

.confirm-box {
  padding: 25px;
  text-align: center;
}

.name-display {
  color: #07c160;
  font-size: 30px;
  margin: 15px 0;
  font-weight: bold;
}

.teacher-entrance {
  margin-top: 18px;
  text-align: center;
  color: #969799;
  font-size: 15px;
  cursor: pointer;
}



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

/* nav-strong-visible */
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

</style>




