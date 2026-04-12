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
            <div class="group-title">1.我试着写清楚了我的植物朋友：</div>
            
            <button
              type="button"
              class="check-row sub"
              :class="{ active: hasMultiaspect, disabled: false }"
              @click="toggleMultiaspect"
            >
              <span>（1）我是从多方面写的</span>
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
              <span>（2）我是按照一定顺序写的</span>
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
              <span>2.我还愿意把习作分享给别人</span>
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
            <p>在《我的植物朋友》探索中，你共获得了 <span class="strong-num">{{ totalStars }}</span> 颗星！</p>
            <p>根据你的表现，特授予你以下称号：</p>
            <p class="badge-title-row">
              <span class="badge-star" aria-hidden="true">★</span>
              <span class="badge-title">{{ awardTitle }}</span>
              <span class="badge-star" aria-hidden="true">★</span>
            </p>
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
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 12% 18%, rgba(195, 231, 195, 0.45) 0%, rgba(195, 231, 195, 0) 36%),
    radial-gradient(circle at 88% 24%, rgba(255, 236, 189, 0.42) 0%, rgba(255, 236, 189, 0) 34%),
    radial-gradient(circle at 48% 76%, rgba(217, 239, 212, 0.42) 0%, rgba(217, 239, 212, 0) 32%),
    linear-gradient(180deg, #f5faef 0%, #eff7ea 52%, #f6f1dc 100%);
}

.certificate-wrap::before {
  content: "";
  position: absolute;
  inset: -6%;
  pointer-events: none;
  opacity: 0.24;
  background-image:
    radial-gradient(ellipse at 20% 25%, rgba(103, 156, 98, 0.28) 0 18%, transparent 20%),
    radial-gradient(ellipse at 73% 54%, rgba(129, 179, 121, 0.24) 0 16%, transparent 18%),
    radial-gradient(ellipse at 44% 74%, rgba(153, 199, 143, 0.2) 0 14%, transparent 16%);
  filter: blur(1px);
}

.certificate {
  width: min(92vw, 860px);
  position: relative;
  z-index: 2;
  background:
    linear-gradient(135deg, rgba(255, 252, 241, 0.82) 0%, rgba(255, 247, 225, 0.78) 100%);
  border-radius: 24px;
  padding: 16px;
  border: 1px solid rgba(230, 203, 126, 0.75);
  box-shadow:
    0 18px 36px rgba(72, 100, 52, 0.2),
    0 6px 12px rgba(72, 100, 52, 0.12);
  backdrop-filter: blur(4px);
}

.cert-inner {
  position: relative;
  border: 4px double #d7b351;
  border-radius: 18px;
  background:
    repeating-linear-gradient(
      -12deg,
      rgba(255, 251, 238, 0.95) 0px,
      rgba(255, 251, 238, 0.95) 6px,
      rgba(255, 247, 229, 0.95) 6px,
      rgba(255, 247, 229, 0.95) 12px
    );
  padding: 30px 26px 24px;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.85);
}

.cert-title {
  text-align: center;
  font-size: 58px;
  font-weight: 900;
  letter-spacing: 11px;
  margin-bottom: 20px;
  background: linear-gradient(180deg, #1f8a49 0%, #1f6e41 45%, #155535 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow:
    0 1px 0 #f6fff6,
    0 3px 8px rgba(45, 108, 58, 0.25);
  -webkit-text-stroke: 1px rgba(19, 74, 40, 0.26);
}

.cert-body {
  font-size: 27px;
  color: #4d3d19;
  line-height: 1.82;
}

.strong-name,
.strong-num {
  font-weight: 900;
  color: #1d6f3f;
  padding: 0 4px;
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(233, 252, 231, 0.95) 0%, rgba(219, 246, 214, 0.95) 100%);
}

.badge-title-row {
  margin-top: 12px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.badge-title {
  font-size: 40px;
  font-weight: 900;
  color: #1f7541;
  letter-spacing: 1px;
  text-shadow:
    0 1px 0 #f6fff6,
    0 4px 10px rgba(43, 105, 55, 0.24);
}

.badge-star {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #fff7cb;
  background: radial-gradient(circle at 34% 32%, #ffe98a 0%, #ffcf4e 50%, #e3a825 100%);
  box-shadow:
    0 0 12px rgba(255, 207, 78, 0.72),
    0 4px 10px rgba(212, 144, 29, 0.35);
  border: 1px solid rgba(255, 245, 198, 0.7);
}

.cert-footer {
  margin-top: 18px;
  display: flex;
  justify-content: space-between;
  font-size: 18px;
  color: #7d6632;
}

.cert-deco {
  position: absolute;
  z-index: 1;
  pointer-events: none;
}

.leaf {
  width: 34px;
  height: 22px;
  background: linear-gradient(140deg, #7ec783 0%, #4ea86f 100%);
  border-radius: 22px 22px 22px 4px;
  box-shadow: 0 6px 10px rgba(55, 122, 68, 0.18);
}

.leaf-a { top: 76px; left: 78px; transform: rotate(-24deg); }
.leaf-b { right: 70px; top: 96px; transform: rotate(18deg) scale(1.15); }
.leaf-c { right: 120px; bottom: 86px; transform: rotate(-34deg); }

.flower {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: radial-gradient(circle, #fff5bd 0%, #ffd97c 48%, #f6ba59 100%);
  box-shadow: 0 0 0 6px rgba(255, 244, 204, 0.55);
}

.flower-a { left: 124px; bottom: 110px; }
.flower-b { right: 152px; top: 150px; }

.ladybug {
  width: 16px;
  height: 16px;
  right: 92px;
  bottom: 132px;
  border-radius: 50%;
  background: radial-gradient(circle at 38% 30%, #ff6e61 0%, #dc3f34 70%);
  box-shadow: 0 3px 8px rgba(128, 30, 30, 0.28);
}

.ladybug::before {
  content: "";
  position: absolute;
  left: 7px;
  top: 1px;
  width: 2px;
  height: 14px;
  background: #3a2d2d;
}

.ladybug::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 36% 42%, #222 0 1.4px, transparent 1.6px),
    radial-gradient(circle at 65% 30%, #222 0 1.3px, transparent 1.5px),
    radial-gradient(circle at 62% 64%, #222 0 1.4px, transparent 1.6px);
}

.vine-corner {
  position: absolute;
  width: 44px;
  height: 44px;
  pointer-events: none;
  border: 2px solid rgba(82, 138, 82, 0.55);
}

.vine-tl { top: 10px; left: 10px; border-right: 0; border-bottom: 0; border-radius: 16px 0 0 0; }
.vine-tr { top: 10px; right: 10px; border-left: 0; border-bottom: 0; border-radius: 0 16px 0 0; }
.vine-bl { bottom: 10px; left: 10px; border-right: 0; border-top: 0; border-radius: 0 0 0 16px; }
.vine-br { bottom: 10px; right: 10px; border-left: 0; border-top: 0; border-radius: 0 0 16px 0; }

.vine-corner::after {
  content: "";
  position: absolute;
  width: 10px;
  height: 6px;
  background: linear-gradient(140deg, #7fbf75 0%, #59a562 100%);
  border-radius: 8px 8px 8px 0;
}

@media (max-width: 1200px) {
  .tree-label .title { font-size: 20px; }
  .tree-label .sub { font-size: 16px; }
  .check-label { font-size: 15px; }
  .stage5-check-card { width: min(29vw, 300px); top: 43%; right: 5.5%; }
  .tree-a { left: 11%; width: 172px; }
  .tree-b { left: 39%; width: 172px; }
  .tree-c { right: 20%; width: 110px; top: 19%; }
  .cert-title { font-size: 46px; letter-spacing: 8px; }
  .cert-body { font-size: 22px; }
  .badge-title { font-size: 33px; }
  .badge-star { width: 36px; height: 36px; font-size: 20px; }
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

  .certificate-wrap { padding: 16px; }
  .certificate { width: min(96vw, 860px); padding: 12px; }
  .cert-inner { padding: 22px 18px 18px; }
  .cert-title { font-size: 36px; letter-spacing: 6px; }
  .cert-body { font-size: 18px; }
  .badge-title { font-size: 28px; }
  .badge-star { width: 30px; height: 30px; font-size: 16px; }
  .cert-footer { font-size: 14px; }
  .leaf, .flower, .ladybug { transform: scale(0.85); }
}
</style>
