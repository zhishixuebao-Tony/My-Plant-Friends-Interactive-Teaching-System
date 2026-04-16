<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">看一看，向伙伴“学一学”</div>
      <van-button type="primary" round size="small" :disabled="!canGoNext" @click="goNext" class="top-nav-action">下一步</van-button>
    </div>

    <div class="stage-body">
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
  padding: 30px 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto; /* 允许内容滚动 */
}

/* =========== 卡片网格 =========== */
.cards-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-template-rows: auto;
  gap: 24px; /* 拉开间距，更像散落的照片 */
  align-content: center;
  width: min(100%, 1200px);
  margin: 0 auto;
}

/* =========== 拍立得/相片质感卡片 =========== */
.card-slot {
  background: #FDFBF2; /* 相纸白 */
  border: 1px solid #E3DBC7; /* 微微泛黄的边缘 */
  border-radius: 4px; /* 拍立得的硬朗小圆角 */
  padding: 16px 14px 20px; /* 底部留白多一点，写tip */
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: clamp(260px, 50vh, 380px);
  box-shadow: 2px 6px 18px rgba(90, 76, 67, 0.12); /* 纸张漂浮阴影 */
  position: relative; /* 为顶部纸胶带定位 */
  transition: all 0.25s ease-out;
}

/* 互动反馈：悬停/点击时卡片微微翘起 */
.card-slot:hover, .card-slot:active {
  transform: translateY(-6px) rotate(1deg);
  box-shadow: 4px 12px 24px rgba(90, 76, 67, 0.18);
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
  font-size: 18px;
  font-weight: 800;
  color: #5A4C43;
  text-align: center;
  margin-bottom: 2px;
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
.card-slot:hover :deep(.van-image__img) {
  transform: scale(1.02);
}

.slot-tip {
  font-size: 15px;
  font-weight: 800;
  color: #5C8D6D; /* 护眼深绿 */
  text-align: center;
  background: rgba(92, 141, 109, 0.1); /* 浅绿底色强调 */
  padding: 6px 0;
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
    padding: 20px 14px;
  }

  .cards-grid {
    grid-template-columns: 1fr;
    gap: 28px; /* 单列时拉开更大间距，防止胶带遮挡 */
    padding-top: 10px; /* 给最上面的胶带留出空间 */
  }

  .card-slot {
    height: 280px; /* 竖屏时固定一个合适的高度 */
  }
}
</style>