<template>
  <div class="app-main">
    
    <!-- 1. 顶部调试工具栏 (仅在开发时开启，为了方便你快速测试各环节) -->
    <div class="dev-toolbar" v-if="!isTeacherMode">
      <span>环节跳转: </span>
      <button @click="userStore.currentStage = '0'">登录</button>
      <button @click="userStore.currentStage = '1'">1感官</button>
      <button @click="userStore.currentStage = '2'">2记录</button>
      <button @click="userStore.currentStage = '3'">3初稿</button>
      <button @click="userStore.currentStage = '4'">4资源</button>
      <button @click="userStore.currentStage = '5'">5定稿</button>
      <span style="margin-left: 10px; color: #f0ad4e;">当前: {{ userStore.currentStage }}</span>
    </div>

    <!-- 2. 核心内容区域 -->
    <div class="content-wrapper">
      
      <!-- 教师端大屏 (通过 URL 上的 ?role=teacher 判断) -->
      <TeacherDash v-if="isTeacherMode" />

      <!-- 学生端：各个环节页面 -->
      <template v-else>
        <!-- 环节 0: 登录 -->
        <Login v-if="userStore.currentStage === '0'" />

        <!-- 环节 1: 感官自评 -->
        <Sensory v-else-if="userStore.currentStage === '1'" />

        <!-- 环节 2: 记录卡修改与上传 -->
        <RecordCard v-else-if="userStore.currentStage === '2'" />

        <!-- 环节 3: 习作初稿与 AI 评价 -->
        <DraftAndAI v-else-if="userStore.currentStage === '3'" />

        <!-- 环节 4: 魔法资源包与习题 -->
        <ResourcePack v-else-if="userStore.currentStage === '4'" />

        <!-- 环节 5: 最终定稿 -->
        <FinalDraft v-else-if="userStore.currentStage === '5'" />
        
        <!-- 兜底显示 -->
        <div v-else class="placeholder">
          <h2>系统状态异常</h2>
          <van-button type="default" @click="userStore.reset()">返回登录</van-button>
        </div>
      </template>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from './store/user';
// 引入所有子组件
import Login from './views/Login.vue';
import Sensory from './views/Sensory.vue';
import RecordCard from './views/RecordCard.vue';
import DraftAndAI from './views/DraftAndAI.vue';
import ResourcePack from './views/ResourcePack.vue';
import FinalDraft from './views/FinalDraft.vue';
import TeacherDash from './views/TeacherDash.vue';

// 必须要保证 Pinia 的 store 是在 setup 函数内部、且没有发生任何挂载前调用
const userStore = useUserStore();

// 判断是否为教师模式
const isTeacherMode = ref(false);

onMounted(() => {
  // 当页面 DOM 挂载完成后，再去读取 URL 参数，这绝对安全
  const params = new URLSearchParams(window.location.search);
  isTeacherMode.value = params.get('role') === 'teacher';
});
</script>

<style>
/* 基础复位 */
body { margin: 0; background-color: #f7f8fa; }

.app-main {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 调试工具栏样式：固定在顶部，方便你测试 */
.dev-toolbar {
  background: #333;
  color: white;
  padding: 8px;
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  z-index: 300;
}

.dev-toolbar button {
  padding: 2px 8px;
  background: #555;
  color: white;
  border: 1px solid #777;
  cursor: pointer;
}

.placeholder {
  padding: 100px;
  text-align: center;
}
</style>