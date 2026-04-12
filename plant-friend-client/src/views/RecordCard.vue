<template>
  <div class="stage-container">
    <div class="top-nav">
      <span class="top-nav-spacer" aria-hidden="true"></span>
      <div class="top-nav-title">我的新发现</div>
      <van-button
        type="primary"
        round
        size="small"
        :loading="isSubmitting"
        :disabled="selectedChecks.length === 0 || !canGoNext"
        @click="onFinalSubmit"
        class="top-nav-action"
      >
        提交并下一步
      </van-button>
    </div>

    <div class="stage-body">
      <section class="observe-panel">

        <div class="left-split">
          <div class="left-card">
            <div class="sub-title">课前记录卡</div>
            <van-image
              v-if="preRecordCardUrl"
              :src="preRecordCardUrl"
              fit="contain"
              radius="8"
              class="record-img"
              @click="openPreRecordCardPreview"
            />
            <div v-else class="empty-tip">暂无课前记录卡</div>
          </div>

          <div class="left-card">
            <div class="sub-title">植物朋友的照片</div>
            <div v-if="prePlantPhotos.length" class="photo-grid">
              <button
                v-for="(img, idx) in prePlantPhotos"
                :key="idx"
                type="button"
                class="photo-btn"
                @click="openPlantPreview(idx)"
              >
                <van-image :src="img" fit="cover" radius="8" class="plant-img" />
              </button>
            </div>
            <div v-else class="empty-tip">暂无课前植物照片</div>
          </div>
        </div>
      </section>
      <section class="evaluate-panel">
        <header class="panel-header">再次观察，我有没有新的发现呢？</header>

        <div class="eval-box">
          <button
            type="button"
            class="check-row"
            :class="{ active: noNewFinding, disabled: noNewDisabled }"
            :disabled="noNewDisabled"
            @click="toggleNoNew"
          >
            <span>我暂时没有新的发现。</span>
            <span class="square" :class="{ checked: noNewFinding }">{{ noNewFinding ? '✓' : '' }}</span>
          </button>

          <div class="group-title">我已经有了新的发现：</div>

          <button
            type="button"
            class="check-row sub"
            :class="{ active: hasUnseen, disabled: groupDisabled }"
            :disabled="groupDisabled"
            @click="toggleUnseen"
          >
            <span>（1）有以前没观察到的</span>
            <span class="square" :class="{ checked: hasUnseen }">{{ hasUnseen ? '✓' : '' }}</span>
          </button>

          <button
            type="button"
            class="check-row sub"
            :class="{ active: hasFeeling, disabled: groupDisabled }"
            :disabled="groupDisabled"
            @click="toggleFeeling"
          >
            <span>（2）观察后，有了点儿感受（身体感觉 心里想法）</span>
            <span class="square" :class="{ checked: hasFeeling }">{{ hasFeeling ? '✓' : '' }}</span>
          </button>
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
const preRecordCardUrl = ref('');
const prePlantPhotos = ref([]);

const noNewFinding = ref(false);
const hasUnseen = ref(false);
const hasFeeling = ref(false);
const canGoNext = computed(() => userStore.isNextButtonEnabled(NEXT_BUTTON_KEYS.recordCard));

const groupDisabled = computed(() => noNewFinding.value);
const noNewDisabled = computed(() => hasUnseen.value || hasFeeling.value);

const selectedChecks = computed(() => {
  const checks = [];
  if (noNewFinding.value) {
    checks.push('我暂时没有新的发现');
    return checks;
  }
  if (hasUnseen.value) checks.push('我已经有了新的发现：（1）有以前没观察到的');
  if (hasFeeling.value) checks.push('我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）');
  return checks;
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
    const response = await axios.get(`/api/teacher/dashboard/student-detail/${userStore.studentId}`);
    const data = response.data || {};
    preRecordCardUrl.value = toDisplayImageUrl(data.pre_record_card || '');

    const photosFromApi = [data.pre_plant_1, data.pre_plant_2, data.pre_plant_3]
      .map((v) => toDisplayImageUrl(v))
      .filter(Boolean);
    prePlantPhotos.value = photosFromApi.length ? photosFromApi : userStore.prePlantPhotos || [];
  } catch (error) {
    prePlantPhotos.value = userStore.prePlantPhotos || [];
    console.warn('获取课前素材失败:', error);
  }
});

const openPreRecordCardPreview = () => {
  if (!preRecordCardUrl.value) return;
  showImagePreview({
    images: [preRecordCardUrl.value],
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body',
  });
};

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

const onFinalSubmit = async () => {
  if (!canGoNext.value) return;
  if (selectedChecks.value.length === 0) {
    showToast('请至少勾选一项评价');
    return;
  }

  const stage3Stars = Number(hasUnseen.value || hasFeeling.value);

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
  flex-shrink: 0;
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
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 12px;
  padding: 12px;
  box-sizing: border-box;
  overflow: hidden;
}

.observe-panel,
.evaluate-panel {
  background: #fff;
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid #e8edf6;
  overflow: hidden;
}

.panel-header {
  font-size: 16px;
  font-weight: 700;
  color: #243447;
}

.left-split {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-rows: 1fr 1fr;
  gap: 10px;
}

.left-card {
  border: 1px solid #e8edf6;
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
}

.sub-title {
  font-size: 14px;
  font-weight: 700;
  color: #243447;
}

.record-img {
  width: 100%;
  height: 100%;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  flex: 1;
  min-height: 0;
}

.photo-btn {
  border: 0;
  padding: 0;
  background: transparent;
  cursor: pointer;
}

.plant-img {
  width: 100%;
  height: 100%;
  min-height: 88px;
}

.empty-tip {
  color: #8a9ab0;
  border: 1px dashed #d3ddec;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.evaluate-panel {
  min-height: 0;
}

.eval-box {
  border: 1px solid #e1e8f5;
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-height: 0;
}

.group-title {
  font-size: 15px;
  font-weight: 700;
  color: #2e4058;
  margin-top: 6px;
}

.check-row {
  width: 100%;
  border: 1px solid #d7e0ef;
  border-radius: 10px;
  background: #fff;
  padding: 10px 12px;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  min-height: 72px;
  font-size: 18px;
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
  width: 44px;
  height: 44px;
  border: 2px solid #c2cede;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #377dff;
  font-size: 22px;
  font-weight: 700;
  flex-shrink: 0;
  background: #f8fbff;
}

.square.checked {
  border-color: #377dff;
  background: #eaf1ff;
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

  .stage-body {
    grid-template-columns: 1fr;
    overflow: auto;
  }
}
</style>
