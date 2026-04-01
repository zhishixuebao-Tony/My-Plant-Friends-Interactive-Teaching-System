<template>
  <div class="stage-container">
    <!-- 顶部导航 -->
    <van-nav-bar 
      title="环节 1：我的感官观察站" 
      fixed 
      placeholder 
      border
      left-arrow
      @click-left="$router.back()"
    >
      <template #right>
        <van-icon name="question-o" size="18" @click="showHelp" />
      </template>
    </van-nav-bar>

    <div class="split-layout">
      <!-- ================= 左侧：植物观察区 ================= -->
      <div class="left-panel">
        <!-- 植物照片展示区 -->
        <div class="photo-section" v-if="userStore.prePlantPhotos && userStore.prePlantPhotos.length > 0">
          <div class="section-header">
            <van-icon name="photo-o" color="#07c160" />
            <span>我的植物照片</span>
            <span class="photo-count">{{ userStore.prePlantPhotos.length }}张</span>
          </div>
          
          <div class="photo-gallery">
            <van-swipe 
              class="photo-swipe" 
              :autoplay="isAutoPlaying ? 3500 : false" 
              indicator-color="#07c160"
              :height="photoHeight"
            >
              <van-swipe-item v-for="(img, index) in userStore.prePlantPhotos" :key="index">
                <div class="photo-item" @click="openImagePreview(index)">
                  <van-image 
                    :src="img" 
                    fit="cover" 
                    class="swipe-img"
                    :radius="12"
                  />
                  <div class="photo-overlay">
                    <div class="photo-info">
                      <div class="photo-index">
                        <van-icon name="image" size="14" />
                        <span>照片 {{ index + 1 }}/{{ userStore.prePlantPhotos.length }}</span>
                      </div>
                      <div class="photo-hint">
                        <van-icon name="search" size="14" />
                        <span>点击放大观察细节</span>
                      </div>
                    </div>
                  </div>
                </div>
              </van-swipe-item>
            </van-swipe>
            
            <!-- 轮播控制 -->
            <div class="swipe-controls">
              <van-button 
                type="default" 
                size="small" 
                icon="pause-circle-o"
                @click="pauseAutoPlay"
                v-if="isAutoPlaying"
                class="control-btn"
              >
                暂停自动播放
              </van-button>
              <van-button 
                type="default" 
                size="small" 
                icon="play-circle-o"
                @click="startAutoPlay"
                v-else
                class="control-btn"
              >
                开始自动播放
              </van-button>
            </div>
          </div>
        </div>
        
        <!-- 无照片提示 -->
        <div v-else class="empty-state">
          <div class="empty-content">
            <van-icon name="flower-o" size="60" color="#ebedf0" />
            <h3>等待植物照片</h3>
            <p>老师正在上传你的植物照片，请稍候...</p>
            <van-button 
              type="default" 
              size="small" 
              @click="refreshPhotos"
              :loading="refreshing"
            >
              <van-icon name="replay" />
              刷新查看
            </van-button>
          </div>
        </div>
      </div>

      <!-- ================= 右侧：感官选择区 ================= -->
      <div class="right-panel">
        <div class="sensory-section">
          <div class="sensory-header">
            <van-icon name="eye-o" color="#1989fa" />
            <div class="header-content">
              <h2>我做到了</h2>
              <p class="header-subtitle">(请选择你使用过的感官)</p>
            </div>
          </div>
          
          <div class="sensory-progress">
            <div class="progress-info">
              <span class="progress-text">已选择 {{ checkedItems.length }}/5 个感官</span>
              <span class="progress-percent">{{ Math.round((checkedItems.length / 5) * 100) }}%</span>
            </div>
            <van-progress 
              :percentage="(checkedItems.length / 5) * 100" 
              color="#1989fa" 
              stroke-width="6"
              :show-pivot="false"
              class="progress-bar"
            />
          </div>

          <div class="sensory-grid">
            <div 
              class="sensory-card" 
              v-for="item in options" 
              :key="item.name"
              @click="toggleItem(item.name)"
              :class="{ 'is-selected': checkedItems.includes(item.name) }"
            >
              <div class="sensory-icon">
                <div class="icon-circle" :style="{ backgroundColor: getIconBgColor(item.name) }">
                  <span class="icon-emoji">{{ item.icon }}</span>
                </div>
                <div class="check-indicator" v-if="checkedItems.includes(item.name)">
                  <van-icon name="success" color="#fff" size="16" />
                </div>
              </div>
              <div class="sensory-content">
                <h3 class="sensory-title">{{ item.name }}</h3>
                <p class="sensory-desc">{{ getSensoryDescription(item.name) }}</p>
              </div>
              <div class="sensory-action">
                <van-icon 
                  :name="checkedItems.includes(item.name) ? 'checked' : 'circle'" 
                  :color="checkedItems.includes(item.name) ? '#07c160' : '#dcdee0'" 
                  size="20"
                />
              </div>
            </div>
          </div>

          <!-- 已选感官提示 -->
          <div class="selected-hint" v-if="checkedItems.length > 0">
            <van-icon name="good-job-o" color="#07c160" />
            <span>你已经选择了 {{ checkedItems.length }} 种感官，观察得很仔细！</span>
          </div>
          <div class="empty-hint" v-else>
            <van-icon name="info-o" color="#969799" />
            <span>请选择你使用过的感官进行观察</span>
          </div>
        </div>

        <!-- 底部提交区域 -->
        <div class="submit-section">
          <div class="submit-content">
            <van-button 
              type="primary" 
              block 
              round 
              size="large"
              :disabled="checkedItems.length === 0"
              @click="onNextStep"
              :loading="loading"
              class="submit-btn"
              icon="arrow"
            >
              <template #loading>
                <van-loading type="spinner" size="20px" />
              </template>
              <span v-if="checkedItems.length > 0">
                完成观察，进入记录卡环节
              </span>
              <span v-else>
                请先选择观察的感官
              </span>
            </van-button>
            
            <div class="submit-tip" v-if="checkedItems.length > 0">
              <van-icon name="clock-o" color="#07c160" />
              <span>提交后将进入下一环节，请确认已观察完毕</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { submitSensoryApi } from '../api/student';
import { showToast, showImagePreview, showDialog } from 'vant';

const userStore = useUserStore();
const loading = ref(false);
const checkedItems = ref([]);
const isAutoPlaying = ref(true);
const photoHeight = ref(280);
const refreshing = ref(false);

// --- 左侧多媒体功能 ---
const openImagePreview = (startIndex) => {
  if (!userStore.prePlantPhotos || userStore.prePlantPhotos.length === 0) return;
  showImagePreview({
    images: userStore.prePlantPhotos,
    startPosition: startIndex,
    closeable: true,
    closeOnClickImage: true,
    closeOnClickOverlay: true,
    teleport: 'body'
  });
};

const pauseAutoPlay = () => {
  isAutoPlaying.value = false;
  showToast({
    message: '已暂停自动播放',
    type: 'success',
    duration: 1000
  });
};

const startAutoPlay = () => {
  isAutoPlaying.value = true;
  showToast({
    message: '已开始自动播放',
    type: 'success',
    duration: 1000
  });
};

const refreshPhotos = async () => {
  refreshing.value = true;
  try {
    // 模拟刷新操作，实际项目中可能需要调用API重新获取照片
    await new Promise(resolve => setTimeout(resolve, 1000));
    showToast('已刷新照片列表');
  } catch (error) {
    console.warn('刷新照片失败:', error);
  } finally {
    refreshing.value = false;
  }
};

const showHelp = () => {
  showDialog({
    title: '感官观察站使用说明',
    message: '欢迎来到感官观察站！请先观察左侧的植物照片，然后选择你使用过的感官进行记录。观察完成后，点击提交进入下一环节。',
    confirmButtonText: '知道了',
    cancelButtonText: '关闭'
  });
};

// --- 右侧感官选择功能 ---
const options = [
  { name: '看了看', icon: '👀' },
  { name: '闻了闻', icon: '👃' },
  { name: '摸了摸', icon: '🤚' },
  { name: '听一听', icon: '👂' },
  { name: '尝了尝', icon: '👅' }
];

// 获取感官描述
const getSensoryDescription = (name) => {
  const descriptions = {
    '看了看': '观察植物的颜色、形状、大小等视觉特征',
    '闻了闻': '闻一闻植物有没有特殊的气味或芳香',
    '摸了摸': '触摸植物的叶子、茎干，感受触感',
    '听一听': '倾听风吹过植物的声音或植物生长的声音',
    '尝了尝': '品尝植物的可食用部分（需在老师指导下）'
  };
  return descriptions[name] || '使用该感官进行观察';
};

// 获取图标背景色
const getIconBgColor = (name) => {
  const colors = {
    '看了看': '#4fc3f7',
    '闻了闻': '#81c784',
    '摸了摸': '#ffb74d',
    '听一听': '#ba68c8',
    '尝了尝': '#ff8a65'
  };
  return colors[name] || '#7986cb';
};

const toggleItem = (name) => {
  if (checkedItems.value.includes(name)) {
    checkedItems.value = checkedItems.value.filter(i => i !== name);
  } else {
    checkedItems.value.push(name);
  }
  
  // 提供触觉反馈
  if (checkedItems.value.length === 5) {
    showToast({
      message: '太棒了！你使用了全部五种感官！',
      type: 'success'
    });
  }
};

const onNextStep = async () => {
  if (checkedItems.value.length === 0) return;
  
  loading.value = true;
  try {
    // 调用后端接口保存环节 1 的选项
    await submitSensoryApi(userStore.studentId, checkedItems.value);
    
    showToast({ 
      message: `观察记录成功！你使用了${checkedItems.value.length}种感官`, 
      type: 'success' 
    });
    
    // 平滑过渡到环节 2
    userStore.setStage('2');
  } catch (err) {
    console.error("提交失败:", err);
    showToast('网络有点慢，请重试');
  } finally {
    loading.value = false;
  }
};

// 页面加载时的初始化
onMounted(() => {
  // 检查是否有默认选中的感官（可以从userStore中获取）
  if (userStore.sensorySelections && userStore.sensorySelections.length > 0) {
    checkedItems.value = [...userStore.sensorySelections];
  }
});
</script>

<style scoped>
/* ================= 整体布局 - 平板优化 ================= */
.stage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  overflow: hidden;
}

.split-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
  background-color: transparent;
  max-height: calc(100vh - 120px); /* 考虑导航栏和地址栏空间 */
}

/* 平板横向布局优化 */
@media (max-width: 1024px) {
  .split-layout {
    max-height: calc(100vh - 100px);
  }
}

@media (max-width: 1024px) and (orientation: portrait) {
  .split-layout {
    flex-direction: column;
  }
}

/* 横向平板优化 */
@media (max-width: 1366px) and (min-height: 1024px) and (orientation: portrait) {
  .split-layout {
    max-height: calc(100vh - 140px);
  }
}

/* ================= 左侧：植物观察区 ================= */
.left-panel {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.95);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  border-right: 1px solid rgba(235, 237, 240, 0.8);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
}

/* 观察引导卡片 */
.observation-guide {
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 6px 20px rgba(7, 193, 96, 0.15);
  animation: slideInUp 0.5s ease-out;
}

.guide-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.guide-header span {
  font-size: 18px;
  font-weight: bold;
  color: #2e7d32;
}

.guide-content p {
  font-size: 15px;
  color: #333;
  margin-bottom: 16px;
  line-height: 1.6;
}

.guide-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.guide-step {
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 13px;
  color: #2e7d32;
  border: 1px solid rgba(7, 193, 96, 0.3);
  transition: all 0.3s;
}

.guide-step:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(7, 193, 96, 0.2);
}

/* 植物照片展示区 */
.photo-section {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  animation: fadeIn 0.6s ease-out;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  background: linear-gradient(90deg, #f8f9fa 0%, #fff 100%);
  border-bottom: 1px solid #f2f3f5;
}

.section-header span {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-left: 8px;
}

.photo-count {
  background: #07c160;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.photo-gallery {
  padding: 20px;
}

.photo-swipe {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.photo-item {
  position: relative;
  height: 100%;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
}

.swipe-img {
  width: 100%;
  height: 280px;
  object-fit: cover;
  transition: transform 0.3s;
}

.photo-item:hover .swipe-img {
  transform: scale(1.03);
}

.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  padding: 20px;
  opacity: 0;
  transition: opacity 0.3s;
}

.photo-item:hover .photo-overlay {
  opacity: 1;
}

.photo-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.photo-index,
.photo-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.swipe-controls {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.control-btn {
  background: #fff;
  border: 1px solid #07c160;
  color: #07c160;
  font-weight: 500;
  border-radius: 20px;
  padding: 6px 16px;
  transition: all 0.3s;
}

.control-btn:hover {
  background: #07c160;
  color: white;
}

/* 无照片提示 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #fff;
  border-radius: 16px;
  padding: 40px 20px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  animation: fadeIn 0.6s ease-out;
}

.empty-content {
  text-align: center;
}

.empty-content h3 {
  margin: 16px 0 8px;
  color: #333;
  font-size: 18px;
}

.empty-content p {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
  line-height: 1.5;
}

/* 观察提示卡片 */
.observation-tips {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 6px 20px rgba(242, 189, 39, 0.15);
  animation: slideInUp 0.7s ease-out;
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.tips-header span {
  font-size: 16px;
  font-weight: bold;
  color: #f57c00;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  position: relative;
  padding-left: 24px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.tips-list li:before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #07c160;
  font-weight: bold;
}

/* ================= 右侧：感官选择区 ================= */
.right-panel {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sensory-section {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
}

.sensory-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f4ff;
  animation: fadeIn 0.5s ease-out;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.header-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: #666;
}

.sensory-progress {
  background: #f8f9ff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(25, 137, 250, 0.1);
  animation: slideInRight 0.6s ease-out;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-text {
  font-size: 14px;
  color: #666;
}

.progress-percent {
  font-size: 18px;
  font-weight: bold;
  color: #1989fa;
}

.progress-bar {
  border-radius: 3px;
}

.sensory-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  animation: fadeIn 0.8s ease-out;
}

.sensory-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 2px solid #f2f3f5;
  position: relative;
  overflow: hidden;
}

.sensory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border-color: #dcdee0;
}

.sensory-card.is-selected {
  background: linear-gradient(135deg, #f0f9ff 0%, #e3f2fd 100%);
  border-color: #1989fa;
  box-shadow: 0 8px 20px rgba(25, 137, 250, 0.2);
  animation: cardPulse 0.4s ease-out;
}

@keyframes cardPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

.sensory-icon {
  position: relative;
  margin-right: 16px;
  flex-shrink: 0;
}

.icon-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s;
}

.sensory-card:hover .icon-circle {
  transform: scale(1.1);
}

.icon-emoji {
  font-size: 28px;
}

.check-indicator {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #07c160;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #fff;
  box-shadow: 0 2px 6px rgba(7, 193, 96, 0.3);
  animation: popIn 0.3s ease-out;
}

@keyframes popIn {
  0% { transform: scale(0); }
  70% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.sensory-content {
  flex: 1;
}

.sensory-title {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.sensory-desc {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.sensory-action {
  opacity: 0.6;
  transition: opacity 0.3s;
}

.sensory-card:hover .sensory-action {
  opacity: 1;
}

/* 提示区域 */
.selected-hint,
.empty-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  border-radius: 12px;
  font-size: 14px;
  animation: fadeIn 0.5s ease-out;
}

.selected-hint {
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e8 100%);
  color: #07c160;
}

.empty-hint {
  background: #f8f9fa;
  color: #969799;
  border: 1px dashed #dcdee0;
}

/* 底部提交区域 */
.submit-section {
  background: #fff;
  border-top: 1px solid #ebedf0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
  padding: 20px;
  animation: slideInUp 0.5s ease-out;
}

.submit-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.submit-btn {
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 0.5px;
  box-shadow: 0 6px 15px rgba(25, 137, 250, 0.3);
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(25, 137, 250, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  color: #07c160;
}

/* 动画定义 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .split-layout {
    flex-direction: column;
  }
  
  .left-panel {
    border-right: none;
    border-bottom: 1px solid rgba(235, 237, 240, 0.8);
    max-height: 50vh;
  }
  
  .right-panel {
    max-height: 50vh;
  }
  
  .guide-steps {
    flex-direction: column;
    gap: 8px;
  }
  
  .photo-gallery {
    padding: 15px;
  }
  
  .swipe-img {
    height: 200px;
  }
  
  .sensory-card {
    padding: 16px;
  }
  
  .icon-circle {
    width: 48px;
    height: 48px;
  }
  
  .icon-emoji {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .stage-container {
    background: #f5f7fa;
  }
  
  .left-panel,
  .right-panel {
    padding: 15px;
  }
  
  .observation-guide,
  .observation-tips {
    padding: 16px;
  }
  
  .sensory-title {
    font-size: 15px;
  }
  
  .sensory-desc {
    font-size: 12px;
  }
}

/* 滚动条美化 */
.sensory-section::-webkit-scrollbar,
.left-panel::-webkit-scrollbar {
  width: 6px;
}

.sensory-section::-webkit-scrollbar-track,
.left-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.sensory-section::-webkit-scrollbar-thumb,
.left-panel::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.sensory-section::-webkit-scrollbar-thumb:hover,
.left-panel::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
