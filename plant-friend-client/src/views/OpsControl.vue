<template>
  <div class="ops-page">
    <div class="top-nav">程序员控制台 - 下一步按钮开关</div>

    <div v-if="!verified" class="login-card">
      <van-field
        v-model="password"
        type="password"
        label="控制密码"
        placeholder="请输入程序员控制密码"
      />
      <van-button type="primary" block round :loading="verifying" @click="verifyPassword">
        进入控制台
      </van-button>
    </div>

    <div v-else class="panel">
      <div class="hint">切换后会实时同步到所有学生端</div>
      <div class="list">
        <div v-for="item in controlItems" :key="item.key" class="row">
          <span class="label">{{ item.label }}</span>
          <van-switch
            :model-value="Boolean(controls[item.key])"
            :loading="loadingMap[item.key]"
            @update:model-value="(v) => updateOne(item.key, v)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import axios from 'axios';
import { showToast } from 'vant';
import { DEFAULT_NEXT_BUTTON_CONTROL_STATE, NEXT_BUTTON_LABELS } from '../constants/nextButtonControls';

const password = ref('');
const verifying = ref(false);
const verified = ref(false);
const controls = ref({ ...DEFAULT_NEXT_BUTTON_CONTROL_STATE });
const loadingMap = ref({});

const controlItems = computed(() =>
  Object.entries(NEXT_BUTTON_LABELS).map(([key, label]) => ({ key, label }))
);

const verifyPassword = async () => {
  const pwd = String(password.value || '').trim();
  if (!pwd) {
    showToast('请输入控制密码');
    return;
  }

  verifying.value = true;
  try {
    const res = await axios.post('/api/ops/verify-password', { password: pwd });
    if (!res.data?.success) {
      showToast(res.data?.message || '密码错误');
      return;
    }
    verified.value = true;
    await fetchControls();
    showToast({ message: '已进入控制台', type: 'success' });
  } catch (_) {
    showToast('验证失败');
  } finally {
    verifying.value = false;
    password.value = '';
  }
};

const fetchControls = async () => {
  try {
    const res = await axios.get('/api/ops/next-buttons');
    controls.value = {
      ...DEFAULT_NEXT_BUTTON_CONTROL_STATE,
      ...(res.data?.controls || {}),
    };
  } catch (_) {
    showToast('获取按钮状态失败');
  }
};

const updateOne = async (key, enabled) => {
  loadingMap.value = { ...loadingMap.value, [key]: true };
  try {
    controls.value = { ...controls.value, [key]: Boolean(enabled) };
    const res = await axios.post(`/api/ops/next-buttons/${key}`, { enabled: Boolean(enabled) });
    controls.value = {
      ...DEFAULT_NEXT_BUTTON_CONTROL_STATE,
      ...(res.data?.controls || controls.value),
    };
  } catch (_) {
    controls.value = { ...controls.value, [key]: !Boolean(enabled) };
    showToast('更新失败');
  } finally {
    loadingMap.value = { ...loadingMap.value, [key]: false };
  }
};
</script>

<style scoped>
.ops-page {
  min-height: 100dvh;
  background: #f7f8fa;
}

.top-nav {
  min-height: 56px;
  padding: max(0px, env(safe-area-inset-top)) 16px 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border-bottom: 1px solid #dfe6f3;
  font-size: 17px;
  font-weight: 700;
  color: #1f2d3d;
}

.login-card,
.panel {
  width: min(92vw, 760px);
  margin: 24px auto;
  padding: 18px;
  border-radius: 14px;
  background: #ffffff;
  border: 1px solid #e8edf6;
}

.hint {
  margin-bottom: 12px;
  color: #5b6b7f;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e8edf6;
  border-radius: 10px;
}

.label {
  font-size: 14px;
  font-weight: 600;
  color: #243447;
}
</style>
