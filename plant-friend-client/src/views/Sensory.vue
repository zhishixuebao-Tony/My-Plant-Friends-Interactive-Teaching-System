<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">了解我的植物朋友</div>
      <van-button
        type="primary"
        round
        size="small"
        :disabled="checkedItems.length === 0 || !canGoNext"
        :loading="loading"
        @click="onNextStep"
        class="top-nav-action"
      >
        提交
      </van-button>
    </div>

    <div class="stage-body">
      <section class="evaluate-panel">
        <header class="panel-header method-title">我用了哪些观察方法了解植物朋友？</header>

        <div class="option-list">
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

      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useUserStore } from '../store/user';
import { submitSensoryApi } from '../api/student';
import { showToast } from 'vant';
import { NEXT_BUTTON_KEYS } from '../constants/nextButtonControls';

const userStore = useUserStore();
const loading = ref(false);
const checkedItems = ref([]);
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.sensory));

const options = [
  { name: '看一看', icon: '👀' },
  { name: '闻一闻', icon: '👃' },
  { name: '摸一摸', icon: '✋' },
  { name: '听一听', icon: '👂' },
  { name: '尝一尝', icon: '👅' },
  { name: '其他', icon: '✨' },
];

const toggleItem = (name) => {
  if (checkedItems.value.includes(name)) {
    checkedItems.value = checkedItems.value.filter((v) => v !== name);
  } else {
    checkedItems.value.push(name);
  }
};

const onNextStep = async () => {
  if (!canGoNext.value) return;
  if (checkedItems.value.length === 0) return;

  loading.value = true;
  try {
    await submitSensoryApi(userStore.studentId, checkedItems.value);
    userStore.setSensorySelections(checkedItems.value);
    userStore.setStage('sensory-transition');
    showToast({ message: '提交成功', type: 'success' });
  } catch (error) {
    console.error(error);
    showToast('提交失败，请重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* =========== 全局背景手账化 =========== */
.stage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #F4F1E1; /* 整体页面变成复古牛皮纸色 */
}

/* =========== 顶部导航栏（融入纸张风格） =========== */
.top-nav {
  min-height: 56px;
  padding: max(0px, env(safe-area-inset-top)) 16px 0 16px;
  display: grid;
  grid-template-columns: 132px 1fr 132px;
  align-items: center;
  gap: 8px;
  background: #FDFBF2; /* 导航栏纸张色 */
  border-bottom: 2px dashed #D4CBB3; /* 虚线边缘 */
  box-shadow: 0 4px 10px rgba(90, 76, 67, 0.05); /* 柔和暖色阴影 */
  flex-shrink: 0;
  z-index: 10;
}

.top-nav-title {
  font-size: 21px;
  font-weight: 800;
  color: #5A4C43; /* 深棕灰字体 */
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 1px;
}

.top-nav-spacer {
  width: 100%;
}

.top-nav-action {
  width: 100%;
  justify-self: end;
}

/* 覆盖 Vant 按钮样式 - 3D手账风 */
:deep(.van-button--primary) {
  background-color: #5C8D6D !important;
  border-color: #5C8D6D !important;
  box-shadow: 0 4px 0 #3A664A !important;
  color: #FDFBF2 !important;
  transition: all 0.1s;
}

:deep(.van-button--primary:active) {
  transform: translateY(4px);
  box-shadow: 0 0 0 #3A664A !important;
}

/* 禁用状态的纸板质感 */
:deep(.van-button--primary:disabled) {
  background-color: #E3DBC7 !important;
  border-color: #E3DBC7 !important;
  color: #A3968C !important;
  box-shadow: none !important;
  opacity: 1 !important; /* 覆盖vant默认的透明度，保持纸板实色感 */
  transform: none !important;
}

/* =========== 内容区域 =========== */
.stage-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
  overflow: hidden;
}

/* 核心记录面板 - 手账内页质感 */
.evaluate-panel {
  background: #FDFBF2;
  border-radius: 16px;
  padding: 30px 24px 34px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  border: 2px dashed #D4CBB3;
  box-shadow: 4px 12px 30px rgba(90, 76, 67, 0.12);
  width: min(96%, 1220px);
  max-height: 100%;
  overflow: visible;
  position: relative; /* 为伪元素胶带定位 */
}

/* 面板顶部的小胶带装饰（纯CSS） */
.evaluate-panel::before {
  content: '';
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%) rotate(-2.5deg);
  width: 112px;
  height: 26px;
  background: rgba(215, 202, 171, 0.8);
  box-shadow: 0 1px 3px rgba(85, 70, 45, 0.14);
  border-radius: 1px;
  z-index: 8;
}

.panel-header {
  font-size: 16px;
  font-weight: 700;
  color: #5A4C43;
}

.method-title {
  font-size: 24px;
  font-weight: 900;
  text-align: center;
  margin-bottom: 10px;
  position: relative;
  display: inline-block;
  align-self: center;
}

/* 标题底部加一条马克笔风格的高亮线 */
.method-title::after {
  content: '';
  position: absolute;
  bottom: 0px;
  left: 0;
  width: 100%;
  height: 8px;
  background: rgba(246, 218, 115, 0.6); /* 暖黄色马克笔 */
  z-index: -1;
  border-radius: 4px;
}

/* =========== 选项列表（互动卡片） =========== */
.option-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  padding: 4px; /* 为阴影留出空间 */
}

/* 选项厚纸板样式 */
.option-card {
  width: 100%;
  min-height: 108px;
  border: 2px solid #E3DBC7;
  border-radius: 14px;
  background: #FAF7EA;
  padding: 0 16px 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  text-align: left;
  box-shadow: 0 6px 0 #E3DBC7; /* 坚实的底部阴影，像厚积木/纸板 */
  transition: all 0.15s ease;
}

/* 选中状态：按压下去，变绿 */
.option-card.active {
  background: #5C8D6D;
  border-color: #3A664A;
  box-shadow: 0 6px 0 #3A664A; /* 保持高度感，避免容器视觉缩小 */
  transform: none;
}

.option-text {
  font-size: 22px;
  color: #5A4C43;
  font-weight: 800;
  transition: color 0.15s;
}

/* 选中后文字变纸白色 */
.option-card.active .option-text {
  color: #FDFBF2;
}

/* 右侧勾选框 - 未选中像盖章区 */
.option-check {
  width: 44px;
  height: 44px;
  border-radius: 50%; /* 改成圆形更童趣 */
  border: 2px dashed #D4CBB3;
  background: transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 900;
  flex-shrink: 0;
  transition: all 0.2s;
}

/* 选中后的打钩状态 */
.option-check.checked {
  border: none;
  background: #FDFBF2;
  color: #5C8D6D; /* 绿色的钩 */
  box-shadow: 0 2px 6px rgba(0,0,0,0.15); /* 微微浮起 */
  transform: scale(1.1) rotate(-5deg); /* 选中时有一点俏皮的放大和倾斜 */
}


:deep(.van-button--large) {
  height: 44px;
}

:deep(.top-nav-action.van-button) {
  height: 40px;
  padding-inline: 18px;
  font-size: 16px;
  font-weight: 800;
}


/* =========== 平板竖屏/小屏幕适配 =========== */
@media (max-width: 900px) {
  .top-nav {
    grid-template-columns: 112px 1fr 112px;
    padding-inline: 10px;
  }

  :deep(.top-nav-action.van-button) {
    font-size: 14px;
    padding-inline: 14px;
  }

  .stage-body {
    padding: 12px;
  }

  .evaluate-panel {
    padding: 24px 16px 26px;
  }

  .method-title {
    font-size: 21px;
  }

  .option-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }

  .option-card {
    min-height: 96px;
    box-shadow: 0 4px 0 #E3DBC7;
  }
  
  .option-text {
    font-size: 19px;
  }
}
</style>
