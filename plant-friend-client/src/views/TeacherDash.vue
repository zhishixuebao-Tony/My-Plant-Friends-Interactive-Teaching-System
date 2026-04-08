<template>
  <!-- eslint-disable vue/no-v-model-argument -->
  <div class="teacher-container">
    <van-nav-bar title="教师指挥中心" />

    <div class="main-content">
      <div class="section-title">全班学生在线状态 (<span class="highlight">{{ stats.online }}</span>/{{ stats.total }})</div>

      <div class="matrix-grid">
        <div
          v-for="student in studentList"
          :key="student.student_id"
          class="student-card"
          :class="student.is_logged_in ? 's-online' : 's-offline'"
          @click="openDetail(student.student_id)"
        >
          <div class="id-tag">{{ student.student_id }}</div>
          <div class="name-text">{{ student.student_name || '未登录' }}</div>
          <div v-if="shouldShowStars(student)" class="star-row">
            {{ formatStars(getFinalStars(student)) }}
          </div>
          <div v-if="student.final_img" class="medal-icon">🏅</div>
        </div>
      </div>

      <div class="section-title tables-title">各环节数据实时统计</div>
      <div class="tables-container">
        <div class="data-table-box">
          <div class="table-head">观察方法统计</div>
          <table class="custom-table">
            <thead>
              <tr><th>观察项</th><th>勾选数</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in sensoryRows" :key="row.key">
                <td>
                  <button class="link-cell" @click="openSelectionPopup('sensory', row)">{{ row.label }}</button>
                </td>
                <td>{{ getSensoryCount(row.key) }} 人</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="data-table-box">
          <div class="table-head">新发现统计</div>
          <table class="custom-table">
            <thead>
              <tr><th>评价项</th><th>勾选数</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in dimensionRows" :key="row.key">
                <template v-if="row.type === 'group'">
                  <td colspan="2" class="dimension-group-row">{{ row.label }}</td>
                </template>
                <template v-else>
                  <td>
                    <button class="link-cell" @click="openSelectionPopup('dimension', row)">{{ row.label }}</button>
                  </td>
                  <td>{{ getDimensionCount(row.key) }} 人</td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="data-table-box">
          <div class="table-head">资源点击统计</div>
          <table class="custom-table">
            <thead>
              <tr><th>资源名称</th><th>点击数</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in resourceRows" :key="row.key">
                <td>
                  <button class="link-cell" @click="openSelectionPopup('resource', row)">{{ row.label }}</button>
                </td>
                <td>{{ getResourceCount(row.key) }} 次</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="data-table-box">
          <div class="table-head">写作目标达成统计</div>
          <table class="custom-table">
            <thead>
              <tr><th>评价项</th><th>勾选数</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in writingRows" :key="row.key">
                <template v-if="row.type === 'group'">
                  <td colspan="2" class="dimension-group-row">{{ row.label }}</td>
                </template>
                <template v-else>
                  <td>
                    <button class="link-cell" @click="openSelectionPopup('writing', row)">{{ row.label }}</button>
                  </td>
                  <td>{{ getWritingCount(row.key) }} 人</td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <van-popup v-model:show="showDrawer" position="right" :style="{ width: '550px', height: '100%' }">
      <div v-if="detailLoading" class="loading-box">
        <van-loading size="24px" vertical>正在读取该生详细档案...</van-loading>
      </div>

      <div v-else-if="activeData" class="detail-panel">
        <van-nav-bar
          :title="`${activeData.student_id}号 ${activeData.student_name} 的档案`"
          left-text="关闭"
          @click-left="showDrawer = false"
          fixed
          placeholder
          border
        />

        <div class="scroll-body">
          <div class="module-title">课前准备：植物照片</div>
          <div class="pre-media-box">
            <div class="plant-photos" v-if="activeData.pre_plant_1 || activeData.pre_plant_2 || activeData.pre_plant_3">
              <van-image v-if="activeData.pre_plant_1" :src="activeData.pre_plant_1" fit="cover" class="p-img" @click="preview(activeData.pre_plant_1)" />
              <van-image v-if="activeData.pre_plant_2" :src="activeData.pre_plant_2" fit="cover" class="p-img" @click="preview(activeData.pre_plant_2)" />
              <van-image v-if="activeData.pre_plant_3" :src="activeData.pre_plant_3" fit="cover" class="p-img" @click="preview(activeData.pre_plant_3)" />
            </div>
            <div v-else class="empty-text">该生暂无课前植物照片</div>
          </div>

          <div class="module-title module-gap">写作流程档案</div>
          <div class="img-group">
            <div class="img-item">
              <div class="item-tag">课前原始记录卡</div>
              <van-image
                v-if="activeData.pre_record_card"
                :src="activeData.pre_record_card"
                fit="contain"
                @click="preview(activeData.pre_record_card)"
              />
              <div v-else class="empty-text">未获取</div>
            </div>
          </div>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showSelectionPopup" position="center" round :style="{ width: '480px', maxWidth: '92vw' }">
      <div class="selection-popup">
        <div class="selection-title">{{ selectionTitle }}</div>
        <div class="selection-subtitle">选择该词条的学生（{{ selectedStudents.length }} 人）</div>
        <div v-if="selectedStudents.length" class="selection-grid">
          <div
            v-for="item in selectedStudents"
            :key="item.id"
            class="student-card"
            :class="item.isLoggedIn ? 's-online' : 's-offline'"
          >
            <div class="id-tag">{{ item.id }}</div>
            <div class="name-text">{{ item.name }}</div>
          </div>
        </div>
        <div v-else class="empty-text">暂无学生选择该词条</div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import axios from 'axios';
import { showImagePreview, showToast } from 'vant';

const studentList = ref([]);
const stats = ref({ online: 0, total: 50, table1: {}, table2: {}, table3: {}, table4: {}, table5: 0, resource_completed: 0 });

const showDrawer = ref(false);
const activeData = ref(null);
const detailLoading = ref(false);
const showSelectionPopup = ref(false);
const selectionTitle = ref('');
const selectedStudents = ref([]);

const sensoryRows = [
  { key: '看一看', label: '👀 看一看' },
  { key: '闻一闻', label: '👃 闻一闻' },
  { key: '摸一摸', label: '✋ 摸一摸' },
  { key: '听一听', label: '👂 听一听' },
  { key: '尝一尝', label: '👅 尝一尝' },
  { key: '其他', label: '✨ 其他' },
];

const dimensionRows = [
  { key: '我暂时没有新的发现', label: '1.我暂时没有新的发现' },
  { key: 'dimension-group-found', label: '2.我已经有了新的发现：', type: 'group' },
  { key: '我已经有了新的发现：（1）有以前没观察到的', label: '（1）有以前没观察到的' },
  { key: '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）', label: '（2）观察后，有了点儿感受（身体感觉 心里想法）' },
];

const resourceRows = [
  { key: '融入感受', label: '感受小锦囊' },
  { key: '有序介绍', label: '顺序百宝箱' },
  { key: '优美词句', label: '词语百花园' },
];

const writingRows = [
  { key: 'writing-group-clarity', label: '1. 我试着写清楚了：', type: 'group' },
  { key: '（1）我能从多方面介绍', label: '（1）我能从多方面介绍' },
  { key: '（2）我能有顺序介绍', label: '（2）我能有顺序介绍' },
  { key: '2.我分享了我的习作', label: '2.我分享了我的习作' },
];

const getSensoryCount = (name) => {
  const aliasMap = {
    '看一看': ['看一看'],
    '闻一闻': ['闻一闻'],
    '摸一摸': ['摸一摸'],
    '听一听': ['听一听'],
    '尝一尝': ['尝一尝'],
    '其他': ['其他'],
  };
  const keys = aliasMap[name] || [name];
  return keys.reduce((sum, key) => sum + (stats.value.table1?.[key] || 0), 0);
};

const getDimensionCount = (name) => {
  const aliasMap = {
    '我暂时没有新的发现': ['我暂时没有新的发现', '我暂时没有新的发现。'],
    '我已经有了新的发现：（1）有以前没观察到的': ['我已经有了新的发现：（1）有以前没观察到的', '评价一：能真实记录植物特点', '评价一'],
    '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': [
      '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    ],
  };
  const keys = aliasMap[name] || [name];
  return keys.reduce((sum, key) => sum + (stats.value.table2?.[key] || 0), 0);
};

const getResourceCount = (resourceName) => {
  const rows = Object.entries(stats.value.table3 || {});
  return rows.reduce((sum, [key, count]) => {
    if (String(key).startsWith(resourceName)) return sum + Number(count || 0);
    return sum;
  }, 0);
};

const getWritingCount = (name) => {
  const aliasMap = {
    '（1）我能从多方面介绍': ['（1）我能从多方面介绍', '（1）我能从多方面介绍。（√）'],
    '（2）我能有顺序介绍': ['（2）我能有顺序介绍', '（2）我能有顺序介绍。（√）'],
    '2.我分享了我的习作': ['2.我分享了我的习作', '我分享了我的习作'],
  };
  const keys = aliasMap[name] || [name];
  return keys.reduce((sum, key) => sum + (stats.value.table4?.[key] || 0), 0);
};

const getFinalStars = (student) => {
  if (!student) return 0;
  const candidates = [
    student.total_stars,
    student.totalStars,
    student.final_stars,
    student.finalStars,
    student.stage_total_stars,
  ];
  for (const value of candidates) {
    const n = Number(value);
    if (Number.isFinite(n) && n >= 0) return Math.max(0, Math.floor(n));
  }
  return 0;
};

const shouldShowStars = (student) => {
  if (!student) return false;
  const claimed = Boolean(student.has_claimed_certificate);
  return claimed && getFinalStars(student) > 0;
};

const formatStars = (count) => {
  const n = Math.max(0, Number(count) || 0);
  return n > 0 ? `⭐`.repeat(n) : '';
};

const getSensoryAliases = (name) => {
  const aliasMap = {
    '看一看': ['看一看', '看了看'],
    '闻一闻': ['闻一闻', '闻了闻'],
    '摸一摸': ['摸一摸', '摸了摸'],
    '听一听': ['听一听'],
    '尝一尝': ['尝一尝', '尝了尝'],
    '其他': ['其他'],
  };
  return aliasMap[name] || [name];
};

const getDimensionAliases = (name) => {
  const aliasMap = {
    '我暂时没有新的发现': ['我暂时没有新的发现', '我暂时没有新的发现。'],
    '我已经有了新的发现：（1）有以前没观察到的': ['我已经有了新的发现：（1）有以前没观察到的', '评价一：能真实记录植物特点', '评价一'],
    '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': [
      '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    ],
  };
  return aliasMap[name] || [name];
};

const getWritingAliases = (name) => {
  const aliasMap = {
    '（1）我能从多方面介绍': ['（1）我能从多方面介绍', '（1）我能从多方面介绍。（√）'],
    '（2）我能有顺序介绍': ['（2）我能有顺序介绍', '（2）我能有顺序介绍。（√）'],
    '2.我分享了我的习作': ['2.我分享了我的习作', '我分享了我的习作'],
  };
  return aliasMap[name] || [name];
};

const openSelectionPopup = (type, row) => {
  const students = (studentList.value || []).filter((student) => {
    if (type === 'sensory') {
      const values = student.sensory_evaluations || [];
      const aliases = getSensoryAliases(row.key);
      return values.some((item) => aliases.includes(String(item).trim()));
    }
    if (type === 'dimension') {
      const values = student.dimension_evaluations || [];
      const aliases = getDimensionAliases(row.key);
      return values.some((item) => aliases.includes(String(item).trim()));
    }
    if (type === 'resource') {
      const statsMap = student.resource_click_stats || {};
      return Object.entries(statsMap).some(([k, v]) => String(k).startsWith(row.key) && Number(v || 0) > 0);
    }
    if (type === 'writing') {
      const values = student.stage5_checks || [];
      const aliases = getWritingAliases(row.key);
      return values.some((item) => aliases.includes(String(item).trim()));
    }
    return false;
  });

  selectedStudents.value = students.map((s) => ({
    id: String(s.student_id || '').padStart(2, '0'),
    name: s.student_name || '未命名',
    isLoggedIn: !!s.is_logged_in,
  }));
  selectionTitle.value = row.label;
  showSelectionPopup.value = true;
};

const fetchDashboardData = async () => {
  try {
    const res = await axios.get('/api/teacher/dashboard/statistics');
    studentList.value = res.data.students_list || [];
    stats.value = {
      online: res.data.logged_in_count || 0,
      total: res.data.total_students || 0,
      table1: res.data.table1_sensory || {},
      table2: res.data.table2_dimension || {},
      table3: res.data.table3_resource || {},
      table4: res.data.table4_writing || {},  // 改为写作统计对象
      table5: res.data.table5_ai_count || 0,  // AI计数移到table5
      resource_completed: res.data.resource_completed_count || 0,
    };
  } catch (err) {
    console.error('刷新大屏失败:', err);
  }
};

const getWsUrl = () => {
  const base = axios.defaults.baseURL || window.location.origin;
  if (base.startsWith('https')) return base.replace(/^https/, 'wss') + '/ws/stats';
  if (base.startsWith('http')) return base.replace(/^http/, 'ws') + '/ws/stats';
  return 'ws://127.0.0.1:8000/ws/stats';
};

const wsURL = getWsUrl();
let socket = null;
let reconnectTimer = null;
let pollTimer = null;

const initWebSocket = () => {
  socket = new WebSocket(wsURL);

  socket.onopen = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.action === 'REFRESH_DASHBOARD') fetchDashboardData();
  };

  socket.onclose = () => {
    reconnectTimer = setTimeout(initWebSocket, 3000);
  };

  socket.onerror = () => socket.close();
};

const openDetail = async (studentId) => {
  showDrawer.value = true;
  detailLoading.value = true;
  activeData.value = null;
  try {
    const res = await axios.get(`/api/teacher/dashboard/student-detail/${studentId}`);
    if (res.data?.error) {
      showToast('未找到该学生数据');
      showDrawer.value = false;
      return;
    }
    activeData.value = res.data;
  } catch (err) {
    showToast('获取档案失败');
    showDrawer.value = false;
  } finally {
    detailLoading.value = false;
  }
};

const preview = (url) => {
  if (!url) return;
  showImagePreview({ images: [url], closeable: true, closeOnClickOverlay: true, teleport: 'body' });
};


onMounted(() => {
  fetchDashboardData();
  initWebSocket();
  pollTimer = setInterval(fetchDashboardData, 60000);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (socket) {
    socket.onclose = null;
    socket.close();
  }
});
</script>

<style scoped>
.teacher-container { 
  height: 100%; 
  background-color: #f2f3f5; 
  display: flex; 
  flex-direction: column; 
  overflow-y: auto; 
  overflow-x: hidden; 
  /* 默认底部安全区域 */
  padding-bottom: 100px;
}

/* 平板横屏优化布局 */
@media (min-width: 768px) and (max-width: 1199px) {
  .teacher-container {
    /* 底部安全区域增加到150px，确保不被系统导航栏遮挡 */
    padding-bottom: env(safe-area-inset-bottom, 150px);
  }
  
  /* 针对横屏优化：增加整体内边距，提升视觉舒适度 */
  .main-content {
    padding: 36px; /* 保持整体内边距 */
  }
  
  /* 横屏下表格区域增加更多上边距 */
  .tables-title {
    margin-top: 48px;
  }
  
  /* 横屏下优化学生矩阵网格：10列可能太密，调整为7列，提高可读性 */
  .matrix-grid {
    grid-template-columns: repeat(7, 1fr);
    gap: 16px;
  }
  
  /* 横屏下学生卡片增大，提高可读性 */
  .student-card {
    height: 92px;
  }
  
  /* 横屏下学生卡片内文字优化 */
  .name-text {
    font-size: 16px;
  }
  
  /* 表格压缩：与默认样式保持一致 */
  .data-table-box {
    padding: 16px 12px; /* 与默认保持一致 */
  }
  
  .table-head {
    font-size: 16px; /* 与默认保持一致 */
    margin-bottom: 14px; /* 与默认保持一致 */
  }
  
  /* 横屏下表格内容与默认保持一致 */
  .custom-table th,
  .custom-table td {
    padding: 10px 8px; /* 与默认保持一致 */
    font-size: 14px; /* 与默认保持一致 */
  }
  
  .custom-table th:nth-child(1),
  .custom-table td:nth-child(1) {
    padding-right: 16px; /* 与默认保持一致 */
    width: 70%; /* 与默认保持一致 */
  }
  
  .custom-table th:nth-child(2),
  .custom-table td:nth-child(2) {
    padding-left: 16px; /* 与默认保持一致 */
    font-size: 14px; /* 与默认保持一致 */
    width: 30%; /* 与默认保持一致 */
  }
  
  /* 横屏下整体字体适当调整 */
  .section-title {
    font-size: 22px;
  }
  
  .highlight {
    font-size: 28px;
  }
}

.main-content { padding: 24px; }
.section-title { font-size: 20px; font-weight: 700; color: #333; margin-bottom: 20px; border-left: 5px solid #07c160; padding-left: 12px; }
.tables-title { margin-top: 36px; }
.highlight { color: #07c160; font-size: 26px; }
.matrix-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 12px; }
.student-card { height: 82px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; cursor: pointer; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); transition: transform 0.15s; }
.student-card:active { transform: scale(0.98); }
.s-online { background-color: #eafaf1; border: 1px solid #8ce6b0; color: #1e8e3e; }
.s-offline { background-color: #fff; border: 1px solid #dcdee0; color: #969799; }
.id-tag { position: absolute; top: 4px; left: 6px; font-size: 12px; font-weight: 700; background: rgba(0, 0, 0, 0.05); padding: 2px 6px; border-radius: 4px; }
.name-text { font-size: 15px; font-weight: 700; margin-top: 6px; }
.star-row { margin-top: 4px; font-size: 14px; line-height: 1; letter-spacing: 1px; color: #f59e0b; font-weight: 700; }
.medal-icon { position: absolute; top: -8px; right: -6px; font-size: 18px; }
.tables-container { 
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 横屏2x2田字排列 */
  gap: 24px;
}

.data-table-box { 
  background: #fff; 
  border-radius: 12px; 
  padding: 16px 12px; /* 压缩左右内边距 */
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04); 
  border-top: 4px solid #07c160; 
  transition: transform 0.2s ease;
  min-width: 0; 
  overflow: hidden; 
}

.data-table-box:hover {
  transform: translateY(-2px); 
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08); 
}





.custom-table {
  width: 100%;
  table-layout: fixed; 
}

.custom-table th:nth-child(1),
.custom-table td:nth-child(1) {
  width: 70%;
}

.custom-table th:nth-child(2),
.custom-table td:nth-child(2) {
  width: 30%;
}

.custom-table th,
.custom-table td {
  word-break: break-word; 
  overflow-wrap: break-word;
}


.table-head { font-weight: 700; font-size: 16px; margin-bottom: 14px; color: #333; text-align: center; }
.custom-table { width: 100%; border-collapse: collapse; text-align: left; }
.custom-table th, .custom-table td { padding: 10px 8px; border-bottom: 1px dashed #ebedf0; }
.custom-table th { color: #969799; font-weight: 400; font-size: 14px; }
.custom-table td { color: #323233; font-weight: 500; }

.custom-table th:nth-child(1),
.custom-table td:nth-child(1) {
  text-align: left;
  padding-right: 16px; /* 从24px压缩到16px */
  padding-left: 6px; /* 从8px压缩到6px */
}

.custom-table th:nth-child(2),
.custom-table td:nth-child(2) {
  text-align: right;
  padding-left: 16px; /* 从24px压缩到16px */
  padding-right: 8px; /* 从12px压缩到8px */
  font-weight: 600; 
  color: #07c160; 
}

.dimension-group-row {
  color: #6b7280 !important;
  font-weight: 700 !important;
  background: #fafafa;
  text-align: left !important;
  padding-left: 8px !important;
  padding-right: 8px !important;
}
.link-cell {
  border: 0;
  background: transparent;
  color: inherit;
  text-decoration: none;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
  font-weight: inherit;
  text-align: left;
}
.loading-box { height: 100%; display: flex; justify-content: center; align-items: center; }
.scroll-body { padding: 20px; overflow-y: auto; height: calc(100% - 46px); background: #f7f8fa; }
.module-title { font-size: 16px; font-weight: 700; color: #333; margin-bottom: 15px; padding-left: 5px; border-left: 4px solid #1989fa; }
.module-gap { margin-top: 24px; }
.pre-media-box { background: #fff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); }
.plant-photos { display: flex; gap: 10px; }
.p-img { flex: 1; height: 110px; border-radius: 8px; overflow: hidden; border: 1px solid #ebedf0; cursor: pointer; }
.empty-text { font-size: 13px; color: #999; text-align: center; padding: 20px; }
.img-group { display: grid; grid-template-columns: 1fr; gap: 15px; }
.img-item { background: #fff; padding: 12px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); }
.item-tag { font-size: 13px; font-weight: 700; color: #666; margin-bottom: 10px; text-align: center; }
.img-item .van-image { width: 100%; height: 160px; border-radius: 8px; overflow: hidden; background: #f2f3f5; cursor: pointer; border: 1px solid #f0f0f0; }
.selection-popup { padding: 16px; }
.selection-title { font-size: 18px; font-weight: 700; color: #1f2937; margin-bottom: 4px; }
.selection-subtitle { font-size: 13px; color: #6b7280; margin-bottom: 10px; }
.selection-grid {
  max-height: 50vh;
  overflow: auto;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding: 4px;
}

.selection-grid .student-card {
  height: 58px;
}

.selection-grid .id-tag {
  top: 3px;
  left: 5px;
  font-size: 11px;
}

.selection-grid .name-text {
  font-size: 14px;
}

@media (max-width: 768px) {
  .selection-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
