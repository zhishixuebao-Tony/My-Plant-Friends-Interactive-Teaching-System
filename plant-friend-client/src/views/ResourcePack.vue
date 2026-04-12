<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">试着写清楚</div>
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
          <div class="pack-card-title">我的植物朋友</div>
          <div class="plant-photo-strip">
            <button
              v-for="(photo, index) in displayedPlantPhotos"
              :key="index"
              type="button"
              class="plant-photo-btn"
              @click="onPhotoPreview(index)"
            >
              <van-image :src="photo" fit="cover" radius="10" class="plant-photo-image" />
            </button>
          </div>
        </div>

        <div class="help-section">
          <div class="help-title">我需要一点帮助：</div>
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
                  <div class="help-item-text">{{ pack.prompt }}</div>
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
.stage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
  overflow: hidden;
}

.resource-layout {
  flex: 1;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  align-items: stretch;
  justify-content: center;
  overflow: hidden;
}

.resource-stack {
  flex: 1;
  min-height: 0;
  width: min(100%, 1200px);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pack-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  border: 1px solid #e8edf6;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.plant-card {
  flex: 0 0 auto;
  padding: 18px 18px 20px;
}

.pack-card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2d3d;
}

.plant-photo-strip {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
  gap: 10px;
}

.plant-photo-btn {
  border: 0;
  padding: 0;
  background: transparent;
  cursor: pointer;
  width: min(31%, 280px);
  flex: 0 1 min(31%, 280px);
}

.plant-photo-image {
  width: 100%;
  height: clamp(180px, 24vh, 290px);
  border: 1px solid #dbe4f3;
  background: #f8fbff;
}

.help-section {
  flex: 0 0 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.help-title {
  font-size: 20px;
  font-weight: 800;
  color: #1f2d3d;
  text-align: center;
}

.help-grid {
  flex: 0 0 auto;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.help-item {
  border: 0;
  border-radius: 14px;
  background: linear-gradient(180deg, #e9f5ff 0%, #dcecff 100%);
  text-align: left;
  padding: 8px;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(37, 86, 143, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
}

.help-item:hover {
  box-shadow: 0 12px 22px rgba(37, 86, 143, 0.24);
}

.help-item:active {
  transform: scale(0.98);
}

.help-item-text {
  font-size: 17px;
  line-height: 1.45;
  font-weight: 700;
  color: #23453a;
  text-align: center;
  font-family: "STXingkai", "KaiTi", "STKaiti", "Microsoft YaHei", sans-serif;
}

.help-item-content {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.help-item-inner {
  width: calc(100% - 14px);
  margin: 0 auto;
  border: 0;
  border-radius: 11px;
  background: linear-gradient(180deg, #ffffff 0%, #f4fbec 100%);
  padding: 10px 10px 9px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  box-shadow: 0 6px 12px rgba(76, 135, 96, 0.2);
}

.help-item-tip {
  font-size: 15px;
  font-weight: 800;
  line-height: 1.2;
  color: #2d8a4e;
  letter-spacing: 0.5px;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
}

.top-nav {
  min-height: 56px !important;
  padding: max(0px, env(safe-area-inset-top)) 16px 0 16px;
  display: grid;
  grid-template-columns: 132px 1fr 132px;
  align-items: center;
  gap: 8px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
  border-bottom: 1px solid #dfe6f3;
  box-shadow: 0 3px 10px rgba(30, 60, 120, 0.08);
  flex-shrink: 0;
}

.top-nav-title {
  font-size: 17px;
  font-weight: 700;
  color: #1f2d3d;
  letter-spacing: 0.2px;
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

:deep(.top-nav-action.van-button) {
  height: 34px;
  padding-inline: 10px;
  font-size: 13px;
  font-weight: 700;
}

@media (max-width: 900px) {
  .top-nav {
    grid-template-columns: 112px 1fr 112px;
    padding-inline: 10px;
  }

  :deep(.top-nav-action.van-button) {
    font-size: 12px;
    padding-inline: 8px;
  }

  .pack-card {
    padding: 12px;
  }

  .help-title {
    font-size: 18px;
  }

  .help-item-text {
    font-size: 15px;
  }

  .help-item-tip {
    font-size: 14px;
  }

  .plant-photo-image {
    height: clamp(150px, 20vh, 230px);
  }
}

@media (max-width: 600px) {
  .help-grid {
    grid-template-columns: 1fr;
  }

  .plant-photo-strip {
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
  }

  .plant-photo-btn {
    width: min(32%, 180px);
    flex-basis: min(32%, 180px);
  }
}
</style>
