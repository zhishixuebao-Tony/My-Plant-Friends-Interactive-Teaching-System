<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">记录我的植物朋友</div>
      <van-button
        type="primary"
        round
        size="small"
        :loading="isSubmitting"
        :disabled="nextDisabled"
        @click="onNextClick"
        class="top-nav-action"
      >
        {{ isPhotoPage ? '下一步' : '提交' }}
      </van-button>
    </div>

    <div v-if="isPhotoPage" class="stage-body photo-page">
      <section class="photo-panel" :class="{ 'photo-panel--judge': hasJudgePreRecord }">
        <div class="photo-hint">再次走近自己的植物朋友，也许你会有新的发现，把你的新发现补充在记录卡上。</div>
        <div
          v-if="prePlantPhotos.length"
          class="photo-grid"
          :class="[
            `photo-grid-count-${Math.min(prePlantPhotos.length, 3)}`,
            { 'photo-grid--judge': hasJudgePreRecord },
          ]"
        >
          <button
            v-for="(img, idx) in prePlantPhotos"
            :key="idx"
            type="button"
            class="photo-btn"
            @click="openPlantPreview(idx)"
          >
            <van-image :src="img" fit="cover" radius="4" class="plant-img" />
          </button>
        </div>
        <div v-if="isJudgeLogin && preRecordCardUrls.length" class="pre-record-section">
          <div class="pre-record-title">记录卡</div>
          <div class="pre-record-grid">
            <button
              v-for="(url, idx) in preRecordCardUrls"
              :key="`pre-record-${idx}`"
              type="button"
              class="pre-record-btn"
              @click="openRecordCardPreview(idx)"
            >
              <van-image :src="url" fit="cover" radius="4" class="pre-record-img" />
            </button>
          </div>
        </div>
        <div v-if="!prePlantPhotos.length" class="empty-tip">暂无植物照片</div>
      </section>
    </div>

    <div v-else class="stage-body check-page">
      <section class="evaluate-panel">
        <header class="level-1-title">再次观察，我有没有新的发现呢？</header>
        <div class="eval-box">
          <div class="discovery-group">
          <div class="level-2-title">我已经有了新的发现：</div>

          <button
            type="button"
            class="check-row level-3-row"
            :class="{ active: hasUnseen, disabled: groupDisabled }"
            :disabled="groupDisabled"
            @click="toggleUnseen"
          >
            <span>（1）有以前没观察到的</span>
            <span class="square" :class="{ checked: hasUnseen }">{{ hasUnseen ? '✓' : '' }}</span>
          </button>

          <button
            type="button"
            class="check-row level-3-row"
            :class="{ active: hasFeeling, disabled: groupDisabled }"
            :disabled="groupDisabled"
            @click="toggleFeeling"
          >
            <span>（2）观察后，有了点儿感受（身体感觉/心里想法）</span>
            <span class="square" :class="{ checked: hasFeeling }">{{ hasFeeling ? '✓' : '' }}</span>
          </button>

          </div>

          <div class="no-discovery-group">
          <button
            type="button"
            class="check-row level-2-row no-discovery-row"
            :class="{ active: noNewFinding, disabled: noNewDisabled }"
            :disabled="noNewDisabled"
            @click="toggleNoNew"
          >
            <span>我暂时没有新的发现。</span>
            <span class="square" :class="{ checked: noNewFinding }">{{ noNewFinding ? '✓' : '' }}</span>
          </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import axios from 'axios';
import { showImagePreview, showToast } from 'vant';
import { useUserStore } from '../store/user';
import { toDisplayImageUrl } from '../utils/imageProxy';
import { NEXT_BUTTON_KEYS } from '../constants/nextButtonControls';

const userStore = useUserStore();

const isSubmitting = ref(false);
const currentPage = ref(1);
const prePlantPhotos = ref([]);
const preRecordCardUrls = ref([]);

const noNewFinding = ref(false);
const hasUnseen = ref(false);
const hasFeeling = ref(false);
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.recordCard));

const isJudgeLogin = computed(() => {
  const sid = Number(String(userStore.studentId || '').trim());
  return Number.isFinite(sid) && sid >= 51 && sid <= 70;
});

const isPhotoPage = computed(() => currentPage.value === 1);
const groupDisabled = computed(() => noNewFinding.value);
const noNewDisabled = computed(() => hasUnseen.value || hasFeeling.value);
const hasJudgePreRecord = computed(() => isJudgeLogin.value && preRecordCardUrls.value.length > 0);

const selectedChecks = computed(() => {
  const checks = [];
  if (noNewFinding.value) {
    checks.push('我暂时没有新的发现。');
    return checks;
  }
  if (hasUnseen.value) checks.push('我已经有了新的发现：（1）有以前没观察到的');
  if (hasFeeling.value) checks.push('我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉/心里想法）');
  return checks;
});

const nextDisabled = computed(() => {
  if (isPhotoPage.value) return !canGoNext.value;
  return selectedChecks.value.length === 0;
});

const toggleNoNew = () => {
  if (noNewDisabled.value) return;
  noNewFinding.value = !noNewFinding.value;
  if (noNewFinding.value) {
    hasUnseen.value = false;
    hasFeeling.value = false;
  }
};

const toggleUnseen = () => {
  if (groupDisabled.value) return;
  hasUnseen.value = !hasUnseen.value;
};

const toggleFeeling = () => {
  if (groupDisabled.value) return;
  hasFeeling.value = !hasFeeling.value;
};

onMounted(async () => {
  try {
    const response = await axios.get(`/api/student/info/${userStore.studentId}`);
    const data = response.data || {};
    const photosFromApi = [data.pre_plant_1, data.pre_plant_2, data.pre_plant_3]
      .map((v) => toDisplayImageUrl(v))
      .filter(Boolean);
    const recordCardUrl = toDisplayImageUrl(data.pre_record_card || '');
    preRecordCardUrls.value = recordCardUrl ? [recordCardUrl] : [];
    prePlantPhotos.value = photosFromApi.length ? photosFromApi : userStore.prePlantPhotos || [];
  } catch (error) {
    prePlantPhotos.value = userStore.prePlantPhotos || [];
    preRecordCardUrls.value = userStore.preRecordCard ? [userStore.preRecordCard] : [];
    console.warn('获取课前植物照片失败:', error);
  }
});

const openPlantPreview = (startIndex) => {
  if (!prePlantPhotos.value.length) return;
  showImagePreview({
    images: prePlantPhotos.value,
    startPosition: startIndex,
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body',
  });
};


const openRecordCardPreview = (startIndex) => {
  if (!preRecordCardUrls.value.length) return;
  showImagePreview({
    images: preRecordCardUrls.value,
    startPosition: startIndex,
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body',
  });
};
const onFinalSubmit = async () => {
  if (selectedChecks.value.length === 0) {
    showToast('请至少勾选一项评价');
    return;
  }

  const stage3Stars = Number(selectedChecks.value.length > 0);

  isSubmitting.value = true;
  try {
    await axios.post('/api/student/stage2/record-card', {
      student_id: userStore.studentId,
      checks: selectedChecks.value,
    });
    if (typeof userStore.setStage3Stars === 'function') {
      userStore.setStage3Stars(stage3Stars);
    }
    userStore.setDimensionSelections(selectedChecks.value);
    userStore.setStage('record-card-transition');
    showToast({ message: '提交成功', type: 'success' });
  } catch (error) {
    console.error(error);
    showToast('提交失败，请重试');
  } finally {
    isSubmitting.value = false;
  }
};

const onNextClick = async () => {
  if (isPhotoPage.value) {
    if (!canGoNext.value) return;
    currentPage.value = 2;
    return;
  }
  await onFinalSubmit();
};
</script>

<style scoped>
/* =========== 全局背景 =========== */
.stage-container {
  height: 100%;
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
  padding: 16px;
  box-sizing: border-box;
  overflow: hidden;
}

/* ========================================= */
/*               第一页：照片回顾页              */
/* ========================================= */
.photo-page {
  display: flex;
}

/* 手账内页面板 */
.photo-panel {
  width: min(100%, 1200px);
  margin: 0 auto;
  background: #FDFBF2;
  border-radius: 16px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border: 2px dashed #D4CBB3;
  box-shadow: 4px 12px 30px rgba(90, 76, 67, 0.12);
  min-height: 0;
  position: relative;
}

/* 面板顶部的小胶带 */
.photo-panel::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%) rotate(1deg);
  width: 120px;
  height: 24px;
  background-color: rgba(135, 179, 146, 0.6);
  box-shadow: 1px 2px 4px rgba(0,0,0,0.05);
  border-radius: 2px;
  z-index: 10;
}

.photo-title {
  font-size: 26px;
  font-weight: 900;
  color: #5A4C43;
  text-align: center;
  position: relative;
  display: inline-block;
  align-self: center;
}
.photo-title::after {
  content: '';
  position: absolute;
  bottom: 0px;
  left: -5%;
  width: 110%;
  height: 10px;
  background: rgba(246, 218, 115, 0.6); /* 马克笔高亮 */
  z-index: -1;
  border-radius: 4px;
}

/* 提示框：黄色便利贴风格 */
.photo-hint {
  font-size: 20px;
  line-height: 1.5;
  font-weight: 800;
  color: #6B5D53;
  text-align: center;
  background: #FFF9D2; /* 便利贴黄 */
  border: 1px solid #EBE1A7;
  border-radius: 4px 12px 12px 4px; /* 模拟便利贴翘角 */
  padding: 12px 16px;
  box-shadow: 2px 4px 10px rgba(200, 180, 100, 0.2);
  transform: rotate(-0.5deg);
  margin-bottom: 10px;
}

/* 照片网格 */
.photo-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  align-content: center;
  padding: 10px; /* 给相片阴影留空间 */
}

.photo-panel--judge {
  gap: 10px;
  padding-top: 18px;
}

.photo-panel--judge .photo-hint {
  margin-top: 8px;
}

.photo-grid--judge {
  flex: 1;
  align-content: center;
  gap: 12px;
  margin-top: 0;
  padding-top: 0;
}

.photo-panel--judge .photo-btn {
  min-height: 170px;
  padding: 10px 10px 14px;
}

.photo-panel--judge .plant-img {
  min-height: 160px;
  height: 186px;
}

/* 单个照片：拍立得相纸风格 */
.photo-grid.photo-grid-count-1 {
  grid-template-columns: minmax(0, 420px) !important;
  justify-content: center;
}

.photo-grid.photo-grid-count-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  justify-content: center;
  width: min(100%, 860px);
  margin: 0 auto;
}

.photo-btn {
  border: 0;
  padding: 10px 10px 24px 10px; /* 底部留白更多，像相纸 */
  background: #FFF;
  border: 1px solid #E3DBC7;
  box-shadow: 2px 6px 14px rgba(90, 76, 67, 0.1);
  border-radius: 4px;
  cursor: pointer;
  min-height: 130px;
  transition: all 0.2s ease;
}
.plant-img {
  width: 100%;
  height: 100%;
  min-height: 130px;
  background: #F6F4E8;
  border-radius: 2px !important; /* 覆盖原来的大圆角 */
}

.empty-tip {
  color: #A3968C;
  border: 2px dashed #D4CBB3;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  font-size: 20px;
  font-weight: 700;
  background: #FAF7EA;
}

.pre-record-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 6px;
}

.photo-panel--judge .pre-record-section {
  margin-top: -18px;
  flex: 1;
  min-height: 0;
}

.photo-panel--judge .pre-record-title {
  text-align: center;
  transform: translateY(-12px);
}

.pre-record-title {
  font-size: 18px;
  font-weight: 800;
  color: #5A4C43;
  text-align: left;
}

.pre-record-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}

.photo-panel--judge .pre-record-grid {
  grid-template-columns: minmax(0, 420px);
  justify-content: center;
  align-content: center;
  flex: 1;
  margin-top: -18px;
}

.pre-record-btn {
  border: 0;
  padding: 6px;
  background: #FFF;
  border: 1px solid #E3DBC7;
  border-radius: 4px;
  cursor: pointer;
}

.pre-record-img {
  width: 100%;
  height: 110px;
  background: #F6F4E8;
}

.photo-panel--judge .pre-record-img {
  height: clamp(170px, 32vh, 300px);
}

/* ========================================= */
/*               第二页：选项打卡页              */
/* ========================================= */
.check-page {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 打卡面板（复用手账风格） */
.evaluate-panel {
  width: min(980px, 100%);
  background: #FDFBF2;
  border-radius: 16px;
  padding: 30px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border: 2px dashed #D4CBB3;
  box-shadow: 4px 12px 30px rgba(90, 76, 67, 0.12);
  min-height: 0;
  position: relative;
}
.evaluate-panel::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%) rotate(-1deg);
  width: 120px;
  height: 24px;
  background-color: rgba(220, 203, 163, 0.7); /* 土黄胶带 */
  box-shadow: 1px 2px 4px rgba(0,0,0,0.05);
  border-radius: 2px;
  z-index: 10;
}

.level-1-title {
  font-size: 32px;
  line-height: 1.3;
  font-weight: 900;
  color: #5A4C43;
  text-align: center;
}

/* 内部选项框：像在纸上画的虚线区域 */
.eval-box {
  border: 2px solid #E3DBC7;
  background: #FAF7EA;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.level-2-title {
  font-size: 24px;
  line-height: 1.25;
  font-weight: 800;
  color: #5C8D6D; /* 绿色副标题 */
  margin-bottom: 6px;
}

/* 选项条：厚纸板按钮 */
.check-row {
  width: 100%;
  border: 2px solid #E3DBC7;
  border-radius: 12px;
  background: #FDFBF2;
  padding: 12px 16px;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  color: #5A4C43;
  box-shadow: 0 5px 0 #E3DBC7; /* 坚实的底部阴影 */
  transition: all 0.15s ease;
}

.level-2-row {
  font-size: 24px;
  font-weight: 800;
  min-height: 70px;
  margin-top: 10px;
}

.level-3-row {
  margin-left: 14px;
  width: calc(100% - 14px);
  font-size: 20px;
  font-weight: 700;
  min-height: 64px;
}

/* 选中状态：被按下，变绿 */
.check-row.active {
  background: #5C8D6D;
  border-color: #3A664A;
  color: #FDFBF2;
  box-shadow: 0 0 0 #3A664A; /* 阴影消失 */
  transform: translateY(5px); /* 位置下压 */
}

/* 禁用状态（互斥时）：变成灰暗的旧纸板 */
.check-row.disabled {
  background: #EBE5D3;
  border-color: #D4CBB3;
  color: #A3968C;
  box-shadow: 0 5px 0 #D4CBB3;
  cursor: not-allowed;
}

/* 右侧勾选框：圆形手绘盖章区 */
.square {
  width: 42px;
  height: 42px;
  border: 2px dashed #D4CBB3;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #5C8D6D;
  font-size: 24px;
  font-weight: 900;
  flex-shrink: 0;
  background: transparent;
  transition: all 0.2s;
}

/* 选中后的打钩状态 */
.check-row.active .square.checked {
  border: none;
  background: #FDFBF2;
  color: #5C8D6D;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  transform: scale(1.1) rotate(-5deg);
}

/* 分组卡片样式 */
.discovery-group,
.no-discovery-group {
  border: 2px solid #E3DBC7;
  border-radius: 12px;
  background: #FDFBF2;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 取消提示卡片外观，保持正文样式 */
.photo-hint {
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  transform: none !important;
  padding: 0 !important;
}

/* “暂无新发现”行文案强调 */
.no-discovery-row {
  color: #5C8D6D;
  font-size: 24px;
  font-weight: 800;
  margin-top: 0;
}


/* =========== 按钮尺寸适配 =========== */
:deep(.top-nav-action.van-button) {
  height: 40px;
  padding-inline: 18px;
  font-size: 16px;
  font-weight: 800;
}

/* =========== 响应式适配 =========== */
@media (max-width: 900px) {
  .top-nav {
    grid-template-columns: 112px 1fr 112px;
    padding-inline: 10px;
  }

  :deep(.top-nav-action.van-button) {
    font-size: 14px;
    padding-inline: 14px;
  }

  .photo-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .pre-record-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .photo-panel--judge .pre-record-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .photo-panel--judge .pre-record-img {
    height: clamp(150px, 28vh, 220px);
  }

  .photo-btn, .plant-img {
    min-height: 100px;
  }

  .evaluate-panel {
    padding: 20px 16px;
  }

  .level-1-title {
    font-size: 26px;
  }

  .level-2-title, .level-2-row {
    font-size: 20px;
  }

  .level-3-row {
    font-size: 17px;
    width: 100%;
    margin-left: 0;
  }
  
  .check-row.active {
    transform: translateY(4px);
  }
  .check-row, .check-row.disabled {
    box-shadow: 0 4px 0 #E3DBC7;
  }
}

/* 固定勾选态高度，避免选中时容器抖动 */
.check-row.active {
  transform: none !important;
  box-shadow: 0 5px 0 #3A664A !important;
}

@media (max-width: 900px) {
  .check-row.active {
    transform: none !important;
    box-shadow: 0 4px 0 #3A664A !important;
  }
}
</style>

