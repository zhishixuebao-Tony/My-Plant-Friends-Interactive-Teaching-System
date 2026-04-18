<template>
  <div class="welcome-page">
    <div class="scene-overlay">
      <div class="book-area">
        <div class="book-card">
          <div class="book-title"></div>
          <div class="book-cover"></div>
        </div>
      </div>

      <div class="right-area">
        <div class="encouragement-box">
          <div class="encouragement-title">{{ pageTitle }}</div>
          <div class="encouragement-content">
            <p>{{ encouragementText }}</p>
            <div v-if="displaySelections.length > 0" class="selected-discoveries">
              <span v-for="(selection, index) in displaySelections" :key="index" class="discovery-item">
                {{ selection }}
              </span>
            </div>
            <p v-if="starsMessageFinal" class="stars-info">{{ starsMessageFinal }}</p>
            <p v-if="starsEarned > 0" class="stars-reward">{{ rewardText }} <img src="/sun.svg" alt="" class="sun-inline-icon" /></p>
            <p v-else class="no-stars-message">你的认真记录同样值得表扬！</p>
          </div>
        </div>
      </div>

      <button type="button" class="grass-btn" :disabled="!canGoNext" @click="goNext">
        <span class="grass-icon"></span>
        <span>下一步</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useUserStore } from '../store/user';
import { NEXT_BUTTON_KEYS } from '../constants/nextButtonControls';

const userStore = useUserStore();
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.recordCardTransition));

const displaySelections = computed(() => {
  const selections = userStore.dimensionSelections || [];
  return selections.map((selectionRaw) => {
    const selection = String(selectionRaw || '');
    if (selection.includes('暂时没有')) {
      return '暂时没有新的发现';
    }
    if (
      selection.includes('(1)') ||
      selection.includes('（1）') ||
      selection.includes('有以前没观察到')
    ) {
      return '有以前没观察到的';
    }
    if (
      selection.includes('(2)') ||
      selection.includes('（2）') ||
      selection.includes('观察后') ||
      selection.includes('感受')
    ) {
      return '观察后，有了点儿感受';
    }
    return selection;
  });
});

const starsEarned = computed(() => {
  const selections = userStore.dimensionSelections || [];
  return selections.length > 0 ? 1 : 0;
});

const hasNoNewDiscovery = computed(() =>
  displaySelections.value.some((s) => s.includes('暂时没有新的发现'))
);

const pageTitle = computed(() => {
  return '';
});

const encouragementText = computed(() => {
  if (hasNoNewDiscovery.value) {
    return '你认真地完成了记录卡，并诚实选择了：';
  }
  return '再次和植物朋友见面，你有了这些发现：';
});

const rewardText = computed(() =>
  hasNoNewDiscovery.value ? '同样值得表扬！获得一缕阳光' : '获得1缕阳光'
);

const starsMessage = computed(() => {
  if (starsEarned.value === 0) {
    return '我们到下一个环节继续探索吧。';
  }
  return '';
});

const starsEarnedFinal = computed(() => starsEarned.value);
const starsMessageFinal = computed(() => starsMessage.value);

const goNext = () => {
  if (!canGoNext.value) return;
  userStore.setStage('4');
};
</script>

<style scoped>
.welcome-page {
  height: 100dvh;
  overflow: hidden;
  background-image:
    linear-gradient(180deg, rgba(0, 0, 0, 0.34) 0%, rgba(0, 0, 0, 0.34) 100%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(240, 251, 240, 0.2) 100%),
    url('/transition-pages/recordcard-transition/background.jpg');
  background-color: #e8f3e6;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.scene-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  padding: 3.2vw;
  box-sizing: border-box;
}

.book-area {
  position: absolute;
  left: 7vw;
  top: 50%;
  transform: translateY(-50%);
  width: min(34vw, 500px);
}

.book-card {
  border-radius: 28px;
  background: transparent;
  border: 0;
  box-shadow: none;
  padding: 0;
}

.book-title {
  font-size: 22px;
  font-weight: 800;
  color: #2c6f48;
  margin-bottom: 12px;
}

.book-cover {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 20px;
  border: 0;
  background-image: url('/transition-pages/recordcard-transition/book-page.png');
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  background-color: transparent;
}

.right-area {
  position: absolute;
  right: 5vw;
  top: 5.5vh;
  width: min(50vw, 850px);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.encouragement-box {
  margin-top: 15vh;
  width: min(100%, 1000px);
  padding: 35px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.encouragement-title {
  font-size: clamp(32px, 3vw, 48px);
  font-weight: 800;
  color: #2d8a4e;
  margin-bottom: 24px;
}

.encouragement-content {
  font-size: clamp(18px, 1.8vw, 28px);
  color: #333;
  line-height: 1.6;
}

.selected-discoveries {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin: 20px 0;
}

.discovery-item {
  background: linear-gradient(135deg, #73d46d, #2d8a4e);
  color: white;
  padding: 10px 20px;
  border-radius: 50px;
  font-size: clamp(16px, 1.5vw, 24px);
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(45, 138, 78, 0.3);
}

.stars-info {
  font-size: clamp(20px, 2vw, 32px);
  color: #2c6f48;
  font-weight: 700;
  margin: 24px 0 12px;
}

.stars-reward {
  font-size: clamp(24px, 2.2vw, 36px);
  color: #ff9900;
  font-weight: 800;
  margin: 16px 0;
}

.no-stars-message {
  font-size: clamp(20px, 2vw, 32px);
  color: #666;
  font-weight: 700;
  margin: 24px 0;
  font-style: italic;
}

.sun-inline-icon {
  width: 1em;
  height: 1em;
  vertical-align: -0.08em;
}

.star-count {
  font-size: clamp(28px, 2.5vw, 42px);
  color: #ff6600;
  font-weight: 900;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.grass-btn {
  position: absolute;
  right: 4.4vw;
  bottom: 6vh;
  border: 0;
  background: linear-gradient(180deg, #73d46d 0%, #2d8a4e 100%);
  color: #fff;
  font-size: clamp(20px, 2vw, 30px);
  font-weight: 800;
  border-radius: 999px 999px 20px 20px;
  padding: 16px 28px 14px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 0 12px 22px rgba(28, 86, 49, 0.25);
}

.grass-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.grass-btn:active {
  transform: translateY(1px) scale(0.99);
}

.grass-icon {
  width: 22px;
  height: 22px;
  position: relative;
}

.grass-icon::before,
.grass-icon::after {
  content: '';
  position: absolute;
  bottom: 0;
  width: 7px;
  height: 18px;
  background: #dff8dd;
  border-radius: 10px 10px 2px 2px;
}

.grass-icon::before {
  left: 2px;
  transform: rotate(-18deg);
}

.grass-icon::after {
  right: 2px;
  transform: rotate(18deg);
}

@media (max-width: 900px) {
  .book-area {
    left: 3vw;
    width: min(40vw, 340px);
  }

  .right-area {
    right: 3vw;
    width: 50vw;
  }

  .school-badge {
    width: 72px;
    height: 72px;
    font-size: 17px;
  }

  .school-line {
    margin-top: 70px;
  }

  .encouragement-box {
    margin-top: 2vh;
    padding: 20px;
  }

  .grass-btn {
    right: 3vw;
    bottom: 4.5vh;
    padding: 12px 18px 10px;
    font-size: 18px;
  }
}
</style>

