<template>
  <div class="stage-container">
    <div class="top-nav">我与植物朋友共成长</div>

    <div v-if="!showCertificate" class="main-board">
      <div class="vine-stage">
        <div class="stars-summary">当前总计获得：<span>{{ totalStars }}</span> 颗星</div>
        <svg class="vine-svg" viewBox="0 0 1200 680" preserveAspectRatio="none" aria-hidden="true">
          <path
            d="M 90 590 C 250 520, 330 450, 430 360 C 520 280, 620 230, 740 190 C 860 150, 980 100, 1110 70"
            class="vine-path"
          />
          <path
            d="M 170 560 C 250 580, 300 620, 350 660"
            class="vine-branch"
          />
          <path
            d="M 520 300 C 600 320, 650 360, 700 410"
            class="vine-branch"
          />
          <path
            d="M 820 160 C 900 180, 960 230, 1020 290"
            class="vine-branch"
          />
        </svg>

        <div class="fruit fruit-a" aria-hidden="true">
          <span class="leaf"></span>
          <span class="body">🍎</span>
        </div>
        <div class="fruit fruit-b" aria-hidden="true">
          <span class="leaf"></span>
          <span class="body">🍎</span>
        </div>
        <div class="fruit fruit-c current" aria-hidden="true">
          <span class="leaf"></span>
          <span class="body pulse">🍎</span>
        </div>

        <div class="node-label label-a">
          <div class="title">观察</div>
          <div class="sub">已获得 1 ⭐</div>
        </div>

        <div class="node-label label-b">
          <div class="title">记录</div>
          <div class="sub">已获得 {{ stage3Stars }} ⭐</div>
        </div>

        <div class="node-label label-c">
          <div class="title">试写</div>
        </div>

        <section class="stage5-check-card">
          <div class="card-title">请勾选你试写环节完成的表现</div>
          <div class="check-group">
            <button
              v-for="item in stage5Options"
              :key="item"
              type="button"
              class="check-option"
              :class="{ checked: stage5Checks.includes(item) }"
              @click="toggleStage5Check(item)"
            >
              <span class="check-label">{{ item }}</span>
              <span class="check-box" :class="{ checked: stage5Checks.includes(item) }">
                <span v-if="stage5Checks.includes(item)">✓</span>
              </span>
            </button>
          </div>
          <div class="stage5-star-tip">试写环节获得：{{ stage5Stars }} ⭐</div>
        </section>
      </div>

      <div class="action-footer">
        <van-button type="default" block round size="large" class="prev-btn" @click="goPrevStep">上一步</van-button>
        <van-button
          type="primary"
          block
          round
          size="large"
          :loading="isSubmitting"
          loading-text="正在提交..."
          @click="submitStage5"
        >
          完成全部挑战，领取荣誉证书
        </van-button>
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

      <div class="cert-actions">
        <van-button type="default" round size="large" @click="backToVinePage">上一步</van-button>
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

const userStore = useUserStore();

const isSubmitting = ref(false);
const showCertificate = ref(false);
const stage5Checks = ref([]);

const stage5Options = [
  '1. 我能写清楚',
  '2. 我愿意分享我的习作',
];

const toggleStage5Check = (item) => {
  if (stage5Checks.value.includes(item)) {
    stage5Checks.value = stage5Checks.value.filter((v) => v !== item);
  } else {
    stage5Checks.value = [...stage5Checks.value, item];
  }
};

const stage1Stars = computed(() => Number(userStore.stage1Stars ?? 1));
const stage3Stars = computed(() => Number(userStore.stage3Stars ?? 0));
const stage5Stars = computed(() => stage5Checks.value.length);
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
  if (isSubmitting.value) return;

  isSubmitting.value = true;
  try {
    await axios.post('/api/student/stage5/submit', {
      student_id: String(userStore.studentId || ''),
      stage5_checks: [...stage5Checks.value],
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

const goPrevStep = () => {
  userStore.setStage('4');
};

const backToVinePage = () => {
  showCertificate.value = false;
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
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #ffffff 0%, #f4fbf6 100%);
  border-bottom: 1px solid #d9eede;
  box-shadow: 0 3px 10px rgba(45, 138, 78, 0.08);
  font-size: 20px;
  font-weight: 800;
  color: #1f5d35;
  flex-shrink: 0;
}

.main-board {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 10px;
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
  position: relative;
  min-height: 0;
  border-radius: 26px;
  background: linear-gradient(165deg, #ffffff 0%, #f7fdf8 100%);
  border: 2px solid #ccead5;
  overflow: hidden;
}

.vine-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.vine-path {
  fill: none;
  stroke: #2d8a4e;
  stroke-width: 14;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 8 2;
  opacity: 0.95;
}

.vine-branch {
  fill: none;
  stroke: #49a968;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 6 2;
  opacity: 0.9;
}

.fruit {
  position: absolute;
  width: 56px;
  height: 60px;
  pointer-events: none;
}

.fruit .leaf {
  position: absolute;
  left: 50%;
  top: -6px;
  width: 16px;
  height: 10px;
  background: #5cc77a;
  border-radius: 100% 0 100% 0;
  transform: translateX(-10px) rotate(-28deg);
  box-shadow: inset -1px -1px 0 rgba(0, 0, 0, 0.12);
}

.fruit .body {
  position: absolute;
  left: 50%;
  top: 2px;
  font-size: 48px;
  line-height: 1;
  transform: translateX(-50%);
  filter: drop-shadow(0 3px 3px rgba(0, 0, 0, 0.18));
}

.fruit-a { left: 12%; bottom: 12%; }
.fruit-b { left: 48%; bottom: 42%; }
.fruit-c { right: 13%; top: 8%; }

.node-label {
  position: absolute;
  color: #1f5d35;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.65);
  text-align: center;
}

.node-label .title {
  font-size: 26px;
  font-weight: 900;
  line-height: 1.2;
}

.node-label .sub {
  margin-top: 4px;
  font-size: 20px;
  font-weight: 800;
  color: #f49b00;
}

.label-a { left: calc(12% - 67px); bottom: calc(12% - 62px); width: 190px; text-align: center; }
.label-b { left: calc(48% - 58px); bottom: calc(42% - 66px); width: 172px; }
.label-c { right: calc(13% - 24px); top: calc(8% + 58px); width: 110px; }

.pulse {
  animation: pulseGlow 1.5s infinite;
}

@keyframes pulseGlow {
  0% { transform: translateX(-50%) scale(1); }
  50% { transform: translateX(-50%) scale(1.08); }
  100% { transform: translateX(-50%) scale(1); }
}

.stage5-check-card {
  position: absolute;
  right: 3.5%;
  top: calc(8% + 110px);
  width: min(34vw, 420px);
  background: #fffdf7;
  border: 2px solid #f3dfb5;
  border-radius: 20px;
  padding: 12px;
  box-shadow: 0 8px 18px rgba(188, 140, 50, 0.12);
}

.card-title {
  font-size: 16px;
  font-weight: 800;
  color: #6f5518;
  margin-bottom: 8px;
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
  margin-top: 8px;
  text-align: right;
  font-size: 16px;
  font-weight: 800;
  color: #f49b00;
}

.action-footer {
  padding: 6px 0 0;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: center;
}

.prev-btn {
  min-width: 130px;
}

:deep(.van-button--large) {
  height: 54px;
  font-size: 22px;
  font-weight: 800;
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

.cert-actions {
  width: min(92vw, 860px);
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1200px) {
  .node-label .title { font-size: 20px; }
  .node-label .sub { font-size: 16px; }
  .check-label { font-size: 15px; }
  .stage5-check-card { width: min(39vw, 380px); }
  .fruit .body { font-size: 40px; }
  .cert-title { font-size: 44px; }
  .cert-body { font-size: 22px; }
  .badge-title { font-size: 32px; }
}

@media (max-width: 900px) {
  .main-board { padding: 10px; }
  .stars-summary { font-size: 16px; left: 10px; top: 10px; padding: 6px 10px; }
  .stars-summary span { font-size: 19px; }
  .stage5-check-card {
    right: 4%;
    width: 92%;
    top: auto;
    bottom: 5%;
  }
  .node-label .title { font-size: 17px; }
  .node-label .sub { font-size: 14px; }
  .fruit .body { font-size: 34px; }
  .label-a { left: calc(12% - 47px); bottom: calc(12% - 52px); width: 150px; text-align: center; }
  .fruit-b { left: 49%; bottom: 43%; }
  .label-b { left: calc(49% - 46px); bottom: calc(43% - 56px); width: 148px; }
  .label-c { right: calc(13% - 18px); top: calc(8% + 52px); width: 90px; }
  .action-footer {
    grid-template-columns: 1fr;
  }
  .prev-btn {
    width: 100%;
  }
}
</style>
