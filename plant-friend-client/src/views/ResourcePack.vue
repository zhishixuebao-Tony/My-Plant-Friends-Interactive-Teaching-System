<template>
  <div class="stage-container">
    <div class="top-nav">试着写清楚</div>

    <div class="resource-layout">

      <div class="pack-list-view">
        <div class="pack-grid">
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

      <div class="action-footer">
        <van-button type="primary" block round size="large" @click="submitStage4" :loading="loading">查看完资源包，下一步</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useUserStore } from '../store/user';
import { showConfirmDialog, showImagePreview, showToast } from 'vant';

const userStore = useUserStore();
const loading = ref(false);

const resourcePacks = ref([
  {
    id: 'multi-aspect',
    title: '多方面介绍',
    images: [{ name: '多方面观察技巧', url: '/resources/multi-aspect.jpg' }],
  },
  {
    id: 'feeling',
    title: '融入感受',
    images: [{ name: '情感表达方法', url: '/resources/feeling.jpg' }],
  },
  {
    id: 'orderly',
    title: '有序介绍',
    images: [{ name: '有序描写步骤', url: '/resources/orderly.jpg' }],
  },
  {
    id: 'vocabulary',
    title: '优美词句',
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

.resource-header {
  font-size: 20px;
  font-weight: bold;
}

.pack-list-view {
  flex: 1;
  min-height: 0;
}

.pack-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr));
  gap: 12px;
  height: 100%;
  min-height: 0;
}

.pack-card {
  background: #fff;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 12px;
  min-height: 0;
  border: 1px solid #e8edf6;
}

.pack-card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 4px;
}

.pack-card-image {
  width: 100%;
  height: clamp(150px, 22vh, 220px);
  border: 1px solid #dbe4f3;
  border-radius: 10px;
  background: #f8fbff;
  padding: 6px;
  box-sizing: border-box;
  overflow: hidden;
  cursor: pointer;
}

.action-footer {
  margin-top: auto;
  flex-shrink: 0;
}

@media (max-width: 900px) {
  .pack-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: repeat(2, minmax(0, 1fr));
    height: 100%;
  }

  .pack-card {
    padding: 12px;
  }

  .pack-card-title {
    font-size: 15px;
  }
  
  .pack-card-image {
    height: clamp(120px, 18vh, 170px);
  }

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
