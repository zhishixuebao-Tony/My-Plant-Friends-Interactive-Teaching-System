<template>
  <div class="login-page">
    <van-nav-bar title="我的植物朋友 - 课堂系统" />

    <div class="login-body">
      <div class="header-box">
        <van-icon name="flower-o" size="80" color="#07c160" />
        <h1>你好，新朋友！</h1>
        <p>请输入你的序号开始植物之旅</p>
      </div>

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

// 【关键修复】定义一个响应式对象，用来跨函数存储后端返回的学生完整数据
const studentFullData = ref(null);

const onPreLogin = async () => {
  if (!inputId.value) return showToast('先输入序号哦！');
  
  let sid = inputId.value;
  if (sid.length === 1) sid = '0' + sid;
  inputId.value = sid;

  loading.value = true;
  try {
    const res = await axios.post('/api/student/stage0/login', { 
      student_id: sid 
    });
    
    // 解析后端返回的数据
    if (res.data && res.data.status === 'success') {
      studentFullData.value = res.data.data; 
      tempName.value = studentFullData.value.student_name;
      showConfirm.value = true;
    } else {
      showToast('学号不存在，请联系老师');
    }
  } catch (err) {
    console.error("登录接口报错详情:", err);
    // 如果 F12 控制台显示 422，说明参数格式不对；如果显示 404，说明路径不对
    showToast('网络请求失败，请按 F12 检查接口路径');
  } finally {
    loading.value = false;
  }
};

const onFinalConfirm = () => {
  if (!studentFullData.value) return;

  userStore.setUserInfo({
    student_id: studentFullData.value.student_id,
    student_name: studentFullData.value.student_name,
    pre_plant_1: studentFullData.value.pre_plant_1, 
    pre_plant_2: studentFullData.value.pre_plant_2,
    pre_plant_3: studentFullData.value.pre_plant_3
  });
  
  showToast('登录成功！');
  userStore.setStage('1'); 
};

const handleTeacherLogin = async () => {
  if (!adminPassword.value) return showToast('请输入密码');
  try {
    const res = await axios.post('/api/teacher/verify-password', {
      password: adminPassword.value
    });
    if (res.data.success) {
      showToast({ message: '验证通过', type: 'success' });
      window.location.href = '/?role=teacher'; 
    } else {
      showToast({ message: res.data.message || '密码错误', type: 'fail' });
    }
  } catch (err) {
    showToast('服务器连接失败');
  } finally {
    adminPassword.value = ''; 
  }
};
</script>

<style scoped>
/* 保持原样 */
.login-page { 
  height: 100%;
  background-color: #f7f8fa;
  display: flex;
  flex-direction: column;
}
.login-body { 
  flex: 1;
  padding: 60px 30px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
.header-box { text-align: center; margin-bottom: 40px; }
.form-card { 
  background: white; 
  padding: 30px 20px; 
  border-radius: 16px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-top: auto;
}
.large-input { font-size: 24px; margin-bottom: 30px; border: 1px solid #ebedf0; border-radius: 8px; }
.confirm-box { padding: 30px; text-align: center; }
.name-display { color: #07c160; font-size: 32px; margin: 10px 0; }
.teacher-entrance { 
  margin-top: 20px; 
  margin-bottom: 20px;
  text-align: center; 
  color: #969799; 
  font-size: 14px; 
  cursor: pointer; 
  padding: 10px;
  flex-shrink: 0;
}
.teacher-entrance:active { color: #07c160; }
</style>