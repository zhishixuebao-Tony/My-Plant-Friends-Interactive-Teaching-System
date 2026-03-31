<template>
  <div class="stage-container">
    <!-- 顶部导航 -->
    <van-nav-bar title="环节 1：我的感官观察站" fixed placeholder border />

    <div class="split-layout">
      <!-- ================= 左侧：多媒体展示区 ================= -->
      <div class="left-panel">
        <div class="media-container">
    
          <!-- 上方：植物照片轮播卡片 -->
          <div class="media-card" v-if="userStore.prePlantPhotos && userStore.prePlantPhotos.length > 0">
            <div class="card-title">
              <van-icon name="photo-o" color="#07c160" /> 我的植物档案
            </div>
            
            <van-swipe class="photo-swipe" :autoplay="3500" indicator-color="white">
              <van-swipe-item v-for="(img, index) in userStore.prePlantPhotos" :key="index">
                <!-- 照片 -->
                <van-image 
                  :src="img" 
                  fit="cover" 
                  class="swipe-img" 
                  @click="openImagePreview(index)" 
                />
                <!-- 悬浮提示条 -->
                <div class="swipe-hint">🔍 点击放大观察细节 ({{ index + 1 }}/{{ userStore.prePlantPhotos.length }})</div>
              </van-swipe-item>
            </van-swipe>
          </div>
          
          <!-- 无数据时的缺省提示 -->
          <div v-if="(!userStore.prePlantPhotos || userStore.prePlantPhotos.length === 0) && !userStore.preVideoUrl" class="empty-hint">
            <van-icon name="flower-o" size="50" color="#ebedf0" />
            <p>老师还在准备你的植物资源哦~</p>
          </div>

        </div>
      </div>

      <!-- ================= 右侧：感官选择区 ================= -->
      <div class="right-panel">
        <div class="panel-header">我观察到了... (可多选)</div>
        
        <div class="scroll-content">
          <van-checkbox-group v-model="checkedItems" shape="square">
            <div 
              class="custom-check-card" 
              v-for="item in options" 
              :key="item.name"
              @click="toggleItem(item.name)"
              :class="{ 'is-active': checkedItems.includes(item.name) }"
            >
              <van-checkbox :name="item.name" @click.stop>
                <div class="check-label">
                  <span class="emoji">{{ item.icon }}</span>
                  <span class="text">{{ item.name }}</span>
                </div>
              </van-checkbox>
            </div>
          </van-checkbox-group>
        </div>

        <!-- 底部固定提交按钮 -->
        <div class="action-footer">
          <van-button 
            type="primary" 
            block 
            round 
            size="large"
            :disabled="checkedItems.length === 0"
            @click="onNextStep"
            :loading="loading"
            loading-text="正在保存记录..."
          >
            确认提交，进入下一步
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { submitSensoryApi } from '../api/student';
import { showToast, showImagePreview } from 'vant';

const userStore = useUserStore();
const loading = ref(false);
const checkedItems = ref([]);

const openImagePreview = (startIndex) => {
  if (!userStore.prePlantPhotos || userStore.prePlantPhotos.length === 0) return;
  showImagePreview({
    images: userStore.prePlantPhotos,
    startPosition: startIndex,
    closeable: true,
  });
};

// --- 右侧答题区逻辑 ---
const options = [
  { name: '看了看', icon: '👀' },
  { name: '闻了闻', icon: '👃' },
  { name: '摸了摸', icon: '🤚' },
  { name: '听一听', icon: '👂' },
  { name: '尝了尝', icon: '👅' }
];

const toggleItem = (name) => {
  if (checkedItems.value.includes(name)) {
    checkedItems.value = checkedItems.value.filter(i => i !== name);
  } else {
    checkedItems.value.push(name);
  }
};

const onNextStep = async () => {
  if (checkedItems.value.length === 0) return;
  
  loading.value = true;
  try {
    // 调用后端接口保存环节 1 的选项
    await submitSensoryApi(userStore.studentId, checkedItems.value);
    
    showToast({ message: '记录成功！', type: 'success' });
    
    // 平滑过渡到环节 2
    userStore.setStage('2');
  } catch (err) {
    console.error("提交失败:", err);
    showToast('网络有点慢，请重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* ================= 整体布局 ================= */
.stage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
}

.split-layout {
  flex: 1;
  display: flex;
  overflow: hidden; 
}

/* ================= 左侧：多媒体面板 ================= */
.left-panel {
  flex: 1.1;
  background-color: #f2f3f5; /* 浅灰色背景，衬托白色卡片 */
  padding: 20px;
  overflow-y: auto;
}

.media-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.media-card {
  background: #fff;
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.card-title {
  font-size: 17px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-hint {
  text-align: center;
  color: #999;
  padding: 50px 0;
  font-size: 14px;
}

/* 轮播图样式 */
.photo-swipe {
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  height: 240px; 
}

.swipe-img {
  width: 100%;
  height: 100%;
  display: block;
  cursor: pointer;
}

.swipe-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  color: white;
  font-size: 13px;
  padding: 20px 10px 10px;
  text-align: center;
  pointer-events: none; 
}

.play-button {
  width: 64px;
  height: 64px;
  border: 2px solid rgba(255,255,255,0.9);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 12px;
  background: rgba(0,0,0,0.4);
}

.cover-text {
  color: #fff;
  font-size: 14px;
  letter-spacing: 1px;
}

/* ================= 右侧：交互面板 ================= */
.right-panel {
  flex: 1;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #ebedf0;
  box-shadow: -4px 0 15px rgba(0,0,0,0.02);
}

.panel-header {
  font-size: 18px;
  font-weight: bold;
  padding: 20px;
  color: #323233;
  border-bottom: 1px solid #f2f3f5;
}

.scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 隐藏滚动条但保留滚动 */
.scroll-content::-webkit-scrollbar, .left-panel::-webkit-scrollbar {
  display: none;
}

.custom-check-card {
  margin-bottom: 16px;
  padding: 20px;
  background-color: #f7f8fa;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.2s;
  cursor: pointer;
}

.custom-check-card:active {
  transform: scale(0.98);
}

.custom-check-card.is-active {
  background-color: #f0f9eb;
  border-color: #07c160;
}

.check-label {
  display: flex;
  align-items: center;
  margin-left: 12px;
}

.emoji { font-size: 32px; margin-right: 15px; }
.text { font-size: 20px; color: #323233; font-weight: 500; }

:deep(.van-checkbox__icon) { font-size: 26px; }

.action-footer {
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 -4px 15px rgba(0,0,0,0.03);
}
</style>