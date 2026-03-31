<template>
  <div class="stage-container">
    <van-nav-bar title="环节 4：魔法资源包与知识闯关" fixed placeholder border />

    <div class="resource-layout">
      
      <!-- 1. 顶部魔法资源展示 -->
      <div class="resource-header">
        <van-icon name="photo-o" color="#07c160" /> 
        魔法资源图片 (点击放大查看)
      </div>
      
      <div class="image-gallery">
        <van-grid :column-num="3" gutter="10">
          <van-grid-item 
            v-for="(img, index) in mockResources" 
            :key="index"
            @click="onPreview(index)"
            class="resource-grid-item"
          >
            <van-image :src="img" radius="8" fit="cover" style="height: 120px;" />
            <div class="img-tag">资源 {{ index + 1 }}</div>
          </van-grid-item>
        </van-grid>
      </div>

      <!-- 2. 习题板块 (知识小闯关) -->
      <div class="quiz-section">
        <div class="quiz-title">
          <van-icon name="award-o" color="#f2bd27" /> 
          知识小闯关
        </div>

        <!-- 题 1：判断题 -->
        <div class="quiz-card">
          <p class="question-text">1. 植物生长不仅需要水分，还需要阳光和充足的营养。(判断题)</p>
          <van-radio-group v-model="q1" direction="horizontal">
            <van-radio name="正确">正确</van-radio>
            <van-radio name="错误">错误</van-radio>
          </van-radio-group>
          
          <!-- 答案反馈区 -->
          <div v-if="q1" class="ans-box" :class="q1 === '正确' ? 'right' : 'wrong'">
            <span v-if="q1 === '正确'">✨ 太棒了！回答正确。</span>
            <span v-else>💡 别灰心！阳光也是植物的好朋友哦。解析：植物的光合作用离不开阳光。</span>
          </div>
        </div>

        <!-- 题 2：选择题 -->
        <div class="quiz-card">
          <p class="question-text">2. 在描写植物朋友时，我们可以从哪些方面来描写？(选择题)</p>
          <van-radio-group v-model="q2" direction="horizontal">
            <van-radio name="A">A. 只有颜色</van-radio>
            <van-radio name="B">B. 颜色、气味、样子、感受</van-radio>
          </van-radio-group>
          
          <!-- 答案反馈区 -->
          <div v-if="q2" class="ans-box" :class="q2 === 'B' ? 'right' : 'wrong'">
            <span v-if="q2 === 'B'">✨ 你真聪明！观察非常全面。</span>
            <span v-else>💡 差一点点就对啦！我们要全方位观察植物。正确答案是 B。</span>
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
          :disabled="!q1 || !q2" 
          @click="submitStage4"
          :loading="loading"
          loading-text="正在保存进度..."
        >
          完成闯关，去写定稿
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

// 答题状态
const q1 = ref('');
const q2 = ref('');

// 模拟资源图片地址 (测试用，使用真实的占位图)
const mockResources = [
  'https://img.yzcdn.cn/vant/apple-1.jpg',
  'https://img.yzcdn.cn/vant/apple-2.jpg',
  'https://img.yzcdn.cn/vant/apple-3.jpg'
];

/**
 * 核心修复：点击图片放大预览，并静默上报点击次数
 */
const onPreview = async (index) => {
  // 1. 调用 Vant 预览大图
  showImagePreview({
    images: mockResources,
    startPosition: index,
    closeable: true,              // 显示右上角关闭按钮
    closeOnClickImage: true,      // 点击图片即可关闭
    closeOnClickOverlay: true,    // 点击黑底背景关闭
    teleport: 'body'              // 挂载到 body，防止被其他层级遮挡卡死
  });

  // 2. 向后端静默上报点击数据
  // 注意：这里的名称必须严格拼写为 "资源 1"（中间有空格），才能和教师端表格对应上！
  const resourceName = `资源 ${index + 1}`; 
  
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
  if (!q1.value || !q2.value) {
    return showToast('请先完成所有知识闯关题哦！');
  }

  loading.value = true;
  try {
    // 告诉后端：该学生已完成环节 4
    await axios.post('/api/student/stage4/complete-resources', {
      student_id: userStore.studentId
    });
    
    showToast({
      message: '知识闯关大成功！',
      type: 'success'
    });
    
    // 顺利进入环节 5
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
}

.resource-layout { 
  padding: 20px; 
  flex: 1;
  overflow-y: auto;
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

.image-gallery {
  margin-bottom: 30px;
}

.resource-grid-item {
  cursor: pointer;
  transition: transform 0.1s;
}

.resource-grid-item:active {
  transform: scale(0.95);
}

.img-tag { 
  font-size: 13px; 
  color: #666; 
  text-align: center; 
  margin-top: 8px; 
  background: #fff;
  padding: 2px 10px;
  border-radius: 10px;
  border: 1px solid #ebedf0;
}

.quiz-section { 
  margin-top: 20px; 
  padding-bottom: 20px;
}

.quiz-title { 
  font-size: 20px; 
  font-weight: bold; 
  margin-bottom: 20px; 
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.quiz-card { 
  background: #fff; 
  padding: 20px; 
  border-radius: 12px; 
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.question-text {
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 15px;
  line-height: 1.5;
}

.ans-box { 
  margin-top: 20px; 
  padding: 12px 15px; 
  border-radius: 8px; 
  font-size: 15px; 
  line-height: 1.6;
}

.ans-box.right { 
  background: #f0f9eb; 
  color: #67c23a; 
  border: 1px solid #e1f3d8;
}

.ans-box.wrong { 
  background: #fef0f0; 
  color: #f56c6c; 
  border: 1px solid #fde2e2;
}

.action-footer { 
  margin-top: 30px; 
  padding-bottom: 40px; 
}
</style>