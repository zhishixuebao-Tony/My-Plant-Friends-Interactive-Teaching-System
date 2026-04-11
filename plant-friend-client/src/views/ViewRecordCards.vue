<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">看一看，向同学“学一学”</div>
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
.stage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f7fb;
}

.top-nav {
  min-height: 56px;
  padding: max(0px, env(safe-area-inset-top)) 16px 0 16px;
  display: grid;
  grid-template-columns: 132px 1fr 132px;
  align-items: center;
  gap: 8px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
  border-bottom: 1px solid #dfe6f3;
  box-shadow: 0 3px 10px rgba(30, 60, 120, 0.08);
}

.top-nav-title {
  font-size: 17px;
  font-weight: 700;
  color: #1f2d3d;
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

.stage-body {
  flex: 1;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.cards-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-template-rows: minmax(0, 1fr);
  gap: 12px;
  min-height: 0;
}

.card-slot {
  background: #ffffff;
  border: 1px solid #e8edf6;
  border-radius: 14px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
}

.slot-title {
  font-size: 15px;
  font-weight: 700;
  color: #243447;
}

.slot-image {
  flex: 1;
  width: 100%;
  min-height: 0;
  background: #f8fbff;
  border: 1px solid #dbe4f3;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
}

:deep(.top-nav-action.van-button) {
  height: 34px;
  padding-inline: 10px;
  font-size: 13px;
  font-weight: 700;
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

  .cards-grid {
    grid-template-columns: 1fr;
    overflow: auto;
  }
}
</style>
