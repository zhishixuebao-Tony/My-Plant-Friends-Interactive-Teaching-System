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
          <div class="encouragement-content">
            <p>为了了解植物朋友，你用了这些方法：</p>
            <div class="selected-methods">
              <span v-for="(method, index) in displayMethods" :key="index" class="method-item">
                {{ method }}
              </span>
            </div>
            <p class="stars-reward">获得1缕阳光 <img src="/sun.svg" alt="" class="sun-inline-icon" /></p>
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
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.sensoryTransition));

const displayMethods = computed(() => {
  const selections = userStore.sensorySelections || [];
  const methodIcons = {
    '看一看': '👀',
    '闻一闻': '👃', 
    '摸一摸': '✋',
    '听一听': '👂',
    '尝一尝': '👅',
    '其他': '✨'
  };
  
  return selections.map(method => {
    const icon = methodIcons[method] || '✨';
    return `${icon} ${method}`;
  });
});

const goNext = () => {
  if (!canGoNext.value) return;
  userStore.setStage('3'); // 跳转到 ViewRecordCards
};
</script>

<style scoped>
.welcome-page {
  height: 100dvh;
  overflow: hidden;
  background-image:
    linear-gradient(180deg, rgba(0, 0, 0, 0.34) 0%, rgba(0, 0, 0, 0.34) 100%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(240, 251, 240, 0.2) 100%),
    url('/transition-pages/sensory-transition/background.jpg');
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
  background-image: url('/transition-pages/sensory-transition/book-page.png');
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

.school-badge {
  position: absolute;
  top: 0;
  right: 0;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  border: 2px solid #eef2f8;
  background-image: url('/welcome/school-badge.png');
  background-position: center 60%;
  background-size: 78% auto;
  background-repeat: no-repeat;
  background-color: #ffffff;
  box-shadow:
    0 8px 18px rgba(12, 52, 28, 0.2),
    0 0 0 2px rgba(255, 255, 255, 0.95);
}

.encouragement-box {
  margin-top: 13vh;
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

.selected-methods {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin: 20px 0;
}

.method-item {
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

.star-count {
  font-size: clamp(28px, 2.5vw, 42px);
  color: #ff6600;
  font-weight: 900;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.sun-inline-icon {
  width: 1em;
  height: 1em;
  vertical-align: -0.08em;
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
