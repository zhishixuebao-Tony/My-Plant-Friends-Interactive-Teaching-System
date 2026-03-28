<template>
  <div class="stage-container">
    <!-- 顶部导航 -->
    <van-nav-bar title="环节 1：我的感官观察站" fixed placeholder border />

    <div class="split-layout">
      <!-- 左侧：植物展示区 (显示课前预置照片) -->
      <div class="left-panel">
        <div class="panel-header">我的植物朋友照片</div>
        <div class="media-content">
          <van-image
            width="100%"
            height="100%"
            fit="contain"
            :src="userStore.prePhotoUrl"
          >
            <template #loading>
              <van-loading type="spinner" size="20" />
            </template>
            <template #error>这里是你的植物照片</template>
          </van-image>
        </div>
      </div>

      <!-- 右侧：感官选择区 -->
      <div class="right-panel">
        <div class="panel-header">我观察到了... (可多选)</div>
        
        <div class="scroll-content">
          <!-- 复选框组 -->
          <van-checkbox-group v-model="checkedItems" shape="square">
            <div 
              class="custom-check-card" 
              v-for="item in options" 
              :key="item.name"
              @click="toggleItem(item.name)"
              :class="{ 'is-active': checkedItems.includes(item.name) }"
            >
              <van-checkbox :name="item.name" ref="checkboxes" @click.stop>
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
            loading-text="正在提交..."
          >
            确认提交并进入下一步
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
import { showToast } from 'vant';

const userStore = useUserStore();
const loading = ref(false);
const checkedItems = ref([]);

// 观察选项定义
const options = [
  { name: '看了看', icon: '👀' },
  { name: '闻了闻', icon: '👃' },
  { name: '摸了摸', icon: '🤚' },
  { name: '听一听', icon: '👂' },
  { name: '想一想', icon: '💭' }
];

// 点击卡片任意位置切换选中状态 (针对平板优化)
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
    // 调用后端接口
    await submitSensoryApi(userStore.studentId, checkedItems.value);
    
    showToast({
      message: '记录成功！',
      type: 'success',
    });
    
    // 跳转到环节2
    userStore.currentStage = '2';
  } catch (err) {
    console.error(err);
    showToast('提交失败，请重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.stage-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
}

.split-layout {
  flex: 1;
  display: flex;
  overflow: hidden; /* 防止页面整体滚动 */
}

/* 左侧样式 */
.left-panel {
  flex: 1.2;
  background-color: #000;
  display: flex;
  flex-direction: column;
  padding: 15px;
}

.media-content {
  flex: 1;
  background-color: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
}

/* 右侧样式 */
.right-panel {
  flex: 1;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #ebedf0;
}

.panel-header {
  font-size: 20px;
  font-weight: 600;
  padding: 20px;
  color: #323233;
  border-bottom: 1px solid #f2f3f5;
}

.scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px 20px;
}

/* 自定义选项卡片 */
.custom-check-card {
  margin-bottom: 15px;
  padding: 20px;
  background-color: #f7f8fa;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.custom-check-card.is-active {
  background-color: #eafaf1;
  border-color: #07c160;
}

.check-label {
  display: flex;
  align-items: center;
  margin-left: 10px;
}

.emoji {
  font-size: 32px;
  margin-right: 15px;
}

.text {
  font-size: 22px;
  color: #323233;
}

/* 底部按钮 */
.action-footer {
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}

/* 强制调整 Vant 复选框图标大小 */
:deep(.van-checkbox__icon) {
  font-size: 26px;
}
</style>