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
        <div class="stars-summary">当前总计获得：<span>{{ totalStars }}</span> 个太阳</div>
        <div class="trees-scene" aria-hidden="true"></div>

        <div class="tree-label tree-a">
          <div class="title">了解</div>
          <div class="sub">已获得 1 ☀</div>
        </div>

        <div class="tree-label tree-b">
          <div class="title">记录</div>
          <div class="sub">已获得 {{ stage3Stars }} ☀</div>
        </div>

        <div class="tree-label tree-c">
          <div class="title">试写</div>
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
              class="check-row"
              :class="{ active: hasShared }"
              @click="toggleShared"
            >
              <span>2.我分享了我的习作。</span>
              <span class="square" :class="{ checked: hasShared }">
                {{ hasShared ? '✓' : '' }}
              </span>
            </button>
          </div>
          <div class="stage5-star-tip">试写环节获得：{{ stage5Stars }} 个太阳 ☀</div>
        </section>
      </div>

    </div>

    <div v-else class="certificate-wrap">
      <span class="cert-deco leaf leaf-a" aria-hidden="true"></span>
      <span class="cert-deco leaf leaf-b" aria-hidden="true"></span>
      <span class="cert-deco leaf leaf-c" aria-hidden="true"></span>
      <span class="cert-deco flower flower-a" aria-hidden="true"></span>
      <span class="cert-deco flower flower-b" aria-hidden="true"></span>
      <span class="cert-deco ladybug" aria-hidden="true"></span>
      <div class="certificate">
        <div class="cert-inner">
          <span class="vine-corner vine-tl" aria-hidden="true"></span>
          <span class="vine-corner vine-tr" aria-hidden="true"></span>
          <span class="vine-corner vine-bl" aria-hidden="true"></span>
          <span class="vine-corner vine-br" aria-hidden="true"></span>
          <div class="cert-title">荣 誉 奖 状</div>
          <div class="cert-body">
            <p>亲爱的 <span class="strong-name">{{ displayName }}</span> 同学：</p>
            <p class="indent-line">在今天的学习中，你种下了一颗小种子，并且你共获得了<span class="strong-num">{{ totalStars }}</span>个小太阳！</p>
            <p class="indent-line">根据你的表现，特授予你以下称号：</p>
            <p class="badge-title-row">
              <span class="badge-star" aria-hidden="true">☀</span>
              <span class="badge-title">{{ awardTitle }}</span>
              <span class="badge-star" aria-hidden="true">☀</span>
            </p>
          </div>
          <div class="cert-footer">
            <span>重庆市人民小学校</span>
            <span>{{ todayText }}</span>
          </div>
        </div>
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
const todayText = new Date().toLocaleDateString();

const awardTitle = computed(() => {
  if (totalStars.value >= 5) return '小小植物学家';
  if (totalStars.value >= 3) return '优秀观察员';
  return '植物好朋友';
});

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

/* 树木路标：手账便利贴 */
.tree-label {
  position: absolute;
  z-index: 2;
  padding: 10px 14px;
  border-radius: 6px;
  background: #FAF7EA;
  border: 2px solid #E3DBC7;
  color: #5A4C43;
  text-align: center;
  box-shadow: 0 4px 0 #E3DBC7; /* 坚实的积木阴影 */
}

.tree-label .title {
  font-size: 24px;
  font-weight: 900;
  line-height: 1.2;
}

.tree-label .sub {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 800;
  color: #D98C3A;
}

.tree-a { left: 13%; bottom: 9%; width: 120px; transform: rotate(-2deg); }
.tree-b { left: 42%; bottom: 9%; width: 120px; transform: rotate(1deg); }
.tree-c { right: 13%; bottom: 70%; width: 120px; transform: rotate(-1.5deg); }

/* --- 试写评价面板（右下角打卡框） --- */
.stage5-check-card {
  position: absolute;
  z-index: 2;
  right: 3%;
  bottom: 5%;
  width: min(30vw, 360px);
  background: #FDFBF2;
  border: 2px dashed #D4CBB3;
  border-radius: 16px;
  padding: 20px 16px;
  box-shadow: 4px 12px 30px rgba(90, 76, 67, 0.12);
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
  font-size: 17px;
  font-weight: 800;
  color: #5C8D6D; /* 绿色标题 */
}

/* 选项条：厚纸板按钮 */
.check-row {
  width: 100%;
  border: 2px solid #E3DBC7;
  border-radius: 10px;
  background: #FAF7EA;
  padding: 12px 14px;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  cursor: pointer;
  min-height: 58px;
  font-size: 18px;
  font-weight: 800;
  color: #5A4C43;
  box-shadow: 0 4px 0 #E3DBC7; /* 坚实阴影 */
  transition: all 0.1s ease;
}

.check-row.sub {
  margin-left: 8px;
  width: calc(100% - 8px);
  font-size: 16px;
  font-weight: 700;
  min-height: 52px;
}

/* 选中状态：按压 */
.check-row.active {
  background: #5C8D6D;
  border-color: #3A664A;
  color: #FDFBF2;
  box-shadow: 0 0 0 #3A664A;
  transform: translateY(4px);
}

/* 勾选框 */
.square {
  width: 34px;
  height: 34px;
  border: 2px dashed #D4CBB3;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #5C8D6D;
  font-size: 20px;
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


/* ================================================== */
/*               第二部分：荣誉奖状视图                 */
/* ================================================== */
.certificate-wrap {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: transparent; /* 背景继续使用最外层的纸张色 */
}

/* 奖状外框：精装绘本边缘感 */
.certificate {
  width: min(92vw, 860px);
  position: relative;
  z-index: 2;
  background: #FDFBF2; /* 羊皮纸色 */
  border-radius: 8px; /* 弱化圆角，更像真实纸张 */
  padding: 16px;
  box-shadow: 
    0 0 0 1px #E3DBC7, 
    0 18px 40px rgba(90, 76, 67, 0.2);
}

/* 奖状内页：复古细线框 */
.cert-inner {
  position: relative;
  border: 2px solid #C07953; /* 陶土砖红色复古边框 */
  outline: 1px solid #C07953;
  outline-offset: -6px; /* 双层复古线框 */
  border-radius: 2px;
  background: #FDFBF2;
  padding: 40px 30px 34px;
}

.cert-title {
  text-align: center;
  font-size: 48px;
  font-weight: 900;
  letter-spacing: 16px;
  margin-bottom: 30px;
  color: #B44A30; /* 复古印章红 */
  text-shadow: 2px 2px 0 rgba(227, 219, 199, 0.8); /* 厚重的排版阴影 */
}

.cert-body {
  font-size: 24px;
  color: #5A4C43;
  line-height: 2;
  font-weight: 700;
}

.cert-body p {
  margin: 0;
  text-indent: 0;
}

.cert-body p.indent-line {
  text-indent: 2em;
}

/* 高亮文字：马克笔下划线 */
.strong-name,
.strong-num {
  font-weight: 900;
  color: #5C8D6D;
  padding: 0 6px;
  position: relative;
  display: inline-block;
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

.badge-title-row {
  margin-top: 20px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  text-indent: 0;
}

.badge-title {
  font-size: 42px;
  font-weight: 900;
  color: #D98C3A; /* 暖金橘色 */
  letter-spacing: 2px;
  text-shadow: 2px 2px 0 rgba(227, 219, 199, 0.8);
}

.badge-star {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #FDFBF2;
  background: #D98C3A;
  box-shadow: 2px 2px 0 #A86522; /* 实体阴影 */
  border: 2px solid #FDFBF2;
}

.cert-footer {
  margin-top: 40px;
  display: flex;
  justify-content: space-between;
  font-size: 18px;
  font-weight: 800;
  color: #8A7C73;
}

/* --- 周边装饰：水彩植物风微调 --- */
.cert-deco {
  position: absolute;
  z-index: 3;
  pointer-events: none;
}

.leaf {
  width: 34px;
  height: 22px;
  background: #87B392; /* 水彩森绿 */
  border-radius: 22px 22px 22px 4px;
  box-shadow: 2px 4px 8px rgba(90, 76, 67, 0.15);
}

.leaf-a { top: 60px; left: 60px; transform: rotate(-24deg); }
.leaf-b { right: 50px; top: 80px; transform: rotate(18deg) scale(1.15); }
.leaf-c { right: 100px; bottom: 70px; transform: rotate(-34deg); }

.flower {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #F6DA73; /* 暖黄 */
  box-shadow: 0 0 0 4px rgba(246, 218, 115, 0.4);
}

.flower-a { left: 100px; bottom: 90px; }
.flower-b { right: 130px; top: 130px; }

.ladybug {
  width: 18px;
  height: 18px;
  right: 70px;
  bottom: 110px;
  border-radius: 50%;
  background: #C75C5C; /* 砖红 */
  box-shadow: 2px 2px 6px rgba(90, 76, 67, 0.2);
}

.ladybug::before {
  content: "";
  position: absolute;
  left: 8px;
  top: 1px;
  width: 2px;
  height: 16px;
  background: #3A2D2D;
}

.ladybug::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 36% 42%, #3A2D2D 0 1.5px, transparent 1.7px),
    radial-gradient(circle at 65% 30%, #3A2D2D 0 1.4px, transparent 1.6px),
    radial-gradient(circle at 62% 64%, #3A2D2D 0 1.5px, transparent 1.7px);
}

/* 四角藤蔓改为复古装饰线 */
.vine-corner {
  position: absolute;
  width: 30px;
  height: 30px;
  pointer-events: none;
  border: 3px solid #C07953;
}
.vine-tl { top: -6px; left: -6px; border-right: 0; border-bottom: 0; }
.vine-tr { top: -6px; right: -6px; border-left: 0; border-bottom: 0; }
.vine-bl { bottom: -6px; left: -6px; border-right: 0; border-top: 0; }
.vine-br { bottom: -6px; right: -6px; border-left: 0; border-top: 0; }

.vine-corner::after { display: none; } /* 去掉原版的渐变小点 */


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
  .tree-label .title { font-size: 20px; }
  .tree-label .sub { font-size: 16px; }
  .stage5-check-card { width: min(29vw, 300px); top: 43%; right: 5.5%; }
  .tree-a { left: 11%; width: 150px; }
  .tree-b { left: 39%; width: 150px; }
  .tree-c { right: 20%; width: 110px; top: 19%; }
  .cert-title { font-size: 38px; letter-spacing: 10px; }
  .cert-body { font-size: 20px; }
  .badge-title { font-size: 32px; }
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
    padding: 16px;
  }
  .check-row { min-height: 50px; font-size: 16px; }
  .check-row.sub { font-size: 15px; }
  
  .tree-label .title { font-size: 18px; }
  .tree-label .sub { font-size: 14px; }
  .tree-a { left: 7%; bottom: 23%; width: 120px; }
  .tree-b { left: 34%; bottom: 23%; width: 120px; }
  .tree-c { right: 10%; top: 17%; width: 90px; }

  .certificate-wrap { padding: 16px; }
  .certificate { width: min(96vw, 860px); padding: 12px; }
  .cert-inner { padding: 30px 18px 24px; }
  .cert-title { font-size: 32px; letter-spacing: 6px; margin-bottom: 20px;}
  .cert-body { font-size: 18px; }
  .badge-title-row { gap: 8px; }
  .badge-title { font-size: 28px; }
  .badge-star { width: 28px; height: 28px; font-size: 16px; }
  .cert-footer { font-size: 14px; margin-top: 24px;}
  .leaf, .flower, .ladybug { transform: scale(0.8); }
}
</style>
