<template>
  <div class="stage-container">
    <div class="top-nav">了解我的植物朋友</div>

    <div class="stage-body">
      <section class="observe-panel">
        <header class="panel-header">观察画面</header>

        <div class="photo-main-box">
          <van-image
            v-if="currentPhoto"
            :src="currentPhoto"
            fit="contain"
            radius="12"
            class="photo-main"
            @click="openImagePreview(selectedPhotoIndex)"
          />
          <div v-else class="empty-tip">暂无可观察照片</div>
        </div>

        <div class="photo-select-box">
          <div class="select-title">植物朋友照片</div>
          <div
            v-if="photos.length > 0"
            class="thumb-list"
            :style="{ '--thumb-cols': Math.min(Math.max(photos.length, 1), 3) }"
          >
            <button
              v-for="(img, idx) in photos"
              :key="idx"
              type="button"
              class="thumb-item"
              :class="{ active: selectedPhotoIndex === idx }"
              @click="selectedPhotoIndex = idx"
            >
              <van-image :src="img" fit="cover" radius="8" class="thumb-img" />
            </button>
          </div>
          <div v-else class="empty-tip small">暂无照片可选择</div>
        </div>
      </section>

      <section class="evaluate-panel">
        <header class="panel-header">我用了哪些观察方法了解植物朋友？</header>

        <div class="option-list" :style="{ '--option-rows': options.length }">
          <button
            v-for="item in options"
            :key="item.name"
            type="button"
            class="option-card"
            :class="{ active: checkedItems.includes(item.name) }"
            @click="toggleItem(item.name)"
          >
            <span class="option-text">{{ item.icon }} {{ item.name }}</span>
            <span class="option-check" :class="{ checked: checkedItems.includes(item.name) }">
              <span v-if="checkedItems.includes(item.name)">✓</span>
            </span>
          </button>
        </div>

        <van-button
          type="primary"
          block
          round
          size="large"
          :disabled="checkedItems.length === 0"
          :loading="loading"
          @click="onNextStep"
          class="submit-btn"
        >
          提交我使用的观察方法
        </van-button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useUserStore } from '../store/user';
import { submitSensoryApi } from '../api/student';
import { showDialog, showImagePreview, showToast } from 'vant';

const userStore = useUserStore();
const loading = ref(false);
const checkedItems = ref([]);
const selectedPhotoIndex = ref(0);

const options = [
  { name: '看一看', icon: '👀' },
  { name: '闻一闻', icon: '👃' },
  { name: '摸一摸', icon: '✋' },
  { name: '听一听', icon: '👂' },
  { name: '尝一尝', icon: '👅' },
  { name: '其他', icon: '✨' },
];

const photos = computed(() => userStore.prePlantPhotos || []);

const currentPhoto = computed(() => {
  if (photos.value.length === 0) return '';
  return photos.value[selectedPhotoIndex.value] || photos.value[0];
});

watch(
  () => photos.value.length,
  (len) => {
    if (len === 0) {
      selectedPhotoIndex.value = 0;
    } else if (selectedPhotoIndex.value >= len) {
      selectedPhotoIndex.value = 0;
    }
  }
);

const openImagePreview = (startIndex) => {
  if (photos.value.length === 0) return;
  showImagePreview({
    images: photos.value,
    startPosition: startIndex,
    closeable: true,
    closeOnClickImage: true,
    closeOnClickOverlay: true,
    teleport: 'body',
  });
};

const toggleItem = (name) => {
  if (checkedItems.value.includes(name)) {
    checkedItems.value = checkedItems.value.filter((v) => v !== name);
  } else {
    checkedItems.value.push(name);
  }
};

const onNextStep = async () => {
  if (checkedItems.value.length === 0) return;

  loading.value = true;
  try {
    await submitSensoryApi(userStore.studentId, checkedItems.value);
    userStore.setSensorySelections(checkedItems.value);
    userStore.setStage('sensory-transition');
    showToast({ message: '观察记录成功', type: 'success' });
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
  overflow: hidden;
  background: #f5f7fb;
}

.top-nav {
  min-height: 48px;
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
  flex-shrink: 0;
}

.stage-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 12px;
  padding: 12px;
  box-sizing: border-box;
  overflow: hidden;
}

.observe-panel,
.evaluate-panel {
  background: #fff;
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid #e8edf6;
  overflow: hidden;
}

.panel-header {
  font-size: 16px;
  font-weight: 700;
  color: #243447;
}

.photo-main-box {
  flex: 0 0 auto;
  height: min(40vh, 300px);
  border-radius: 12px;
  border: 1px dashed #cfd8e8;
  background: #fafcff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.photo-main {
  width: 100%;
  height: 100%;
}

.photo-select-box {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  border-top: 1px solid #edf1f7;
  padding-top: 8px;
}

.select-title {
  font-size: 13px;
  color: #4b5d75;
  margin-bottom: 6px;
  font-weight: 600;
}

.thumb-list {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(var(--thumb-cols), minmax(0, 1fr));
  grid-auto-rows: 1fr;
  gap: 6px;
}

.thumb-item {
  width: 100%;
  height: 100%;
  border: 2px solid transparent;
  border-radius: 10px;
  padding: 0;
  background: transparent;
  cursor: pointer;
  overflow: hidden;
}

.thumb-item.active {
  border-color: #377dff;
}

.thumb-img {
  width: 100%;
  height: 100%;
  display: block;
}

.submit-btn {
  margin-top: auto;
}

.option-list {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-rows: repeat(var(--option-rows), minmax(0, 1fr));
  gap: 8px;
}

.option-card {
  width: 100%;
  height: 100%;
  border: 1.5px solid #d9e2ef;
  border-radius: 10px;
  background: #ffffff;
  padding: 0 12px 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  text-align: left;
}

.option-card.active {
  border-color: #377dff;
  background: #f2f7ff;
}

.option-text {
  font-size: 18px;
  color: #1f2d3d;
  font-weight: 600;
}

.option-check {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: 2px solid #c2cede;
  background: #f8fbff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #377dff;
  font-size: 22px;
  font-weight: 700;
  flex-shrink: 0;
}

.option-check.checked {
  border-color: #377dff;
  background: #eaf2ff;
}

:deep(.van-button--large) {
  height: 44px;
}

.empty-tip {
  color: #8a97ab;
  font-size: 14px;
}

.empty-tip.small {
  font-size: 12px;
}

@media (max-width: 900px) {
  .stage-body {
    grid-template-columns: 1fr;
    gap: 10px;
    padding: 10px;
  }

  .photo-main-box {
    height: min(30vh, 220px);
  }
}
</style>
