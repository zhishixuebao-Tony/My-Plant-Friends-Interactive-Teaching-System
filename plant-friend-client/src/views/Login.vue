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

    <!-- 身份确认弹窗 (补救措施) -->
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
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { loginApi } from '../api/student';
import { useUserStore } from '../store/user';
import { showToast } from 'vant';

const userStore = useUserStore();
const inputId = ref('');
const tempName = ref('');
const loading = ref(false);
const showConfirm = ref(false);

// 点击“确定序号”：去后端查名字
const onPreLogin = async () => {
  if (!inputId.value) return showToast('先输入序号哦！');
  
  loading.value = true;
  try {
    const res = await loginApi(inputId.value);
    tempName.value = res.data.student_name;
    showConfirm.value = true; // 弹出确认框
  } catch (err) {
    showToast('找不到该学号，请检查！');
  } finally {
    loading.value = false;
  }
};

// 点击弹窗里的“是我”：正式存入状态并进入系统
const onFinalConfirm = () => {
  userStore.setUserInfo({
    student_id: inputId.value,
    student_name: tempName.value,
    pre_photo_url: '' // 暂时留空，之后后端会传
  });
  showToast('登录成功！');
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background-color: #f7f8fa;
}
.login-body {
  padding: 60px 30px;
}
.header-box {
  text-align: center;
  margin-bottom: 40px;
}
.form-card {
  background: white;
  padding: 30px 20px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.large-input {
  font-size: 24px;
  margin-bottom: 30px;
  border: 1px solid #ebedf0;
  border-radius: 8px;
}
.confirm-box {
  padding: 30px;
  text-align: center;
}
.name-display {
  color: #07c160;
  font-size: 32px;
  margin: 10px 0;
}
</style>