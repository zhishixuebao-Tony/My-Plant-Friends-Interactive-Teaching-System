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
        class="top-nav-action"
      >
        完成并领取奖状
      </van-button>
      <span v-else class="top-nav-spacer" aria-hidden="true"></span>
    </div>

    <div v-if="!showCertificate" class="main-board">
      <div class="vine-stage">
        <div class="stars-summary">当前总计获得：<span>{{ totalStars }}</span> 颗星</div>
        <div class="trees-scene" aria-hidden="true"></div>

        <div class="tree-label tree-a">
          <div class="title">观察</div>
          <div class="sub">已获得 1 ⭐</div>
        </div>

        <div class="tree-label tree-b">
          <div class="title">记录</div>
          <div class="sub">已获得 {{ stage3Stars }} ⭐</div>
        </div>

        <div class="tree-label tree-c">
          <div class="title">试写</div>
        </div>

        <section class="stage5-check-card">
          <div class="card-title">请勾选你试写环节完成的表现</div>
          <div class="eval-box">
            <div class="group-title">1. 我试着写清楚了：</div>
            
            <button
              type="button"
              class="check-row sub"
              :class="{ active: hasMultiaspect, disabled: false }"
              @click="toggleMultiaspect"
            >
              <span>（1）我能从多方面介绍</span>
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
              <span>（2）我能有顺序介绍</span>
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
              <span>2.我分享了我的习作</span>
              <span class="square" :class="{ checked: hasShared }">
                {{ hasShared ? '✓' : '' }}
              </span>
            </button>
          </div>
          <div class="stage5-star-tip">试写环节获得：{{ stage5Stars }} ⭐</div>
        </section>
      </div>

    </div>

    <div v-else class="certificate-wrap">
      <div class="certificate">
        <div class="cert-inner">
          <div class="cert-title">荣 誉 奖 状</div>
          <div class="cert-body">
            <p>亲爱的 <span class="strong-name">{{ displayName }}</span> 同学：</p>
            <p>在《我的植物朋友》探索中，你共获得了 <span class="strong-num">{{ totalStars }}</span> 颗星！</p>
            <p>根据你的表现，特授予你以下称号：</p>
            <p class="badge-title">{{ awardTitle }}</p>
          </div>
          <div class="cert-footer">
            <span>语文互动课堂</span>
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
  let stars = 0;
  
  if (hasMultiaspect.value || hasOrderly.value) {
    stars += 1;
  }
  
  if (hasShared.value) {
    stars += 1;
  }
  
  return stars;
});

const totalStars = computed(() => stage1Stars.value + stage3Stars.value + stage5Stars.value);

const displayName = computed(() => userStore.studentName || '小朋友');
const todayText = new Date().toLocaleDateString();

const awardTitle = computed(() => {
  if (totalStars.value >= 5) return '🌟 小小植物学家 🌟';
  if (totalStars.value >= 3) return '🌱 优秀观察员 🌱';
  return '🍃 植物好朋友 🍃';
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
      checks.push('（1）我能从多方面介绍。（√）');
    }
    if (hasOrderly.value) {
      checks.push('（2）我能有顺序介绍。（√）');
    }
    if (hasShared.value) {
      checks.push('我分享了我的习作');
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
.stage-container {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: radial-gradient(circle at 20% 10%, #f4fff1 0%, #eef8ef 45%, #e8f2e9 100%);
}

.top-nav {
  min-height: 56px;
  padding: max(0px, env(safe-area-inset-top)) 16px 0 16px;
  display: grid;
  grid-template-columns: 132px 1fr 132px;
  align-items: center;
  gap: 8px;
  background: linear-gradient(180deg, #ffffff 0%, #f4fbf6 100%);
  border-bottom: 1px solid #d9eede;
  box-shadow: 0 3px 10px rgba(45, 138, 78, 0.08);
  flex-shrink: 0;
}

.top-nav-title {
  font-size: 20px;
  font-weight: 800;
  color: #1f5d35;
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

.main-board {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 12px 16px 16px;
  box-sizing: border-box;
}

.stars-summary {
  position: absolute;
  top: 14px;
  left: 14px;
  z-index: 3;
  background: rgba(255, 255, 255, 0.94);
  border: 2px solid #ccead5;
  border-radius: 14px;
  padding: 8px 12px;
  font-size: 19px;
  font-weight: 800;
  color: #1f5d35;
  text-align: left;
}

.stars-summary span {
  color: #f49b00;
  font-size: 24px;
}

.vine-stage {
  flex: 1;
  position: relative;
  min-height: 0;
  border-radius: 26px;
  background: #ffffff;
  border: 2px solid #ccead5;
  overflow: hidden;
}

.trees-scene {
  position: absolute;
  inset: 0;
  background-image:
    url('/final-draft/three-trees.jpg');
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.tree-label {
  position: absolute;
  z-index: 2;
  padding: 8px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(203, 233, 212, 0.95);
  color: #1f5d35;
  text-align: center;
  box-shadow: 0 6px 14px rgba(23, 93, 54, 0.12);
}

.tree-label .title {
  font-size: 26px;
  font-weight: 900;
  line-height: 1.2;
}

.tree-label .sub {
  margin-top: 4px;
  font-size: 20px;
  font-weight: 800;
  color: #f49b00;
}

.tree-a { left: 13.2%; bottom: 9%; width: 120px; }
.tree-b { left: 42%; bottom: 9%; width: 120px; }
.tree-c { right: 14%; bottom: 58%; width: 120px; }

.stage5-check-card {
  position: absolute;
  z-index: 2;
  right: 6%;
  bottom: 5%;
  width: min(27vw, 310px);
  background: rgba(255, 253, 247, 0.70);
  border: 2px solid #f3dfb5;
  border-radius: 16px;
  padding: 8px;
  box-shadow: 0 8px 18px rgba(188, 140, 50, 0.12);
}

.card-title {
  font-size: 14px;
  font-weight: 800;
  color: #6f5518;
  margin-bottom: 6px;
}

.check-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.check-option {
  border: 2px solid #eadfca;
  border-radius: 16px;
  background: #fff;
  padding: 10px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  text-align: left;
}

.check-option.checked {
  border-color: #71be87;
  background: #f3fff6;
}

.check-box {
  width: 28px;
  height: 28px;
  border: 2px solid #c2cede;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #377dff;
  font-size: 18px;
  font-weight: 700;
  background: #f8fbff;
  flex-shrink: 0;
}

.check-box.checked {
  border-color: #377dff;
  background: #eaf1ff;
}

.check-label {
  font-size: 16px;
  font-weight: 700;
  color: #2f3b30;
  line-height: 1.35;
}

.stage5-star-tip {
  margin-top: 6px;
  text-align: right;
  font-size: 14px;
  font-weight: 800;
  color: #f49b00;
}

.eval-box {
  border: 1px solid #e1e8f5;
  border-radius: 10px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-height: 0;
}

.group-title {
  font-size: 13px;
  font-weight: 700;
  color: #2e4058;
  margin-top: 4px;
}

.check-row {
  width: 100%;
  border: 1px solid #d7e0ef;
  border-radius: 8px;
  background: #fff;
  padding: 7px 8px;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  cursor: pointer;
  min-height: 50px;
  font-size: 15px;
  font-weight: 600;
  color: #223247;
}

.check-row.sub {
  margin-left: 8px;
  width: calc(100% - 8px);
}

.check-row.active {
  border-color: #3a7bff;
  background: #f2f7ff;
}

.check-row.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.square {
  width: 32px;
  height: 32px;
  border: 2px solid #c2cede;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #377dff;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
  background: #f8fbff;
}

.square.checked {
  border-color: #377dff;
  background: #eaf1ff;
}

:deep(.van-button--large) {
  height: 54px;
  font-size: 22px;
  font-weight: 800;
}

:deep(.top-nav-action.van-button) {
  height: 34px;
  padding-inline: 10px;
  font-size: 13px;
  font-weight: 700;
}

:deep(.van-button--primary) {
  background: linear-gradient(90deg, #2d8a4e, #4aae67);
  border: 0;
}

.certificate-wrap {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: radial-gradient(circle at 50% 20%, #fff6d8 0%, #f8eecb 45%, #f2e2b4 100%);
}

.certificate {
  width: min(92vw, 860px);
  background: #fff6de;
  border-radius: 20px;
  padding: 14px;
  border: 5px solid #d4a93b;
  box-shadow: 0 14px 30px rgba(127, 88, 15, 0.2);
}

.cert-inner {
  border: 3px solid #e0bf69;
  border-radius: 14px;
  background: #fff9eb;
  padding: 24px;
}

.cert-title {
  text-align: center;
  font-size: 56px;
  font-weight: 900;
  letter-spacing: 10px;
  color: #c4472f;
  margin-bottom: 18px;
}

.cert-body {
  font-size: 26px;
  color: #5a4317;
  line-height: 1.8;
}

.strong-name,
.strong-num {
  font-weight: 900;
  color: #1f5d35;
}

.badge-title {
  margin-top: 12px;
  text-align: center;
  font-size: 40px;
  font-weight: 900;
  color: #1f5d35;
}

.cert-footer {
  margin-top: 18px;
  display: flex;
  justify-content: space-between;
  font-size: 18px;
  color: #8a6a2b;
}

@media (max-width: 1200px) {
  .tree-label .title { font-size: 20px; }
  .tree-label .sub { font-size: 16px; }
  .check-label { font-size: 15px; }
  .stage5-check-card { width: min(29vw, 300px); top: 43%; right: 5.5%; }
  .tree-a { left: 11%; width: 172px; }
  .tree-b { left: 39%; width: 172px; }
  .tree-c { right: 20%; width: 110px; top: 19%; }
  .cert-title { font-size: 44px; }
  .cert-body { font-size: 22px; }
  .badge-title { font-size: 32px; }
}

@media (max-width: 900px) {
  .top-nav {
    grid-template-columns: 112px 1fr 112px;
    padding-inline: 10px;
  }

  :deep(.top-nav-action.van-button) {
    font-size: 12px;
    padding-inline: 8px;
  }

  .main-board { padding: 10px; }
  .stars-summary { font-size: 16px; left: 10px; top: 10px; padding: 6px 10px; }
  .stars-summary span { font-size: 19px; }
  .stage5-check-card {
    right: 4%;
    width: 92%;
    top: auto;
    bottom: 5%;
  }
  .tree-label .title { font-size: 17px; }
  .tree-label .sub { font-size: 14px; }
  .tree-a { left: 7%; bottom: 23%; width: 132px; }
  .tree-b { left: 34%; bottom: 23%; width: 132px; }
  .tree-c { right: 10%; top: 17%; width: 90px; }
}
</style>
