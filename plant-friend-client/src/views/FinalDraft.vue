<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">我与植物朋友共成长</div>
      <van-button
        v-if="!showCertificate"
        type="primary"
        round
        size="small"
        :loading="isSubmitting"
        :disabled="!canGoNext"
        loading-text="提交中"
        @click="submitStage5"
        class="top-nav-action final-submit-attention"
      >
        提交
      </van-button>
      <span v-else class="top-nav-spacer" aria-hidden="true"></span>
    </div>

    <div v-if="!showCertificate" class="main-board">
      <div class="vine-stage">
        <div class="stars-summary">当前总计获得：<span>{{ totalStars }}</span> 缕阳光</div>
        <div class="trees-scene" aria-hidden="true"></div>

        <div class="tree-label tree-a">
          <div class="label-line">了解 <span class="label-reward">获得1</span> <img src="/sun.svg" alt="" class="sun-inline-icon" /></div>
        </div>

        <div class="tree-label tree-b">
          <div class="label-line">记录 <span class="label-reward">获得1</span> <img src="/sun.svg" alt="" class="sun-inline-icon" /></div>
        </div>

        <div class="tree-label tree-c">
          <div class="label-line">试写</div>
        </div>

        <section class="stage5-check-card">
          <div class="eval-box">
            <div class="group-title">1.我试着写清楚了。</div>
            
            <button
              type="button"
              class="check-row sub"
              :class="{ active: hasMultiaspect, disabled: false }"
              @click="toggleMultiaspect"
            >
              <span>(1)我从多方面介绍了植物朋友。</span>
              <span class="square" :class="{ checked: hasMultiaspect }">
                {{ hasMultiaspect ? '✓' : '' }}
              </span>
            </button>

            <button
              type="button"
              class="check-row sub"
              :class="{ active: hasOrderly, disabled: false }"
              @click="toggleOrderly"
            >
              <span>(2)我是把几个方面连起来写的。</span>
              <span class="square" :class="{ checked: hasOrderly }">
                {{ hasOrderly ? '✓' : '' }}
              </span>
            </button>

            <button
              type="button"
              class="check-row main"
              :class="{ active: hasShared }"
              @click="toggleShared"
            >
              <span>2.我分享了我的习作。</span>
              <span class="square" :class="{ checked: hasShared }">
                {{ hasShared ? '✓' : '' }}
              </span>
            </button>
          </div>
          <div class="stage5-star-tip">试写环节获得：{{ stage5Stars }} 缕阳光 <img src="/sun.svg" alt="" class="sun-inline-icon" /></div>
        </section>
      </div>

    </div>

    <div v-else class="certificate-wrap">
      <div class="certificate-scene" aria-hidden="true"></div>
      <div class="certificate-copy">
        <p class="cert-main-text">
          亲爱的 <span class="strong-name">{{ displayName }}</span> 同学，在今天的学习中，你种下了一颗种子，并且一共为它获得了
          <span class="strong-num">{{ totalStars }}</span> 缕阳光，在你的呵护下，它已经生根发芽……
        </p>
      </div>
      <div class="certificate-book-area" aria-hidden="true">
        <div class="certificate-book-cover"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import axios from 'axios';
import { showToast } from 'vant';
import confetti from 'canvas-confetti';
import { useUserStore } from '../store/user';
import { NEXT_BUTTON_KEYS } from '../constants/nextButtonControls';

const userStore = useUserStore();

const isSubmitting = ref(false);
const showCertificate = ref(false);
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.finalDraft));

const hasMultiaspect = ref(false);  
const hasOrderly = ref(false);      
const hasShared = ref(false);      

const toggleMultiaspect = () => {
  hasMultiaspect.value = !hasMultiaspect.value;
};

const toggleOrderly = () => {
  hasOrderly.value = !hasOrderly.value;
};

const toggleShared = () => {
  hasShared.value = !hasShared.value;
};

const stage1Stars = computed(() => Number(userStore.stage1Stars ?? 1));
const stage3Stars = computed(() => Number(userStore.stage3Stars ?? 0));

const stage5Stars = computed(() => {
  return Number(hasMultiaspect.value) + Number(hasOrderly.value) + Number(hasShared.value);
});

const totalStars = computed(() => stage1Stars.value + stage3Stars.value + stage5Stars.value);

const displayName = computed(() => userStore.studentName || '小朋友');
const launchConfetti = () => {
  const end = Date.now() + 2200;
  const defaults = { startVelocity: 35, spread: 100, ticks: 80, zIndex: 1000 };

  const timer = setInterval(() => {
    const left = end - Date.now();
    if (left <= 0) {
      clearInterval(timer);
      return;
    }

    const ratio = left / 2200;
    const count = Math.max(18, Math.floor(60 * ratio));

    confetti({ ...defaults, particleCount: count, origin: { x: 0.15, y: 0.15 } });
    confetti({ ...defaults, particleCount: count, origin: { x: 0.85, y: 0.2 } });
  }, 220);
};

const submitStage5 = async () => {
  if (!canGoNext.value) return;
  if (isSubmitting.value) return;

  isSubmitting.value = true;
  try {
    const checks = [];
    if (hasMultiaspect.value) {
      checks.push('(1)我从多方面介绍了植物朋友');
    }
    if (hasOrderly.value) {
      checks.push('(2)我是把几个方面连起来写的。');
    }
    if (hasShared.value) {
      checks.push('2.我分享了我的习作。');
    }
    
    await axios.post('/api/student/stage5/submit', {
      student_id: String(userStore.studentId || ''),
      stage5_checks: checks,
      total_stars: totalStars.value,
    });
  } catch (error) {
    if (error?.response?.status === 404) {
      await axios.post('/api/student/stage5/final', {
        student_id: String(userStore.studentId || ''),
      });
    } else {
      showToast('提交失败，请重试');
      isSubmitting.value = false;
      return;
    }
  }

  if (typeof userStore.finishAll === 'function') {
    userStore.finishAll();
  }

  showCertificate.value = true;
  launchConfetti();
  showToast({ message: '恭喜你完成全部挑战！', type: 'success' });
  isSubmitting.value = false;
};
</script>

<style scoped>
/* =========== 全局背景手账化 =========== */
.stage-container {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #F4F1E1; /* 复古牛皮纸色底 */
}

/* =========== 顶部导航栏 =========== */
.top-nav {
  min-height: 56px;
  padding: max(0px, env(safe-area-inset-top)) 16px 0 16px;
  display: grid;
  grid-template-columns: 132px 1fr 132px;
  align-items: center;
  gap: 8px;
  background: #FDFBF2; 
  border-bottom: 2px dashed #D4CBB3; 
  box-shadow: 0 4px 10px rgba(90, 76, 67, 0.05); 
  flex-shrink: 0;
  z-index: 10;
}

.top-nav-title {
  font-size: 21px;
  font-weight: 800;
  color: #5A4C43; 
  letter-spacing: 1px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-nav-spacer {
  width: 100%;
}

.top-nav-action {
  width: 100%;
  justify-self: end;
}

/* =========== 3D纸板按钮 & 跳动动画 =========== */
:deep(.van-button--primary) {
  background-color: #5C8D6D !important;
  border-color: #5C8D6D !important;
  box-shadow: 0 4px 0 #3A664A !important;
  color: #FDFBF2 !important;
  transition: all 0.1s;
}

:deep(.van-button--primary:active) {
  transform: translateY(4px) !important;
  box-shadow: 0 0 0 #3A664A !important;
}

:deep(.van-button--primary:disabled) {
  background-color: #E3DBC7 !important;
  border-color: #E3DBC7 !important;
  color: #A3968C !important;
  box-shadow: none !important;
  opacity: 1 !important;
  transform: none !important;
  animation: none !important; /* 禁用时停止跳动 */
}

/* 手账风格的“引人注意”动画（模拟按钮物理弹跳） */
:deep(.final-submit-attention.van-button:not(:disabled)) {
  animation: paperBtnPulse 2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes paperBtnPulse {
  0%, 100% { transform: translateY(0); box-shadow: 0 4px 0 #3A664A; }
  50% { transform: translateY(-3px); box-shadow: 0 7px 0 #3A664A; } /* 微微弹起 */
}


/* ================================================== */
/*               第一部分：成长地图视图                 */
/* ================================================== */
.main-board {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 24px 20px;
  box-sizing: border-box;
}

/* 左上角总计标签：手账小挂签 */
.stars-summary {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 3;
  background: #FDFBF2;
  border: 2px dashed #D4CBB3;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 19px;
  font-weight: 800;
  color: #5A4C43;
  text-align: left;
  box-shadow: 2px 4px 10px rgba(90, 76, 67, 0.1);
  transform: rotate(-1deg);
}

.stars-summary span {
  color: #D98C3A; /* 暖橘色太阳数 */
  font-size: 26px;
  font-weight: 900;
}

/* 地图背景：变成一张贴上去的剪贴画 */
.vine-stage {
  flex: 1;
  position: relative;
  min-height: 0;
  border-radius: 12px;
  background: #FFFFFF;
  border: 4px solid #FDFBF2; /* 相纸白边 */
  box-shadow: 0 0 0 1px #E3DBC7, 4px 12px 30px rgba(90, 76, 67, 0.15); /* 双层边缘+阴影 */
  overflow: hidden;
}

.trees-scene {
  position: absolute;
  inset: 0;
  background-image: url('/final-draft/three-trees.jpg');
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

/* 树木路标：贴合背景木牌 */
.tree-label {
  position: absolute;
  z-index: 2;
  width: 200px;
  padding: 0;
  background: transparent;
  border: 0;
  color: #5f3e23;
  text-align: center;
  text-shadow: 0 1px 0 rgba(255, 235, 210, 0.5);
}

.tree-label .label-line {
  font-size: 33px;
  font-weight: 900;
  line-height: 1.1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tree-label .label-reward {
  font-size: 0.68em;
  color: #a6661f;
  font-weight: 900;
}

.tree-a { left: 26.5%; top: 42.5%; transform: rotate(-1deg); }
.tree-b { left: 26.5%; top: 53%; transform: rotate(0.4deg); }
.tree-c { left: 26.5%; top: 62.5%; transform: rotate(-0.5deg); }

/* --- 试写评价面板（右侧留空区） --- */
.stage5-check-card {
  position: absolute;
  z-index: 2;
  right: 2.2%;
  top: 50%;
  bottom: auto;
  width: min(36vw, 470px);
  background: #FDFBF2;
  border: 2px dashed #D4CBB3;
  border-radius: 16px;
  padding: 24px 18px;
  box-shadow: 4px 12px 30px rgba(90, 76, 67, 0.12);
  transform: translateY(-50%) scale(1.02);
  transform-origin: center right;
}

/* 胶带装饰 */
.stage5-check-card::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%) rotate(2deg);
  width: 100px;
  height: 24px;
  background-color: rgba(135, 179, 146, 0.6);
  box-shadow: 1px 2px 4px rgba(0,0,0,0.05);
  border-radius: 2px;
  z-index: 10;
}

.card-title {
  font-size: 18px;
  font-weight: 900;
  color: #5A4C43;
  text-align: center;
  margin-bottom: 12px;
}

.eval-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.group-title {
  font-size: 20px;
  font-weight: 800;
  color: #5C8D6D; /* 绿色标题 */
}

/* 选项条：厚纸板按钮 */
.check-row {
  width: 100%;
  border: 2px solid #E3DBC7;
  border-radius: 10px;
  background: #FAF7EA;
  padding: 14px 16px;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  cursor: pointer;
  min-height: 66px;
  font-size: 20px;
  font-weight: 800;
  color: #5A4C43;
  box-shadow: 0 4px 0 #E3DBC7; /* 坚实阴影 */
  transition: all 0.1s ease;
}

.check-row.sub {
  margin-left: 8px;
  width: calc(100% - 8px);
  font-size: 18px;
  font-weight: 700;
  min-height: 58px;
}

.check-row.main {
  color: #5C8D6D;
}

/* 选中状态：按压 */
.check-row.active {
  background: #5C8D6D;
  border-color: #3A664A;
  color: #FDFBF2;
  box-shadow: 0 4px 0 #3A664A;
  transform: none;
}

/* 勾选框 */
.square {
  width: 44px;
  height: 44px;
  border: 2px dashed #D4CBB3;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #5C8D6D;
  font-size: 24px;
  font-weight: 900;
  flex-shrink: 0;
  background: transparent;
  transition: all 0.2s;
}

.check-row.active .square.checked {
  border: none;
  background: #FDFBF2;
  color: #5C8D6D;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  transform: scale(1.1) rotate(-5deg);
}

.stage5-star-tip {
  margin-top: 14px;
  text-align: center;
  font-size: 16px;
  font-weight: 900;
  color: #D98C3A;
  background: #FFF9D2; /* 浅黄高亮 */
  padding: 6px;
  border-radius: 6px;
}

.sun-inline-icon {
  width: 1em;
  height: 1em;
  vertical-align: -0.08em;
}


/* ================================================== */
/*               第二部分：荣誉奖状视图                 */
/* ================================================== */
.certificate-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
  isolation: isolate;
  position: relative;
  overflow: hidden;
  background: #dff3ff;
}

.certificate-scene {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(180deg, rgba(0, 0, 0, 0.32) 0%, rgba(0, 0, 0, 0.32) 100%),
    linear-gradient(90deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.02) 45%, rgba(255, 255, 255, 0.02) 100%),
    url('/final-draft/background.jpg');
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.certificate-copy {
  position: absolute;
  z-index: 2;
  left: 5.5%;
  top: 50%;
  transform: translateY(-50%);
  width: min(36vw, 520px);
  padding: 18px 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 12px 30px rgba(22, 48, 35, 0.16);
  backdrop-filter: blur(3px);
}

.cert-main-text {
  margin: 0;
  color: #274c37;
  font-size: clamp(24px, 2vw, 34px);
  line-height: 1.75;
  font-weight: 800;
  text-align: left;
  text-indent: 2em;
}

.certificate-book-area {
  position: absolute;
  z-index: 2;
  right: 7vw;
  top: 50%;
  transform: translateY(-50%);
  width: min(34vw, 500px);
}

.certificate-book-cover {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 20px;
  border: 0;
  background-image: url('/final-draft/book-page.png');
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  background-color: transparent;
}


/* 高亮文字：马克笔下划线 */
.strong-name,
.strong-num {
  font-weight: 900;
  color: #5C8D6D;
  padding: 0 2px;
  position: relative;
  display: inline;
}
.strong-name::after,
.strong-num::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 0;
  width: 100%;
  height: 8px;
  background: rgba(246, 218, 115, 0.5); /* 鹅黄下划线 */
  z-index: -1;
  border-radius: 4px;
}


/* =========== 组件覆盖尺寸 =========== */
:deep(.van-button--large) {
  height: 54px;
  font-size: 22px;
  font-weight: 800;
}

:deep(.top-nav-action.van-button) {
  height: 40px;
  padding-inline: 16px;
  font-size: 15px;
  font-weight: 800;
}


/* =========== 响应式适配 =========== */
@media (max-width: 1200px) {
  .tree-label { width: 180px; }
  .tree-label .label-line { font-size: 30px; }
  .stage5-check-card { width: min(38vw, 430px); right: 1.6%; top: 50%; bottom: auto; transform: translateY(-50%) scale(0.95); }
  .tree-a { left: 23%; top: 41%; }
  .tree-b { left: 23%; top: 52.3%; }
  .tree-c { left: 23%; top: 63.5%; }
  .certificate-copy { width: min(40vw, 500px); left: 4.8%; }
  .cert-main-text { font-size: clamp(20px, 2.1vw, 30px); }
  .certificate-book-area { right: 4vw; width: min(36vw, 460px); }
}

@media (max-width: 900px) {
  .top-nav {
    grid-template-columns: 112px 1fr 112px;
    padding-inline: 10px;
  }
  :deep(.top-nav-action.van-button) {
    font-size: 14px;
    padding-inline: 12px;
  }
  .main-board { padding: 12px; }
  .stars-summary { font-size: 16px; left: 10px; top: 10px; padding: 6px 10px; }
  .stars-summary span { font-size: 20px; }
  
  .stage5-check-card {
    right: 4%;
    width: 92%;
    top: auto;
    bottom: 5%;
    transform: none;
    padding: 16px;
  }
  .check-row { min-height: 50px; font-size: 16px; }
  .check-row.sub { font-size: 15px; }
  
  .tree-label .label-line { font-size: 20px; }
  .tree-a { left: 7%; top: 44%; width: 120px; }
  .tree-b { left: 7%; top: 53.5%; width: 120px; }
  .tree-c { left: 7%; top: 63%; width: 120px; }

  .certificate-copy {
    left: 4%;
    right: 4%;
    top: 14%;
    width: auto;
    transform: none;
    padding: 14px 14px;
  }
  .cert-main-text { font-size: 18px; line-height: 1.65; }
  .certificate-book-area {
    right: 4%;
    top: auto;
    bottom: 4%;
    transform: none;
    width: min(42vw, 300px);
  }
}
</style>
