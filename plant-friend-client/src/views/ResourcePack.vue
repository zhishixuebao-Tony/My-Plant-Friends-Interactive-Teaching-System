<template>
  <div class="stage-container">
    <van-nav-bar title="环节 4：魔法资源包与知识闯关" />

    <div class="resource-layout">
      <!-- 1. 顶部魔法资源展示 (横向滑动或列表) -->
      <div class="resource-header">🌟 魔法资源图片 (点击查看)</div>
      <div class="image-gallery">
        <van-grid :column-num="3" gutter="10">
          <van-grid-item v-for="(img, index) in mockResources" :key="index" @click="onPreview(index)">
            <van-image :src="img" radius="8" />
            <div class="img-tag">资源 {{ index + 1 }}</div>
          </van-grid-item>
        </van-grid>
      </div>

      <!-- 2. 习题板块 -->
      <div class="quiz-section">
        <div class="quiz-title">📝 知识小闯关</div>
        
        <!-- 题 1：判断题 -->
        <div class="quiz-card">
          <p>1. 植物生长不仅需要水分，还需要阳光和充足的营养。(判断题)</p>
          <van-radio-group v-model="q1" direction="horizontal" @change="checkQ1">
            <van-radio name="正确">正确</van-radio>
            <van-radio name="错误">错误</van-radio>
          </van-radio-group>
          <div v-if="q1" class="ans-box" :class="q1 === '正确' ? 'right' : 'wrong'">
            {{ q1 === '正确' ? '🌟 太棒了！回答正确。' : '💡 别灰心，阳光也是植物的好朋友哦！解析：植物的光合作用离不开阳光。' }}
          </div>
        </div>

        <!-- 题 2：选择题 -->
        <div class="quiz-card">
          <p>2. 在描写植物朋友时，我们可以从哪些方面来描写？(选择题)</p>
          <van-radio-group v-model="q2" direction="horizontal" @change="checkQ2">
            <van-radio name="A">A. 只有颜色</van-radio>
            <van-radio name="B">B. 颜色、气味、样子、感受</van-radio>
          </van-radio-group>
          <div v-if="q2" class="ans-box" :class="q2 === 'B' ? 'right' : 'wrong'">
            {{ q2 === 'B' ? '🌟 你真聪明！观察非常全面。' : '💡 差一点点就对啦！我们要全方位观察。正确答案是B。' }}
          </div>
        </div>
      </div>

      <!-- 底部提交 -->
      <div class="footer">
        <van-button 
          type="primary" 
          block 
          round 
          size="large" 
          :disabled="!q1 || !q2" 
          @click="submitStage4"
          :loading="loading"
        >
          完成闯关，去写定稿
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { completeResourceApi } from '../api/student';
import { showImagePreview, showToast } from 'vant';

const userStore = useUserStore();
const loading = ref(false);
const q1 = ref('');
const q2 = ref('');

// 模拟资源图片地址 (请确保这些图片地址是可用的)
const mockResources = [
  'https://img.yzcdn.cn/vant/apple-1.jpg',
  'https://img.yzcdn.cn/vant/apple-2.jpg',
  'https://img.yzcdn.cn/vant/apple-3.jpg'
];

const onPreview = async (index) => {
  // 1. 原有的图片放大逻辑
  showImagePreview({
    images: mockResources,
    startPosition: index,
    closeable: true,
  });

  // 2. 新增：向后端静默上报点击数据 (比如点了第一张图，名字叫"资源 1")
  const resourceName = encodeURIComponent(`资源 ${index + 1}`);
  try {
    // 调用我们在后端留好的点击上报接口
    await axios.post(`/api/student/track-resource-click/${userStore.studentId}/${resourceName}`);
  } catch (err) {
    console.warn("点击上报失败", err.response?.status, err.message);
  }
};

const submitStage4 = async () => {
  if (!q1.value || !q2.value) return showToast('请先完成所有习题哦！');
  
  loading.value = true;
  try {
    await completeResourceApi(userStore.studentId);
    showToast({
      message: '知识闯关大成功！',
      type: 'success'
    });
    userStore.currentStage = '5'; 
  } catch (err) {
    showToast('网络有点小脾气，请重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.resource-layout { padding: 20px; background: #f7f8fa; min-height: 90vh; }
.resource-header { font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #07c160; }
.img-tag { font-size: 12px; color: #999; text-align: center; margin-top: 5px; }
.quiz-section { margin-top: 30px; }
.quiz-title { font-size: 20px; font-weight: bold; margin-bottom: 20px; }
.quiz-card { background: #fff; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
.ans-box { margin-top: 15px; padding: 10px; border-radius: 8px; font-size: 16px; }
.ans-box.right { background: #f0f9eb; color: #67c23a; }
.ans-box.wrong { background: #fef0f0; color: #f56c6c; }
.footer { margin-top: 40px; padding-bottom: 40px; }
</style>