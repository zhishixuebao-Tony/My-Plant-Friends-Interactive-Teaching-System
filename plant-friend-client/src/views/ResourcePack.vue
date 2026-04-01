<template>
  <div class="stage-container">
    <van-nav-bar title="环节 4：魔法资源包与知识闯关" fixed placeholder border />

    <div class="resource-layout">
      
      <!-- 顶部魔法资源包展示 -->
      <div class="resource-header">
        <van-icon name="photo-o" color="#07c160" /> 
        魔法资源包 - 写作小妙招
      </div>
      
      <!-- 1. 资源包列表视图 -->
      <div class="pack-list-view" v-if="!selectedPack">
        <div class="pack-list-description">
          <p>点击下方资源包，查看对应的写作小妙招图片资源</p>
        </div>
        
        <div class="pack-grid">
          <div 
            v-for="pack in resourcePacks" 
            :key="pack.id"
            class="pack-card"
            @click="selectPack(pack)"
          >
            <div class="pack-card-icon">
              <van-icon :name="pack.icon" size="32" color="#1989fa" />
            </div>
            <div class="pack-card-content">
              <h3 class="pack-card-title">{{ pack.title }}</h3>
              <p class="pack-card-desc">{{ pack.description }}</p>
              <div class="pack-card-meta">
                <span class="image-count">
                  <van-icon name="photo-o" size="14" />
                  {{ pack.images.length }} 张图片
                </span>
                <span class="view-hint">点击查看 →</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 资源包详情视图 -->
      <div class="pack-detail-view" v-else>
        <div class="detail-header">
          <van-button 
            icon="arrow-left" 
            type="primary" 
            size="small" 
            plain 
            @click="selectedPack = null"
            class="back-btn"
          >
            返回资源包列表
          </van-button>
          <div class="detail-title">
            <van-icon :name="selectedPack.icon" color="#07c160" />
            <h2>{{ selectedPack.title }}</h2>
          </div>
          <p class="detail-description">{{ selectedPack.description }}</p>
        </div>
        
        <div class="detail-content">
          <!-- 图片资源展示 -->
          <div v-if="selectedPack.images && selectedPack.images.length > 0">
            <div class="image-count-hint">
              <van-icon name="photo-o" /> 共 {{ selectedPack.images.length }} 张图片
            </div>
            <div class="image-gallery">
              <van-grid :column-num="2" gutter="10">
                <van-grid-item 
                  v-for="(img, index) in selectedPack.images" 
                  :key="index"
                  @click="onPreview(selectedPack.id, index)"
                  class="resource-grid-item"
                >
                  <van-image 
                    :src="img.url" 
                    radius="8" 
                    fit="cover" 
                    style="height: 140px;"
                    :alt="img.name"
                  />
                  <div class="img-tag">{{ img.name }}</div>
                </van-grid-item>
              </van-grid>
            </div>
          </div>
          
          <!-- 无图片提示 -->
          <div v-else class="empty-images">
            <van-icon name="photo-fail" size="50" color="#ebedf0" />
            <p>该资源包暂无图片资源</p>
          </div>
          
          <!-- 资源包提示 -->
          <div class="pack-tip" v-if="selectedPack.tip">
            💡 {{ selectedPack.tip }}
          </div>
        </div>
      </div>

      <!-- 3. 底部提交 -->
      <div class="action-footer">
        <van-button
          type="primary"
          block
          round
          size="large"
          @click="submitStage4"
          :loading="loading"
          loading-text="正在保存进度..."
        >
          查看完资源包，下一步
        </van-button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useUserStore } from '../store/user';
import { showImagePreview, showToast } from 'vant';

const userStore = useUserStore();
const loading = ref(false);

// 当前选中的资源包
const selectedPack = ref(null);

// 定义4个资源包，每个包只包含一张图片
const resourcePacks = ref([
  {
    id: 'multi-aspect',
    title: '多方面介绍',
    icon: 'eye-o',
    description: '多方面介绍植物朋友小妙招 - 从颜色、形状、大小等多角度观察植物',
    tip: '试着从不同角度观察你的植物朋友，会有新发现哦！',
    images: [
      { name: '多方面观察技巧', url: '/resources/multi-aspect.jpg' }
    ]
  },
  {
    id: 'feeling',
    title: '融入感受',
    icon: 'smile-comment-o',
    description: '融入感受小妙招 - 把对植物的情感写进作文里',
    tip: '当你触摸叶子时，有什么感觉？闻到花香时，想到了什么？',
    images: [
      { name: '情感表达方法', url: '/resources/feeling.jpg' }
    ]
  },
  {
    id: 'orderly',
    title: '有序介绍',
    icon: 'orders-o',
    description: '有序介绍植物朋友小妙招 - 从上到下、从远到近有条理地描写',
    tip: '先写整体印象，再写局部细节，顺序很重要！',
    images: [
      { name: '有序描写步骤', url: '/resources/orderly.jpg' }
    ]
  },
  {
    id: 'vocabulary',
    title: '优美词句',
    icon: 'notes-o',
    description: '优美词句积累卡 - 收集描写植物的精彩词语和句子',
    tip: '把这些好词好句记下来，让你的作文更生动！',
    images: [
      { name: '词汇句子积累', url: '/resources/vocabulary.jpg' }
    ]
  }
]);

/**
 * 选择资源包
 */
const selectPack = (pack) => {
  selectedPack.value = pack;
};

/**
 * 点击图片放大预览，并静默上报点击次数
 */
const onPreview = async (packId, index) => {
  const pack = resourcePacks.value.find(p => p.id === packId);
  if (!pack) return;
  
  // 获取当前资源包的所有图片URL
  const imageUrls = pack.images.map(img => img.url);
  
  // 1. 调用 Vant 预览大图
  showImagePreview({
    images: imageUrls,
    startPosition: index,
    closeable: true,
    closeOnClickImage: true,
    closeOnClickOverlay: true,
    teleport: 'body'
  });

  // 2. 向后端静默上报点击数据
  // 格式：资源包名称 + 图片名称，例如："多方面介绍-颜色观察法"
  const resourceName = `${pack.title}-${pack.images[index].name}`;
  
  try {
    // 调用后端留好的统计接口
    await axios.post(`/api/student/track-resource-click/${userStore.studentId}/${resourceName}`);
    console.log(`✅ 成功上报点击记录: ${resourceName}`);
  } catch (err) {
    console.warn("点击上报失败，可能是网络问题", err);
  }
};

    /**
     * 提交环节 4
     */
const submitStage4 = async () => {
  loading.value = true;
  try {
    // 告诉后端：该学生已完成环节 4
    await axios.post('/api/student/stage4/complete-resources', {
      student_id: userStore.studentId
    });
    
    showToast({
      message: '资源包学习完成！',
      type: 'success'
    });
    
    // 顺利进入环节 5（AI评语与荣誉时刻页面）
    userStore.setStage('5');
  } catch (err) {
    console.error("提交环节4失败:", err);
    showToast('网络有点小脾气，请重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.stage-container {
  height: 100%;
  background-color: #f7f8fa;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.resource-layout { 
  padding: 15px; 
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 120px); /* 考虑导航栏和地址栏空间 */
}

/* 平板适配 */
@media (max-width: 1024px) {
  .resource-layout {
    max-height: calc(100vh - 100px);
    padding: 12px;
  }
}

/* 横向平板优化 */
@media (max-width: 1366px) and (min-height: 1024px) and (orientation: portrait) {
  .resource-layout {
    max-height: calc(100vh - 140px);
    padding: 20px;
  }
}

.resource-header { 
  font-size: 18px; 
  font-weight: bold; 
  margin-bottom: 15px; 
  color: #333; 
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 资源包列表视图样式 */
.pack-list-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 20px;
  padding: 10px;
  background: #f0f9ff;
  border-radius: 8px;
  line-height: 1.5;
  text-align: center;
}

.pack-grid {
  display: grid;
  grid-template-columns: 1fr; /* 默认单列，平板改为矩阵 */
  gap: 16px;
  margin-bottom: 20px;
}

/* 平板矩阵布局 */
@media (min-width: 768px) {
  .pack-grid {
    grid-template-columns: repeat(2, 1fr); /* 平板2列 */
  }
}

/* 横向平板大屏幕优化 */
@media (min-width: 1024px) and (orientation: portrait) {
  .pack-grid {
    gap: 20px;
  }
}

/* 手机端保持单列 */
@media (max-width: 767px) {
  .pack-grid {
    grid-template-columns: 1fr;
  }
}

.pack-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.pack-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
  border-color: #e6f7ff;
}

.pack-card:active {
  transform: translateY(0);
}

.pack-card-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.pack-card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.pack-card-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0 0 6px 0;
}

.pack-card-desc {
  font-size: 13px;
  color: #666;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.pack-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #888;
}

.view-hint {
  font-size: 12px;
  color: #07c160;
  font-weight: 500;
}

/* 资源包详情视图样式 */
.detail-header {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.back-btn {
  margin-bottom: 16px;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.detail-title h2 {
  font-size: 22px;
  color: #333;
  margin: 0;
}

.detail-description {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin: 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-content {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.image-count-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.image-gallery {
  margin-bottom: 20px;
}

.resource-grid-item {
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 8px;
  overflow: hidden;
}

.resource-grid-item:active {
  transform: scale(0.98);
}

.resource-grid-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.img-tag { 
  font-size: 12px; 
  color: #555; 
  text-align: center; 
  margin-top: 6px; 
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #ebedf0;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-images {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.empty-images p {
  margin-top: 10px;
  font-size: 14px;
}

.pack-tip {
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e8 100%);
  border-left: 4px solid #07c160;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  margin-top: 20px;
  line-height: 1.5;
}

.action-footer { 
  margin-top: 30px; 
  padding-bottom: 40px; 
}
</style>
