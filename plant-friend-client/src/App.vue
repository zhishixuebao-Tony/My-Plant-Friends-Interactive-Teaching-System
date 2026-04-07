<template>
  <div class="app-main">
    <div class="content-wrapper">
      <TeacherDash v-if="isTeacherMode" />

      <template v-else>
        <div v-if="showStudentStageNav" class="student-stage-nav">
          <button
            v-for="item in stageNavItems"
            :key="item.stage"
            type="button"
            class="stage-nav-btn"
            :class="{ active: userStore.currentStage === item.stage }"
            @click="goToStage(item.stage)"
          >
            {{ item.label }}
          </button>
        </div>

        <Login v-if="userStore.currentStage === '0'" />
        <Welcome v-else-if="userStore.currentStage === 'welcome'" />
        <Sensory v-else-if="userStore.currentStage === '1'" />
        <RecordCard v-else-if="userStore.currentStage === '2'" />
        <ViewRecordCards v-else-if="userStore.currentStage === '3'" />
        <ResourcePack v-else-if="userStore.currentStage === '4'" />
        <FinalDraft v-else-if="userStore.currentStage === '5'" />

        <div v-else class="placeholder">
          <h2>系统状态异常</h2>
          <van-button type="default" @click="userStore.reset()">返回登录</van-button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useUserStore } from './store/user';
import FinalDraft from './views/FinalDraft.vue';
import Login from './views/Login.vue';
import RecordCard from './views/RecordCard.vue';
import ResourcePack from './views/ResourcePack.vue';
import Sensory from './views/Sensory.vue';
import TeacherDash from './views/TeacherDash.vue';
import ViewRecordCards from './views/ViewRecordCards.vue';
import Welcome from './views/Welcome.vue';

const userStore = useUserStore();
const isTeacherMode = ref(false);

const isStudentFlowActive = computed(() => !isTeacherMode.value && userStore.currentStage !== '0');
const showStudentStageNav = computed(() => !isTeacherMode.value);

const stageNavItems = [
  { stage: '0', label: '登录页' },
  { stage: 'welcome', label: '欢迎页' },
  { stage: '1', label: '环节1 观察' },
  { stage: '3', label: '环节2 查看记录卡' },
  { stage: '2', label: '环节3 记录卡' },
  { stage: '4', label: '环节4 资源包' },
  { stage: '5', label: '环节5 荣誉时刻' },
];

const goToStage = (stage) => {
  if (!showStudentStageNav.value) return;
  userStore.setStage(stage);
};

const requestStudentFullscreen = async () => {
  if (!isStudentFlowActive.value) return;

  if (document.fullscreenElement !== document.documentElement) {
    try {
      await document.documentElement.requestFullscreen({ navigationUI: 'hide' });
    } catch (error) {
      console.warn('Request fullscreen failed:', error);
    }
  }
};

const onFullscreenChange = () => {
  if (isStudentFlowActive.value && !document.fullscreenElement) {
    requestStudentFullscreen();
  }
};

const onKeyDown = (event) => {
  if (!isStudentFlowActive.value) return;

  if (event.key === 'Escape' || event.key === 'F11') {
    event.preventDefault();
    requestStudentFullscreen();
  }
};

const onStudentLoginSuccess = () => {
  requestStudentFullscreen();
};

onMounted(async () => {
  const params = new URLSearchParams(window.location.search);
  isTeacherMode.value = params.get('role') === 'teacher';

  if (!isTeacherMode.value && userStore.studentId) {
    try {
      await userStore.restorePlantPhotos();
    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 404) {
        userStore.reset();
      }
    }
  }

  document.addEventListener('fullscreenchange', onFullscreenChange);
  window.addEventListener('keydown', onKeyDown, true);
  window.addEventListener('student-login-success', onStudentLoginSuccess);

  requestStudentFullscreen();
});

onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', onFullscreenChange);
  window.removeEventListener('keydown', onKeyDown, true);
  window.removeEventListener('student-login-success', onStudentLoginSuccess);
});

watch(
  () => userStore.currentStage,
  () => {
    requestStudentFullscreen();
  }
);
</script>

<style>
html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #f7f8fa;
  font-size: 16px;
}

#app {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.app-main {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: 100vh;
}

.student-stage-nav {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 10px 12px;
  background: #ffffff;
  border-bottom: 1px solid #e7ecf3;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow-x: auto;
  flex-shrink: 0;
}

.stage-nav-btn {
  border: 1px solid #cfd8e8;
  background: #f8faff;
  color: #2f3d52;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}

.stage-nav-btn.active {
  border-color: #377dff;
  background: #377dff;
  color: #ffffff;
}

.placeholder {
  padding: 60px;
  text-align: center;
  font-size: 18px;
}

@media (max-width: 1024px) and (min-height: 600px) {
  html,
  body {
    font-size: 17px;
  }
}

@media (max-width: 1366px) and (min-height: 1024px) and (orientation: portrait) {
  html,
  body {
    font-size: 18px;
  }
}
</style>
