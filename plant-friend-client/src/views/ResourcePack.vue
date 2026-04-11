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
      <div class="pack-list-view">
        <div class="pack-grid">
          <div class="pack-card">
            <div class="pack-card-title">我的植物朋友</div>
            <div class="plant-photo-strip">
              <button
                v-for="(photo, index) in displayedPlantPhotos"
                :key="index"
                type="button"
                class="plant-photo-btn"
                @click="onPhotoPreview(index)"
              >
                <van-image
                  :src="photo"
                  fit="cover"
                  radius="10"
                  class="plant-photo-image"
                />
              </button>
            </div>
          </div>

          <div v-for="pack in resourcePacks" :key="pack.id" class="pack-card">
            <div class="pack-card-title">{{ pack.title }}</div>
            <van-image
              :src="pack.images[0]?.url"
              :alt="pack.images[0]?.name || pack.title"
              fit="contain"
              radius="10"
              class="pack-card-image"
              @click="onPreview(pack.id, 0)"
            />
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
    id: 'feeling',
    title: '感受小锦囊',
    images: [{ name: '情感表达方法', url: '/resources/feeling.jpg' }],
  },
  {
    id: 'orderly',
    title: '顺序百宝箱',
    images: [{ name: '有序描写步骤', url: '/resources/orderly.jpg' }],
  },
  {
    id: 'vocabulary',
    title: '词语百花园',
    images: [{ name: '词句积累', url: '/resources/vocabulary.jpg' }],
  },
]);

const onPreview = async (packId, index) => {
  const pack = resourcePacks.value.find((p) => p.id === packId);
  if (!pack) return;

  showImagePreview({
    images: pack.images.map((img) => img.url),
    startPosition: index,
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body',
  });

  try {
    const resourceName = `${pack.title}-${pack.images[index].name}`;
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
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.pack-list-view {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: stretch;
  justify-content: center;
  width: 100%;
}

.pack-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr));
  gap: 20px;
  align-items: stretch;
  justify-content: center;
  width: min(100%, 1200px);
  height: 100%;
  margin: 0 auto;
}

.pack-card {
  --media-height: clamp(160px, 24vh, 280px);
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  border: 1px solid #e8edf6;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  height: 100%;
  min-height: 0;
}

.pack-card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 4px;
}

.pack-card-image {
  width: 100%;
  height: var(--media-height);
  max-height: var(--media-height);
  min-height: var(--media-height);
  object-fit: contain;
  border: 1px solid #dbe4f3;
  border-radius: 10px;
  background: #f8fbff;
  padding: 6px;
  box-sizing: border-box;
  overflow: hidden;
  cursor: pointer;
  flex: 1;
}

.plant-photo-strip {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.plant-photo-btn {
  border: 0;
  padding: 0;
  background: transparent;
  cursor: pointer;
}

.plant-photo-image {
  width: 100%;
  height: var(--media-height);
  border: 1px solid #dbe4f3;
  background: #f8fbff;
}

.photo-tip {
  font-size: 14px;
  color: #8a97ab;
  text-align: center;
  margin-top: 8px;
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

@media (min-width: 900px) {
  .pack-grid {
    grid-template-columns: repeat(2, minmax(280px, 1fr));
    gap: 24px;
    max-width: 1200px;
  }

  .pack-card {
    --media-height: clamp(200px, 25vh, 340px);
    padding: 28px;
    gap: 20px;
  }

  .pack-card-title {
    font-size: 18px;
  }

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

  .pack-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .pack-card {
    --media-height: clamp(120px, 18vh, 200px);
    padding: 12px;
  }

  .pack-card-title {
    font-size: 15px;
  }

}

@media (max-width: 600px) {
  .pack-grid {
    grid-template-columns: 1fr;
  }

  .plant-photo-strip {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }
}
</style>
