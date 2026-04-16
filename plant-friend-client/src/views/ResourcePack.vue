<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">写写我的植物朋友</div>
      <van-button
        type="primary"
        round
        size="small"
        @click="submitStage4"
        :loading="loading"
        :disabled="!canGoNext"
        class="top-nav-action"
      >
        下一步
      </van-button>
    </div>

    <div class="resource-layout">
      <div class="resource-stack">
        <div class="pack-card plant-card">
          <div class="pack-card-title">回看照片</div>
          <div class="plant-photo-strip">
            <button
              v-for="(photo, index) in displayedPlantPhotos"
              :key="index"
              type="button"
              class="plant-photo-btn"
              @click="onPhotoPreview(index)"
            >
              <van-image :src="photo" fit="cover" radius="4" class="plant-photo-image" />
            </button>
          </div>
        </div>

        <div class="help-section">
          <div class="help-title">我还需要一点帮助：</div>
          <div class="help-grid">
            <button
              v-for="pack in resourcePacks"
              :key="pack.id"
              type="button"
              class="help-item"
              @click="onPreview(pack)"
            >
              <div class="help-item-content">
                <div class="help-item-inner">
                  <div class="help-item-text">{{ formatPrompt(pack.prompt) }}</div>
                  <div class="help-item-tip">点击查看</div>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import axios from 'axios';
import { useUserStore } from '../store/user';
import { showConfirmDialog, showImagePreview, showToast } from 'vant';
import { NEXT_BUTTON_KEYS } from '../constants/nextButtonControls';

const userStore = useUserStore();
const loading = ref(false);
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.resourcePack));

const displayedPlantPhotos = computed(() => (userStore.prePlantPhotos || []).slice(0, 3));

const onPhotoPreview = (startIndex) => {
  if (displayedPlantPhotos.value.length === 0) return;
  showImagePreview({
    images: displayedPlantPhotos.value,
    startPosition: startIndex,
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body',
  });

  axios.post(`/api/student/track-resource-click/${userStore.studentId}/我的植物朋友照片`).catch((error) => {
    console.warn('上报植物照片点击失败:', error);
  });
};

const formatPrompt = (text) => {
  const raw = String(text || '').trim();
  if (!raw) return '';
  return raw.replace('，', '，\n');
};

const resourcePacks = ref([
  {
    id: 'orderly',
    title: '顺序百宝箱',
    prompt: '我已经想好了“先写什么再写什么”，该怎么连起来呢？',
    imageName: '有序描写步骤',
    imageUrl: '/resources/orderly.jpg',
  },
  {
    id: 'feeling',
    title: '感受小锦囊',
    prompt: '我记录了很多的发现，该怎么合起来写呢？',
    imageName: '情感表达方法',
    imageUrl: '/resources/feeling.jpg',
  },
  {
    id: 'vocabulary',
    title: '词语百花园',
    prompt: '我想把植物朋友写清楚，可以用上哪些优美生动的词句呢？',
    imageName: '词句积累',
    imageUrl: '/resources/vocabulary.jpg',
  },
]);

const onPreview = async (pack) => {
  showImagePreview({
    images: [pack.imageUrl],
    startPosition: 0,
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body',
  });

  try {
    const resourceName = `${pack.title}-${pack.imageName}`;
    await axios.post(`/api/student/track-resource-click/${userStore.studentId}/${resourceName}`);
  } catch (error) {
    console.warn('上报资源点击失败:', error);
  }
};

const submitStage4 = async () => {
  if (!canGoNext.value) return;
  try {
    await showConfirmDialog({
      title: '确认进入下一步',
      message: '确认已完成资源包学习并进入下一环节吗？',
      confirmButtonText: '确认进入',
      cancelButtonText: '返回查看',
    });
  } catch (_) {
    return;
  }

  loading.value = true;
  try {
    await axios.post('/api/student/stage4/complete-resources', { student_id: userStore.studentId });
    userStore.setStage('5');
    showToast({ message: '资源包学习完成', type: 'success' });
  } catch (error) {
    console.error(error);
    showToast('提交失败，请重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* =========== 全局背景手账化 =========== */
.stage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #F4F1E1; /* 复古牛皮纸色底，去除了渐变蓝 */
  overflow: hidden;
}

/* =========== 顶部导航栏（与所有页面保持绝对统一） =========== */
.top-nav {
  min-height: 56px !important;
  padding: max(0px, env(safe-area-inset-top)) 16px 0 16px;
  display: grid;
  grid-template-columns: 132px 1fr 132px;
  align-items: center;
  gap: 8px;
  background: #FDFBF2; 
  border-bottom: 2px dashed #D4CBB3; 
  box-shadow: 0 4px 10px rgba(90, 76, 67, 0.05); 
  flex-shrink: 0;
  z-index: 10;
}

.top-nav-title {
  font-size: 21px;
  font-weight: 800;
  color: #5A4C43; 
  letter-spacing: 1px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-nav-spacer {
  width: 100%;
}

.top-nav-action {
  width: 100%;
  justify-self: end;
}

/* 覆盖 Vant 按钮样式 - 3D手账风 */
:deep(.top-nav-action.van-button) {
  height: 40px;
  padding-inline: 16px;
  font-size: 15px;
  font-weight: 800;
  border: none !important;
  background-color: #5C8D6D !important;
  background: #5C8D6D !important; /* 覆盖原来的蓝色渐变 */
  box-shadow: 0 4px 0 #3A664A !important;
  color: #FDFBF2 !important;
  transition: all 0.1s;
}
:deep(.top-nav-action.van-button:active) {
  transform: translateY(4px) !important;
  box-shadow: 0 0 0 #3A664A !important;
}
:deep(.top-nav-action.van-button:disabled) {
  background: #E3DBC7 !important;
  color: #A3968C !important;
  box-shadow: none !important;
  opacity: 1 !important;
  transform: none !important;
}

/* =========== 内容布局 =========== */
.resource-layout {
  flex: 1;
  padding: 24px 16px;
  box-sizing: border-box;
  display: flex;
  align-items: stretch;
  justify-content: center;
  overflow-y: auto; /* 允许滚动 */
}

.resource-stack {
  flex: 1;
  min-height: 0;
  width: min(100%, 1200px);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* =========== 顶部照片大卡片 =========== */
.pack-card {
  background: #FDFBF2;
  border-radius: 16px;
  border: 2px dashed #D4CBB3;
  box-shadow: 4px 12px 30px rgba(90, 76, 67, 0.12);
  position: relative;
}

.pack-card::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%) rotate(-1deg);
  width: 120px;
  height: 24px;
  background-color: rgba(220, 203, 163, 0.7); /* 胶带装饰 */
  box-shadow: 1px 2px 4px rgba(0,0,0,0.05);
  border-radius: 2px;
  z-index: 10;
}

.plant-card {
  flex: 0 0 auto;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pack-card-title {
  font-size: 22px;
  font-weight: 900;
  color: #5A4C43;
  text-align: center;
  position: relative;
  display: inline-block;
  align-self: center;
}
.pack-card-title::after {
  content: '';
  position: absolute;
  bottom: 0px;
  left: -5%;
  width: 110%;
  height: 8px;
  background: rgba(135, 179, 146, 0.4); /* 绿色荧光笔高亮 */
  z-index: -1;
  border-radius: 4px;
}

/* --- 拍立得照片条 --- */
.plant-photo-strip {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
  gap: 20px;
  padding-top: 10px; /* 给旋转留出空间 */
}

/* 照片底纸 */
.plant-photo-btn {
  border: 0;
  padding: 10px 10px 24px 10px; /* 底部大留白 */
  background: #FFFFFF;
  border: 1px solid #E3DBC7;
  cursor: pointer;
  width: min(31%, 280px);
  flex: 0 1 min(31%, 280px);
  border-radius: 4px; /* 拍立得方角 */
  box-shadow: 2px 6px 14px rgba(90, 76, 67, 0.1);
  transition: all 0.2s ease;
}

/* 错落有致的摆放感 */
.plant-photo-btn:nth-child(1) { transform: rotate(-2deg); }
.plant-photo-btn:nth-child(2) { transform: rotate(1deg); }
.plant-photo-btn:nth-child(3) { transform: rotate(-1.5deg); }

.plant-photo-btn:hover {
  transform: translateY(-6px) rotate(0deg);
  box-shadow: 4px 12px 24px rgba(90, 76, 67, 0.18);
  z-index: 2;
}

.plant-photo-image {
  width: 100%;
  height: clamp(180px, 24vh, 290px);
  background: #F6F4E8;
  border-radius: 2px !important;
}


/* =========== 下方资源锦囊区 =========== */
.help-section {
  flex: 0 0 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 20px;
}

.help-title {
  font-size: 22px;
  font-weight: 900;
  color: #5C8D6D; /* 森系绿 */
  text-align: center;
}

.help-grid {
  flex: 0 0 auto;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

/* 锦囊卡片：厚纸板按钮样式 */
.help-item {
  border: 2px solid #E3DBC7;
  border-radius: 14px;
  text-align: left;
  padding: 12px;
  cursor: pointer;
  box-shadow: 0 8px 0 #E3DBC7; /* 极具物理感的按压阴影 */
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 178px;
  transition: all 0.15s ease;
  background: #FAF7EA;
}

/* 为三个锦囊分配不同的手账纸张色彩 */
.help-item:nth-child(1) {
  background-color: #EAF2E6; /* 浅草绿 */
  border-color: #C0D6BA;
  box-shadow: 0 8px 0 #C0D6BA;
}
.help-item:nth-child(2) {
  background-color: #FFF4E5; /* 暖鹅黄 */
  border-color: #E6CDA8;
  box-shadow: 0 8px 0 #E6CDA8;
}
.help-item:nth-child(3) {
  background-color: #FDFBF2; /* 原木纸白 */
  border-color: #D4CBB3;
  box-shadow: 0 8px 0 #D4CBB3;
}

/* 按压反馈 */
.help-item:active {
  transform: translateY(8px);
  box-shadow: 0 0 0 transparent;
}

.help-item-content {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

/* 去除原来的内部渐变色，变为纯粹的布局容器 */
.help-item-inner {
  width: 100%;
  height: 100%;
  background: transparent;
  border: none;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  justify-content: center;
  box-shadow: none;
}

.help-item-text {
  font-size: 17px;
  line-height: 1.5;
  font-weight: 800;
  color: #5A4C43;
  text-align: center;
  white-space: pre-line;
  min-height: calc(1.5em * 2);
}

.help-item-tip {
  font-size: 14px;
  font-weight: 800;
  color: #8A7C73;
  background: rgba(90, 76, 67, 0.08); /* 淡淡的底色 */
  padding: 6px 16px;
  border-radius: 12px;
  letter-spacing: 0.5px;
}


/* =========== 响应式适配 =========== */
@media (max-width: 900px) {
  .top-nav {
    grid-template-columns: 112px 1fr 112px;
    padding-inline: 10px;
  }

  :deep(.top-nav-action.van-button) {
    font-size: 14px;
    padding-inline: 14px;
  }

  .pack-card {
    padding: 14px;
  }
  
  .plant-card {
    padding: 20px 14px;
  }

  .help-title {
    font-size: 20px;
  }

  .help-item-text {
    font-size: 16px;
  }

  .plant-photo-image {
    height: clamp(150px, 20vh, 230px);
  }
}

@media (max-width: 600px) {
  .help-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .plant-photo-strip {
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
  }

  .plant-photo-btn {
    width: min(45%, 180px); /* 手机端一行排不下3个，改为一行2个或自动 */
    flex-basis: min(45%, 180px);
    transform: rotate(0) !important; /* 手机端去掉旋转，省空间 */
  }
  
  .help-item {
    min-height: 140px;
  }
}
</style>