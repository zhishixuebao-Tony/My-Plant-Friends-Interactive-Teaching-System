<template>
  <div class="stage-container">
    <div class="top-nav">试着写清楚</div>

    <div class="resource-layout">
      <div class="tab-nav">
        <button 
          class="tab-button" 
          :class="{ active: activeTab === 'resources' }"
          @click="activeTab = 'resources'"
        >
          写作资源包
        </button>
        <button 
          class="tab-button" 
          :class="{ active: activeTab === 'photos' }"
          @click="activeTab = 'photos'"
        >
          我的植物朋友照片
        </button>
      </div>

      <div class="content-area">
        <div v-show="activeTab === 'resources'" class="tab-content resource-tab">
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
        </div>

        <div v-show="activeTab === 'photos'" class="tab-content photo-tab">
          <div v-if="plantPhotos.length > 0" class="photo-list-view">
            <div class="photo-grid">
              <div 
                v-for="(photo, index) in plantPhotos" 
                :key="index" 
                class="photo-card"
              >
                <van-image
                  :src="photo"
                  fit="cover"
                  radius="10"
                  class="photo-image"
                  @click="onPhotoPreview(index)"
                />
              </div>
            </div>
            <div class="photo-tip">点击照片可放大查看植物朋友</div>
          </div>
          <div v-else class="empty-photos">
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
import { ref, computed } from 'vue';
import axios from 'axios';
import { useUserStore } from '../store/user';
import { showConfirmDialog, showImagePreview, showToast } from 'vant';

const userStore = useUserStore();
const loading = ref(false);
const activeTab = ref('resources');

const plantPhotos = computed(() => {
  return userStore.prePlantPhotos || [];
});

const onPhotoPreview = (startIndex) => {
  if (plantPhotos.value.length === 0) return;
  showImagePreview({
    images: plantPhotos.value,
    startPosition: startIndex,
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body',
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.pack-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(280px, 1fr));
  gap: 20px;
  align-items: start;
  justify-content: center;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.pack-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  border: 1px solid #e8edf6;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  height: auto;
  min-height: 0;
}

@media (min-width: 900px) {
  .pack-grid {
    grid-template-columns: repeat(3, minmax(280px, 1fr));
    gap: 24px;
    max-width: 1400px;
  }
  
  .pack-card {
    padding: 28px;
    gap: 20px;
  }
  
  .pack-card-title {
    font-size: 18px;
  }
  
  .pack-card-image {
    max-height: 350px;
    min-height: 200px;
  }
}

.pack-card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 4px;
}

.pack-card-image {
  width: 100%;
  height: auto;
  max-height: 300px;
  min-height: 150px;
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

.action-footer {
  margin-top: auto;
  flex-shrink: 0;
}

@media (max-width: 900px) {
  .pack-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(3, auto);
    height: auto;
  }

  .pack-card:first-child,
  .pack-card:nth-child(2),
  .pack-card:nth-child(3) {
    grid-column: 1;
    grid-row: auto;
  }
  
  .pack-card:first-child {
    grid-row: 1;
  }
  
  .pack-card:nth-child(2) {
    grid-row: 2;
  }
  
  .pack-card:nth-child(3) {
    grid-row: 3;
  }

  .pack-card {
    padding: 12px;
  }

  .pack-card-title {
    font-size: 15px;
  }
  
  .pack-card-image {
    height: clamp(140px, 22vh, 200px);
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

.tab-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  border-bottom: 1px solid #e8edf6;
  padding-bottom: 8px;
}

.tab-button {
  flex: 1;
  padding: 12px 16px;
  background: #f5f7fb;
  border: 1px solid #e8edf6;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #4b5d75;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-button:hover {
  background: #edf1f7;
}

.tab-button.active {
  background: #377dff;
  border-color: #377dff;
  color: white;
  box-shadow: 0 2px 6px rgba(55, 125, 255, 0.25);
}

.content-area {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.tab-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.photo-list-view {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.photo-card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e8edf6;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.photo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.photo-image {
  width: 100%;
  height: 220px;
  display: block;
}

.photo-tip {
  font-size: 14px;
  color: #8a97ab;
  text-align: center;
  margin-top: 8px;
}

.empty-photos {
  flex: 1;
  min-height: 0;
}

/* 响应式适配 */
@media (max-width: 900px) {
  .photo-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    max-width: 100%;
  }
  
  .photo-image {
    height: 180px;
  }
  
  .tab-button {
    padding: 10px 12px;
    font-size: 14px;
  }
}

@media (max-width: 600px) {
  .photo-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }
  
  .photo-image {
    height: 150px;
  }
}

</style>