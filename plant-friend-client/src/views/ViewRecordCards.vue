<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">记录我的植物朋友</div>
      <van-button type="primary" round size="small" :disabled="!canGoNext" @click="goNext" class="top-nav-action">下一步</van-button>
    </div>

    <div class="stage-body">
      <div class="stage-subtitle">看一看，向伙伴“学一学”</div>
      <div class="cards-grid">
        <div class="card-slot" v-for="item in cardSlots" :key="item.id">
          <div class="slot-title">{{ item.title }}</div>
          <van-image
            :src="item.url"
            fit="contain"
            radius="10"
            class="slot-image"
            @click="previewCard(item.url)"
          />
          <div class="slot-tip">点击图片查看</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { showImagePreview } from 'vant';
import { computed } from 'vue';
import { useUserStore } from '../store/user';
import { NEXT_BUTTON_KEYS } from '../constants/nextButtonControls';

const userStore = useUserStore();
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.viewRecordCards));

const cardSlots = [
  {
    id: 1,
    title: '记录卡 1',
    url: '/ViewRecordCards/RecordCard1.png',
  },
  {
    id: 2,
    title: '记录卡 2',
    url: '/ViewRecordCards/RecordCard2.png',
  },
  {
    id: 3,
    title: '记录卡 3',
    url: '/ViewRecordCards/RecordCard3.png',
  },
  {
    id: 4,
    title: '记录卡 4',
    url: '/ViewRecordCards/RecordCard4.png',
  },
];

const goNext = () => {
  if (!canGoNext.value) return;
  userStore.setStage('2');
};

const previewCard = (url) => {
  if (!url) return;
  showImagePreview({
    images: [url],
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body',
  });
};
</script>

<style scoped>
/* =========== 全局背景手账化 =========== */
.stage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #F4F1E1; /* 复古牛皮纸色底 */
}

/* =========== 顶部导航栏（融入纸张风格，与上页完全一致） =========== */
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

:deep(.van-button--primary:disabled) {
  background-color: #E3DBC7 !important;
  border-color: #E3DBC7 !important;
  color: #A3968C !important;
  box-shadow: none !important;
  opacity: 1 !important;
  transform: none !important;
}

/* =========== 内容区域 =========== */
.stage-body {
  flex: 1;
  padding: 16px 16px 14px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  overflow: hidden; /* 固定一屏，不允许滚动 */
}

.stage-subtitle {
  width: min(100%, 980px);
  margin: 0 auto;
  text-align: center;
  font-size: clamp(18px, 2.2vw, 22px);
  font-weight: 800;
  color: #5C8D6D;
  letter-spacing: 1px;
}

/* =========== 卡片网格 =========== */
.cards-grid {
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: clamp(10px, 1.8vw, 18px);
  align-content: center;
  width: min(100%, 980px);
  margin: 0 auto;
}

/* =========== 拍立得/相片质感卡片 =========== */
.card-slot {
  background: #FDFBF2; /* 相纸白 */
  border: 1px solid #E3DBC7; /* 微微泛黄的边缘 */
  border-radius: 4px; /* 拍立得的硬朗小圆角 */
  padding: 12px 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: clamp(170px, 23vh, 230px);
  box-shadow: 2px 6px 18px rgba(90, 76, 67, 0.12); /* 纸张漂浮阴影 */
  position: relative; /* 为顶部纸胶带定位 */
  transition: all 0.25s ease-out;
}

@media (orientation: landscape) {
  .stage-body {
    padding: 18px 18px 14px;
    gap: 14px;
  }

  .cards-grid {
    width: min(100%, 1180px);
    gap: clamp(12px, 1.8vw, 20px);
  }

  .card-slot {
    height: clamp(225px, 32vh, 310px);
    padding: 14px 12px;
  }

  .slot-tip {
    padding: 6px 0;
  }
}

/* 纯CSS装饰：顶部的半透明和纸胶带 */
.card-slot::before {
  content: '';
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%) rotate(-3deg);
  width: 80px;
  height: 26px;
  background-color: rgba(220, 203, 163, 0.7); /* 默认土黄色胶带 */
  box-shadow: 1px 2px 4px rgba(0,0,0,0.06);
  border-radius: 1px;
  z-index: 10;
  backdrop-filter: blur(1px);
}

/* 用 nth-child 给三个卡片换不同的胶带颜色和倾斜角度，营造手工随机感 */
.card-slot:nth-child(2)::before {
  background-color: rgba(135, 179, 146, 0.7); /* 绿色胶带 */
  transform: translateX(-50%) rotate(2deg);
}
.card-slot:nth-child(3)::before {
  background-color: rgba(200, 150, 130, 0.65); /* 陶土色胶带 */
  transform: translateX(-50%) rotate(-1deg);
}

/* =========== 卡片内部文字与图片 =========== */
.slot-title {
  font-size: clamp(14px, 1.9vw, 18px);
  font-weight: 800;
  color: #5A4C43;
  text-align: center;
  margin-bottom: 0;
}

.slot-image {
  flex: 1 1 auto;
  width: 100%;
  background: #F6F4E8; /* 图片没有加载出来时的底色 */
  border: 1px dashed #D4CBB3; /* 图片外层的虚线框，更像黏贴上去的 */
  border-radius: 4px !important; /* 覆盖 vant 的大圆角，更贴合相纸 */
  overflow: hidden;
  cursor: zoom-in; /* 鼠标变成放大镜，暗示可点击 */
}

/* 图片悬停放大暗示 */
:deep(.van-image__img) {
  transition: transform 0.3s ease;
}
.slot-tip {
  font-size: clamp(12px, 1.5vw, 14px);
  font-weight: 800;
  color: #5C8D6D; /* 护眼深绿 */
  text-align: center;
  background: rgba(92, 141, 109, 0.1); /* 浅绿底色强调 */
  padding: 4px 0;
  border-radius: 6px;
  margin-top: auto; /* 始终贴近底部 */
}

/* =========== 按钮尺寸适配 =========== */
:deep(.top-nav-action.van-button) {
  height: 40px;
  padding-inline: 18px;
  font-size: 16px;
  font-weight: 800;
}

/* =========== 响应式适配（小屏幕/竖屏平板） =========== */
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
    padding: 12px 10px 10px;
  }

  .cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  .card-slot {
    height: clamp(145px, 21vh, 185px);
    padding: 10px 8px;
  }

  .card-slot::before {
    top: -8px;
    width: 56px;
    height: 18px;
  }
}

@media (max-width: 900px) and (orientation: landscape) {
  .stage-body {
    padding: 14px 12px 12px;
    gap: 10px;
  }

  .cards-grid {
    width: min(100%, 1020px);
    gap: 10px;
  }

  .card-slot {
    height: clamp(205px, 35vh, 270px);
    padding: 12px 10px;
  }
}
</style>
