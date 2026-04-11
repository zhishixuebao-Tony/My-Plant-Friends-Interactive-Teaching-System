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
        <div class="school-badge"></div>
        <div class="school-line">统编教材小学语文三年级下册第一单元习作</div>

        <div class="course-name-image"></div>
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
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.welcome));

const goNext = () => {
  if (!canGoNext.value) return;
  userStore.setStage('1');
};
</script>

<style scoped>
.welcome-page {
  height: 100dvh;
  overflow: hidden;
  background-image:
    linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(240, 251, 240, 0.2) 100%),
    url('/welcome/background.jpg');
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
  background-image: url('/welcome/book-page.png');
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  background-color: transparent;
}

.right-area {
  position: absolute;
  right: 5vw;
  top: 5.5vh;
  width: min(58vw, 980px);
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

.school-line {
  margin-top: 108px;
  font-size: clamp(20px, 2.2vw, 34px);
  color: #ffffff;
  font-weight: 700;
  text-align: center;
  text-shadow: 0 1px 0 rgba(108, 106, 106, 0.68);
}

.course-name-image {
  margin-top: 6.6vh;
  width: min(100%, 1140px);
  aspect-ratio: 41 / 11;
  border-radius: 0;
  background-image: url('/welcome/course-title.png');
  background-position: center;
  background-size: 100% auto;
  background-repeat: no-repeat;
  background-color: transparent;
  box-shadow: none;
}

.grass-btn {
  position: absolute;
  right: 4.4vw;
  bottom: 4.4vh;
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
    width: 58vw;
  }

  .school-badge {
    width: 72px;
    height: 72px;
    font-size: 17px;
  }

  .school-line {
    margin-top: 88px;
  }

  .course-name-image {
    margin-top: 2.4vh;
  }

  .grass-btn {
    right: 3vw;
    bottom: 3vh;
    padding: 12px 18px 10px;
    font-size: 18px;
  }
}
</style>
