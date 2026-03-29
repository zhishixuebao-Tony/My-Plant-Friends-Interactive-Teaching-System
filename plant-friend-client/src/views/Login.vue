<template>
  <div class="login-page">
    <van-nav-bar title="我的植物朋友 - 课堂系统" />

    <div class="login-body">
      <!-- 顶部图标与欢迎语 -->
      <div class="header-box">
        <van-icon name="flower-o" size="80" color="#07c160" />
        <h1>你好，新朋友！</h1>
        <p>请输入你的序号开始植物之旅</p>
      </div>

      <!-- 输入区域 -->
      <div class="form-card">
        <van-field
          v-model="inputId"
          label="学号"
          placeholder="请输入 (如 01)"
          type="digit"
          maxlength="2"
          input-align="center"
          class="large-input"
        />
        <van-button 
          type="primary" 
          block 
          round 
          size="large" 
          @click="onPreLogin"
          :loading="loading"
        >
          确定序号
        </van-button>
      </div>
    </div>

    <!-- 身份确认弹窗 -->
    <van-dialog
      v-model:show="showConfirm"
      title="身份确认"
      show-cancel-button
      confirm-button-text="是我，开始"
      cancel-button-text="选错了"
      @confirm="onFinalConfirm"
    >
      <div class="confirm-box">
        <p>你是 <b>{{ inputId }}号</b> 的</p>
        <h2 class="name-display">{{ tempName }}</h2>
        <p>同学吗？</p>
      </div>
    </van-dialog>

    <div class="teacher-entrance" @click="showPwdDialog = true">
      [ 教师端入口 ]
    </div>

    <!-- 密码输入弹窗 -->
    <van-dialog 
      v-model:show="showPwdDialog" 
      title="教师身份验证" 
      show-cancel-button 
      @confirm="handleTeacherLogin"
    >
      <div style="padding: 20px;">
        <van-field
          v-model="adminPassword"
          type="password"
          placeholder="请输入教师管理密码"
          border
          autofocus
        />
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { loginApi } from '../api/student';
import { useUserStore } from '../store/user';
import { showToast } from 'vant';
import { useRouter } from 'vue-router'; // 导入路由
import axios from 'axios';

const userStore = useUserStore();
const router = useRouter(); // 【修正点2】初始化 router 变量
const inputId = ref('');
const tempName = ref('');
const loading = ref(false);
const showConfirm = ref(false);
const showPwdDialog = ref(false);
const adminPassword = ref('');

// --- 以下学生端逻辑保持不变 ---

const onPreLogin = async () => {
  if (!inputId.value) return showToast('先输入序号哦！');
  loading.value = true;
  try {
    const res = await loginApi(inputId.value);
    tempName.value = res.data.student_name;
    showConfirm.value = true;
  } catch (err) {
    showToast('找不到该学号，请检查！');
  } finally {
    loading.value = false;
  }
};

const onFinalConfirm = () => {
  userStore.setUserInfo({
    student_id: inputId.value,
    student_name: tempName.value,
    pre_photo_url: '' 
  });
  showToast('登录成功！');
  router.push('/stage1'); // 确保学生点击确认后也能跳转
};

// 教师登录逻辑
const handleTeacherLogin = async () => {
  if (!adminPassword.value) {
    showToast('请输入密码');
    return;
  }
  
  try {
    const res = await axios.post('/api/teacher/verify-password', {
      password: adminPassword.value
    });

    if (res.data.success) {
      showToast({ message: '验证通过，欢迎老师', type: 'success' });
      
      // 【核心修改点】跳转到带参数的地址
      window.location.href = '/?role=teacher'; 
      
    } else {
      showToast({ message: res.data.message || '密码错误', type: 'fail' });
    }
  } catch (err) {
    console.error("Teacher login error:", err);
    showToast('服务器连接失败');
  } finally {
    adminPassword.value = ''; 
  }
};
</script>

<style scoped>
/* 样式保持不变 */
.login-page { min-height: 100vh; background-color: #f7f8fa; }
.login-body { padding: 60px 30px; }
.header-box { text-align: center; margin-bottom: 40px; }
.form-card { background: white; padding: 30px 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.large-input { font-size: 24px; margin-bottom: 30px; border: 1px solid #ebedf0; border-radius: 8px; }
.confirm-box { padding: 30px; text-align: center; }
.name-display { color: #07c160; font-size: 32px; margin: 10px 0; }
.teacher-entrance { margin-top: 50px; text-align: center; color: #969799; font-size: 14px; cursor: pointer; padding: 10px; }
.teacher-entrance:active { color: #07c160; }
</style>