<template>
  <div class="teacher-container">
    <van-nav-bar title="教师指挥中心" fixed placeholder />

    <div class="main-content">
      <!-- ================= 学生在线状态 ================= -->
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
            <img
              v-for="idx in getFinalStars(student)"
              :key="`${student.student_id}-sun-${idx}`"
              src="/sun.svg"
              alt=""
              class="sun-inline-icon"
            />
          </div>
        </div>
      </div>

      <div class="tables-head-row">
        <div class="section-title tables-title">实时统计与可视化</div>
        <div class="analysis-switch" role="tablist" aria-label="统计分组切换">
          <button
            v-for="tab in analysisTabs"
            :key="tab.key"
            type="button"
            class="switch-btn"
            :class="{ active: activeAnalysis === tab.key }"
            @click="activeAnalysis = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <Transition name="analysis-slide" mode="out-in">
        <div class="analysis-grid" :key="activeAnalysis">
          <div class="data-table-box">
            <div class="table-head">{{ activeTableTitle }}</div>

            <div v-if="activeAnalysis === 'sensory'" class="stat-list">
              <div class="stat-row" v-for="row in sensoryRows" :key="row.key" @click="openSelectionPopup('sensory', row)">
                <div class="stat-bg" :style="{ width: getPercentage(getSensoryCount(row.key)) + '%' }"></div>
                <div class="stat-content">
                  <span class="stat-label">{{ row.label }}</span>
                  <span class="stat-value">{{ getSensoryCount(row.key) }} 人</span>
                </div>
              </div>
            </div>

            <div v-else-if="activeAnalysis === 'dimension'" class="stat-list">
              <template v-for="row in dimensionRows" :key="row.key">
                <div v-if="row.type === 'group'" class="dimension-group-row">{{ row.label }}</div>
                <div v-else class="stat-row" @click="openSelectionPopup('dimension', row)">
                  <div class="stat-bg" :style="{ width: getPercentage(getDimensionCount(row.key)) + '%' }"></div>
                  <div class="stat-content">
                    <span class="stat-label">{{ row.label }}</span>
                    <span class="stat-value">{{ getDimensionCount(row.key) }} 人</span>
                  </div>
                </div>
              </template>
            </div>

            <div v-else-if="activeAnalysis === 'resource'" class="stat-list">
              <div class="stat-row" v-for="row in resourceRows" :key="row.key" @click="openSelectionPopup('resource', row)">
                <div class="stat-bg resource-bg" :style="{ width: Math.min((getResourceCount(row.key) / 100) * 100, 100) + '%' }"></div>
                <div class="stat-content">
                  <span class="stat-label">{{ row.label }}</span>
                  <span class="stat-value">
                    {{ row.key === '__none_clicked__' ? `${getResourceUserCount(row.key)} 人` : `${getResourceUserCount(row.key)} 人 ${getResourceCount(row.key)} 次` }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="stat-list">
              <template v-for="row in writingRows" :key="row.key">
                <div v-if="row.type === 'group'" class="dimension-group-row">{{ row.label }}</div>
                <div v-else class="stat-row" @click="openSelectionPopup('writing', row)">
                  <div class="stat-bg" :style="{ width: getPercentage(getWritingCount(row.key)) + '%' }"></div>
                  <div class="stat-content">
                    <span class="stat-label">{{ row.label }}</span>
                    <span class="stat-value">{{ getWritingCount(row.key) }} 人</span>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <div class="chart-box"><div ref="activeChartRef" class="echart-instance"></div></div>
        </div>
      </Transition>
    </div>

    <van-button class="floating-refresh-btn" type="primary" round @click="handleManualRefresh">
      刷新
    </van-button>

    <!-- 学生档案抽屉 -->
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
          <div class="module-title">学生的植物朋友照片</div>
          <div class="pre-media-box">
            <div class="plant-photos" v-if="activeData.pre_plant_1 || activeData.pre_plant_2 || activeData.pre_plant_3">
              <van-image v-if="activeData.pre_plant_1" :src="activeData.pre_plant_1" fit="cover" class="p-img" @click="preview(activeData.pre_plant_1)" />
              <van-image v-if="activeData.pre_plant_2" :src="activeData.pre_plant_2" fit="cover" class="p-img" @click="preview(activeData.pre_plant_2)" />
              <van-image v-if="activeData.pre_plant_3" :src="activeData.pre_plant_3" fit="cover" class="p-img" @click="preview(activeData.pre_plant_3)" />
            </div>
            <div v-else class="empty-text">该生暂无植物照片</div>
          </div>

          <div class="module-title module-gap">获得阳光情况</div>
          <div class="star-detail-box">
            <div class="star-stage-item">
              <div class="star-stage-head">
                <span class="stage-name">了解环节</span>
                <span class="stage-stars">{{ Number(activeData.stage1_stars || 0) }} <img src="/sun.svg" alt="" class="sun-inline-icon" /></span>
              </div>
              <div class="stage-selection">
                {{ formatSelectionList(activeData.sensory_evaluations, 'sensory', '未选择观察方法') }}
              </div>
            </div>

            <div class="star-stage-item">
              <div class="star-stage-head">
                <span class="stage-name">记录环节</span>
                <span class="stage-stars">{{ Number(activeData.stage3_stars || 0) }} <img src="/sun.svg" alt="" class="sun-inline-icon" /></span>
              </div>
              <div class="stage-selection">
                {{ formatSelectionList(activeData.dimension_evaluations, 'dimension', '未选择新发现选项') }}
              </div>
            </div>

            <div class="star-stage-item">
              <div class="star-stage-head">
                <span class="stage-name">试写环节</span>
                <span class="stage-stars">{{ Number(activeData.stage5_stars || 0) }} <img src="/sun.svg" alt="" class="sun-inline-icon" /></span>
              </div>
              <div class="stage-selection">
                {{ formatSelectionList(activeData.stage5_checks, 'writing', '未勾选试写表现') }}
              </div>
            </div>

            <div class="star-total-row">
              <span>总计</span>
              <span class="total-stars">{{ Number(activeData.total_stars || 0) }} <img src="/sun.svg" alt="" class="sun-inline-icon" /></span>
            </div>
          </div>
        </div>
      </div>
    </van-popup>

    <!-- 选择弹窗 -->
    <van-popup v-model:show="showSelectionPopup" position="center" round :style="{ width: '640px', maxWidth: '96vw' }">
      <div class="selection-popup">
        <div class="selection-title">{{ selectionTitle }}</div>
        <div class="selection-subtitle">选择该词条的学生（已选择 {{ selectedCount }} 人）</div>
        <div v-if="selectedStudents.length" class="selection-grid">
          <div
            v-for="item in selectedStudents"
            :key="item.id"
            class="student-card s-online"
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
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue';
import axios from 'axios';
import { showImagePreview, showToast } from 'vant';
import * as echarts from 'echarts';

// --- 数据状态 ---
const studentList = ref([]);
const stats = ref({ online: 0, total: 50, table1: {}, table2: {}, table3: {}, table4: {}, resource_completed: 0 });

const showDrawer = ref(false);
const activeData = ref(null);
const detailLoading = ref(false);
const showSelectionPopup = ref(false);
const selectionTitle = ref('');
const selectedStudents = ref([]);
const selectedCount = ref(0);
const analysisTabs = [
  { key: 'sensory', label: '了解' },
  { key: 'dimension', label: '新发现' },
  { key: 'resource', label: '资源' },
  { key: 'writing', label: '写作' },
];
const activeAnalysis = ref('sensory');

// --- 表格定义 ---
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
  { key: '我的植物朋友照片', label: '照片点击次数' },
  { key: '顺序百宝箱', label: '可以这样“连”' },
  { key: '感受小锦囊', label: '可以这样“合”' },
  { key: '词语百花园', label: '可以这样“用”' },
  { key: '__none_clicked__', label: '未点击任何资源人数' },
];

const writingRows = [
  { key: 'writing-group-clarity', label: '1.我试着写清楚了。', type: 'group' },
  { key: '(1)我从多方面介绍了植物朋友', label: '(1)我从多方面介绍了植物朋友。' },
  { key: '(2)我是把几个方面连起来写的。', label: '(2)我是把几个方面连起来写的。' },
  { key: '2.我分享了我的习作。', label: '2.我分享了我的习作。' },
];

const activeTableTitle = computed(() => {
  const titleMap = {
    sensory: '方法统计',
    dimension: '新发现统计',
    resource: '资源点击统计',
    writing: '写作目标达成统计',
  };
  return titleMap[activeAnalysis.value] || '实时统计';
});

// --- 辅助统计函数 ---
const getSensoryCount = (name) => {
  const aliasMap = { '看一看': ['看一看'], '闻一闻': ['闻一闻'], '摸一摸': ['摸一摸'], '听一听': ['听一听'], '尝一尝': ['尝一尝'], '其他': ['其他'] };
  return (aliasMap[name] || [name]).reduce((sum, key) => sum + (stats.value.table1?.[key] || 0), 0);
};

const getDimensionCount = (name) => {
  const aliasMap = {
    '我暂时没有新的发现': ['我暂时没有新的发现', '我暂时没有新的发现。'],
    '我已经有了新的发现：（1）有以前没观察到的': ['我已经有了新的发现：（1）有以前没观察到的', '评价一：能真实记录植物特点', '评价一'],
    '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': ['我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）'],
  };
  return (aliasMap[name] || [name]).reduce((sum, key) => sum + (stats.value.table2?.[key] || 0), 0);
};

const getResourceCount = (resourceName) => {
  if (resourceName === '__none_clicked__') return getNoResourceClickStudentCount();
  const rows = Object.entries(stats.value.table3 || {});
  return rows.reduce((sum, [key, count]) => {
    if (String(key).startsWith(resourceName)) return sum + Number(count || 0);
    return sum;
  }, 0);
};

const getResourceUserCount = (resourceName) => {
  if (resourceName === '__none_clicked__') return getNoResourceClickStudentCount();
  const students = studentList.value || [];
  return students.filter((student) => {
    const clickMap = student.resource_click_stats || {};
    return Object.entries(clickMap).some(([k, v]) => String(k).startsWith(resourceName) && Number(v || 0) > 0);
  }).length;
};

const getNoResourceClickStudentCount = () => {
  const students = studentList.value || [];
  return students.filter((student) => {
    const clickMap = student.resource_click_stats || {};
    const totalClicks = Object.values(clickMap).reduce((sum, v) => sum + Number(v || 0), 0);
    return totalClicks === 0;
  }).length;
};

const getWritingCount = (name) => {
  const aliasMap = {
    '(1)我从多方面介绍了植物朋友': ['(1)我从多方面介绍了植物朋友', '（1）我是从多方面写的', '（1）我能从多方面介绍', '（1）我能从多方面介绍。（√）'],
    '(2)我是把几个方面连起来写的。': ['(2)我是把几个方面连起来写的。', '（2）我是按照一定顺序写的', '（2）我能有顺序介绍', '（2）我能有顺序介绍。（√）'],
    '2.我分享了我的习作。': ['2.我分享了我的习作。', '2.我还愿意把习作分享给别人', '2.我分享了我的习作', '我分享了我的习作'],
  };
  return (aliasMap[name] || [name]).reduce((sum, key) => sum + (stats.value.table4?.[key] || 0), 0);
};

const getPercentage = (count) => {
  const total = stats.value.total || 50;
  return total === 0 ? 0 : Math.min((count / total) * 100, 100);
};

const getFinalStars = (student) => {
  if (!student) return 0;
  const candidates = [student.total_stars, student.totalStars, student.final_stars, student.finalStars, student.stage_total_stars];
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

// --- 名单弹窗映射 ---
const getSensoryAliases = (name) => {
  const aliasMap = { '看一看': ['看一看', '看了看'], '闻一闻': ['闻一闻', '闻了闻'], '摸一摸': ['摸一摸', '摸了摸'], '听一听': ['听一听'], '尝一尝': ['尝一尝', '尝了尝'], '其他': ['其他'] };
  return aliasMap[name] || [name];
};
const getDimensionAliases = (name) => {
  const aliasMap = { '我暂时没有新的发现': ['我暂时没有新的发现', '我暂时没有新的发现。'], '我已经有了新的发现：（1）有以前没观察到的': ['我已经有了新的发现：（1）有以前没观察到的', '评价一：能真实记录植物特点', '评价一'], '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': ['我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）'] };
  return aliasMap[name] || [name];
};
const getWritingAliases = (name) => {
  const aliasMap = {
    '(1)我从多方面介绍了植物朋友': ['(1)我从多方面介绍了植物朋友', '（1）我是从多方面写的', '（1）我能从多方面介绍', '（1）我能从多方面介绍。（√）'],
    '(2)我是把几个方面连起来写的。': ['(2)我是把几个方面连起来写的。', '（2）我是按照一定顺序写的', '（2）我能有顺序介绍', '（2）我能有顺序介绍。（√）'],
    '2.我分享了我的习作。': ['2.我分享了我的习作。', '2.我还愿意把习作分享给别人', '2.我分享了我的习作', '我分享了我的习作'],
  };
  return aliasMap[name] || [name];
};

const isStudentSelectedByRow = (student, type, key) => {
  if (type === 'sensory') {
    const values = student.sensory_evaluations || [];
    const aliases = getSensoryAliases(key);
    return values.some((item) => aliases.includes(String(item).trim()));
  }
  if (type === 'dimension') {
    const values = student.dimension_evaluations || [];
    const aliases = getDimensionAliases(key);
    return values.some((item) => aliases.includes(String(item).trim()));
  }
  if (type === 'resource') {
    if (key === '__none_clicked__') {
      const statsMap = student.resource_click_stats || {};
      const totalClicks = Object.values(statsMap).reduce((sum, v) => sum + Number(v || 0), 0);
      return totalClicks === 0;
    }
    const statsMap = student.resource_click_stats || {};
    return Object.entries(statsMap).some(([k, v]) => String(k).startsWith(key) && Number(v || 0) > 0);
  }
  if (type === 'writing') {
    const values = student.stage5_checks || [];
    const aliases = getWritingAliases(key);
    return values.some((item) => aliases.includes(String(item).trim()));
  }
  return false;
};

const openSelectionPopup = (type, row) => {
  selectedStudents.value = (studentList.value || [])
    .filter((s) => isStudentSelectedByRow(s, type, row.key))
    .map((s) => ({
      id: String(s.student_id || '').padStart(2, '0'),
      name: s.student_name || '未命名',
    }));
  selectedCount.value = selectedStudents.value.length;
  selectionTitle.value = row.label;
  showSelectionPopup.value = true;
};

// --- WebSocket 与数据请求 ---
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
      table4: res.data.table4_writing || {},  
      resource_completed: res.data.resource_completed_count || 0,
    };
  } catch (err) {
    console.error('刷新大屏失败:', err);
  }
};

const handleManualRefresh = async () => {
  await fetchDashboardData();
  showToast('统计已刷新');
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
  socket.onopen = () => { if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; } };
  socket.onmessage = (event) => { const data = JSON.parse(event.data); if (data.action === 'REFRESH_DASHBOARD') fetchDashboardData(); };
  socket.onclose = () => { reconnectTimer = setTimeout(initWebSocket, 3000); };
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

const formatSelectionItem = (item, type) => {
  const text = String(item || '').trim();
  if (!text) return '';

  if (type === 'sensory') {
    const map = {
      看了看: '看一看',
      闻了闻: '闻一闻',
      摸了摸: '摸一摸',
      尝了尝: '尝一尝',
    };
    return map[text] || text;
  }

  if (type === 'dimension') {
    if (text.includes('暂时没有新的发现')) return '我暂时没有新的发现。';
    if (text.includes('（1）') || text.includes('(1)') || text.includes('以前没观察到')) {
      return '（1）有以前没观察到的';
    }
    if (text.includes('（2）') || text.includes('(2)') || text.includes('有了点儿感受')) {
      return '（2）观察后，有了点儿感受（身体感觉 心里想法）';
    }
    return text;
  }

  if (type === 'writing') {
    if (text.includes('（1）') || text.includes('(1)') || text.includes('多方面')) {
      return '(1)我从多方面介绍了植物朋友';
    }
    if (text.includes('（2）') || text.includes('(2)') || text.includes('顺序') || text.includes('连起来')) {
      return '(2)我是把几个方面连起来写的。';
    }
    if (text.includes('分享')) {
      return '2.我分享了我的习作。';
    }
    return text;
  }

  return text;
};

const formatSelectionList = (items, type, emptyText = '暂无') => {
  const arr = Array.isArray(items) ? items : [];
  const normalized = arr
    .map((x) => formatSelectionItem(x, type))
    .filter(Boolean);
  return normalized.length ? normalized.join('；') : emptyText;
};

// ================= ECharts 可视化图表逻辑 =================
const activeChartRef = ref(null);
let activeChart = null;
let resizeHandler = null;

const initCharts = () => {
  if (!activeChartRef.value) return;
  if (activeChart) {
    activeChart.dispose();
  }
  activeChart = echarts.init(activeChartRef.value);
  activeChart.on('click', handleChartClick);
  requestAnimationFrame(() => {
    if (!activeChart) return;
    activeChart.resize();
    updateCharts();
  });
};

const updateCharts = () => {
  if (!activeChart) return;

  if (activeAnalysis.value === 'sensory') {
    activeChart.setOption({
    title: { text: '方法使用倾向', textStyle: { fontSize: 14, color: '#666' }, left: 'center' },
    tooltip: { trigger: 'axis' },
    color: ['#07c160'],
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: sensoryRows.map(r => r.key), axisLabel: { interval: 0, rotate: 30 } },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'bar', barWidth: '40%', data: sensoryRows.map(r => getSensoryCount(r.key)), itemStyle: { borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}人' } }]
    });
    return;
  }

  if (activeAnalysis.value === 'dimension') {
    const dData = dimensionRows.filter(r => r.type !== 'group').map(r => {
    const shortNames = {
      '我暂时没有新的发现': '无新发现',
      '我已经有了新的发现：（1）有以前没观察到的': '新观察',
      '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': '新感受'
    };
    return { name: shortNames[r.key] || r.key, value: getDimensionCount(r.key) };
    }).filter(d => d.value > 0);

    activeChart.setOption({
    title: { text: '新发现维度占比', textStyle: { fontSize: 14, color: '#666' }, left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}<br/>{c}人 ({d}%)' },
    legend: { top: 'bottom', textStyle: { fontSize: 12 }, itemWidth: 10, itemHeight: 10 },
    color: ['#1989fa', '#ff976a', '#ee0a24'],
    series: [{
      type: 'pie', radius: ['20%', '50%'], center: ['50%', '45%'], roseType: 'area',
      itemStyle: { borderRadius: 4 },
      label: { show: dData.length > 0, formatter: '{b}\n{c}人' },
      data: dData.length > 0 ? dData : [{ name: '暂无数据', value: 0 }]
    }]
    });
    return;
  }

  if (activeAnalysis.value === 'resource') {
    const rankedResourceRows = [...resourceRows].sort((a, b) => getResourceCount(b.key) - getResourceCount(a.key));
    activeChart.setOption({
    title: { text: '资源包热度排行', textStyle: { fontSize: 14, color: '#666' }, left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    color: ['#f2bd27'],
    grid: { left: '3%', right: '24%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', inverse: true, data: rankedResourceRows.map(r => r.label), axisLabel: { width: 140, overflow: 'truncate' } },
    series: [{
      type: 'bar',
      data: rankedResourceRows.map((r) => ({
        key: r.key,
        value: getResourceCount(r.key),
        userCount: getResourceUserCount(r.key),
      })),
      label: {
        show: true,
        position: 'right',
        formatter: (params) => {
          if (params?.data?.key === '__none_clicked__') {
            return `${params.data.userCount}人`;
          }
          return `${params.data.userCount}人 ${params.data.value}次`;
        },
      },
      itemStyle: { borderRadius: [0, 4, 4, 0] },
    }]
    });
    return;
  }

  const wData = writingRows.filter(r => r.type !== 'group').map(r => {
    const shortNames = {
      '(1)我从多方面介绍了植物朋友': '多方面',
      '(2)我是把几个方面连起来写的。': '连起来',
      '2.我分享了我的习作。': '愿分享',
    };
    return { name: shortNames[r.key] || r.label, value: getWritingCount(r.key) };
  }).filter(d => d.value > 0);

  activeChart.setOption({
    title: { text: '写作目标达成度', textStyle: { fontSize: 14, color: '#666' }, left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}<br/>{c}人 ({d}%)' },
    legend: { top: 'bottom', textStyle: { fontSize: 12 }, itemWidth: 10, itemHeight: 10 },
    color: ['#7232dd', '#07c160', '#ff976a'],
    series: [{
      type: 'pie', radius: ['35%', '50%'], center: ['50%', '45%'], avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: wData.length > 0, formatter: '{b}\n{c}人' },
      data: wData.length > 0 ? wData : [{ name: '暂无数据', value: 0 }]
    }]
  });
};

const handleChartClick = (params) => {
  if (activeAnalysis.value === 'sensory') {
    const row = sensoryRows.find((r) => r.key === params?.name);
    if (row) openSelectionPopup('sensory', row);
    return;
  }
  if (activeAnalysis.value === 'dimension') {
    const dimensionChartMap = {
      '无新发现': '我暂时没有新的发现',
      '新观察': '我已经有了新的发现：（1）有以前没观察到的',
      '新感受': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    };
    const key = dimensionChartMap[params?.name];
    if (!key) return;
    const row = dimensionRows.find((r) => r.key === key);
    if (row) openSelectionPopup('dimension', row);
    return;
  }
  if (activeAnalysis.value === 'resource') {
    const row = resourceRows.find((r) => r.label === params?.name);
    if (row) openSelectionPopup('resource', row);
    return;
  }

  const writingChartMap = {
    多方面: '(1)我从多方面介绍了植物朋友。',
    连起来: '(2)我是把几个方面连起来写的。',
    愿分享: '2.我分享了我的习作。',
  };
  const key = writingChartMap[params?.name];
  if (!key) return;
  const row = writingRows.find((r) => r.key === key);
  if (row) openSelectionPopup('writing', row);
};

watch(() => stats.value, () => { nextTick(updateCharts); }, { deep: true });
watch(activeAnalysis, async () => {
  await nextTick();
  // out-in 过渡期间容器可能尚未完成挂载，延迟一帧再初始化更稳定
  requestAnimationFrame(() => initCharts());
});
watch(activeChartRef, (el) => {
  if (!el) return;
  requestAnimationFrame(() => initCharts());
});

onMounted(() => {
  fetchDashboardData();
  initWebSocket();
  pollTimer = setInterval(fetchDashboardData, 30000);

  nextTick(() => {
    initCharts();
    resizeHandler = () => {
      if (activeChart) activeChart.resize();
    };
    window.addEventListener('resize', resizeHandler);
  });
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (socket) {
    socket.onclose = null;
    socket.close();
  }
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler);
  }
  if (activeChart) {
    activeChart.dispose();
    activeChart = null;
  }
});
</script>

<style scoped>
/* ================= 核心基础布局 ================= */
.teacher-container { 
  height: 100dvh; 
  background-color: #F4F7F5; 
  display: flex; 
  flex-direction: column; 
  overflow-y: auto; 
  overflow-x: hidden; 
  padding-bottom: 100px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 覆盖 Vant 导航栏，使其更符合后台专业感 */
:deep(.van-nav-bar) {
  background-color: #2D4A38; /* 深邃的黑板绿 */
  z-index: 100 !important; /* 确保层级最高 */
}
:deep(.van-nav-bar__title) {
  color: #FFFFFF;
  font-weight: 800;
  letter-spacing: 1px;
}
:deep(.van-nav-bar .van-icon) {
  color: #FFFFFF;
}

/* 核心修复：顶部增加 70px 避开固定的导航栏 */
.main-content { 
  padding: 70px 24px 40px 24px; 
  max-width: 1400px; 
  margin: 0 auto; 
  width: 100%; 
  box-sizing: border-box; 
}

@media (min-width: 768px) and (max-width: 1199px) {
  .teacher-container {
    padding-bottom: env(safe-area-inset-bottom, 150px);
  }
  .main-content {
    /* 平板端也增加顶部 padding */
    padding: 80px 36px 40px 36px;
  }
  .matrix-grid { grid-template-columns: repeat(7, 1fr); gap: 16px; }
  .student-card { height: 92px; }
  .name-text { font-size: 16px; }
  .section-title { font-size: 20px; }
  .highlight { font-size: 26px; }
}

/* ================= 标题与全局控件 ================= */
.section-title { 
  font-size: 18px; 
  font-weight: 800; 
  color: #2C3E50; 
  margin-bottom: 20px; 
  border-left: 5px solid #4CAF50; /* 标志性的自然绿左边框 */
  padding-left: 12px; 
  display: flex;
  align-items: center;
}

.tables-title { 
  margin-top: 36px; 
  border-left-color: #3B82F6; /* 图表区用清爽蓝区分 */
}

.highlight { 
  color: #4CAF50; 
  font-size: 24px; 
  margin: 0 4px;
}

.tables-head-row {
  margin-top: 40px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}
.tables-head-row .tables-title {
  margin-top: 0;
  margin-bottom: 0;
}

/* 统计分组切换按钮：类似教案本的标签页 */
.analysis-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px;
  border-radius: 12px;
  background: #E8ECEF;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}
.switch-btn {
  border: none;
  background: transparent;
  color: #64748B;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}
.switch-btn.active {
  background: #FFFFFF;
  color: #2D4A38;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 悬浮刷新按钮 */
.floating-refresh-btn {
  position: fixed;
  right: calc((100vw - min(1400px, 100vw)) / 2 - 22px);
  top: 50%;
  transform: translateY(-50%);
  z-index: 1200;
}
:deep(.floating-refresh-btn.van-button) {
  min-width: 64px;
  height: 64px;
  font-size: 15px;
  font-weight: 800;
  background: #4CAF50;
  border: none;
  box-shadow: 0 8px 20px rgba(76, 175, 80, 0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
:deep(.floating-refresh-btn.van-button:hover) {
  transform: translateY(-50%) scale(1.05);
  box-shadow: 0 10px 24px rgba(76, 175, 80, 0.45);
}


/* ================= 学生在线状态矩阵 ================= */
.matrix-grid { 
  display: grid; 
  grid-template-columns: repeat(10, 1fr); 
  gap: 14px; 
}

.student-card { 
  height: 86px; 
  border-radius: 10px; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center; 
  position: relative; 
  cursor: pointer; 
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.student-card:active { 
  transform: scale(0.96); 
}

/* 在线状态：清爽的自然绿 */
.s-online { 
  background-color: #F0FAF4; 
  border: 1px solid #A2D8B6; 
  color: #246B3E; 
  box-shadow: 0 2px 6px rgba(162, 216, 182, 0.2);
}
/* 离线状态：低调的灰白色 */
.s-offline { 
  background-color: #FFFFFF; 
  border: 1px solid #E2E8F0; 
  color: #94A3B8; 
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
}

.id-tag { 
  position: absolute; 
  top: 6px; 
  left: 8px; 
  font-size: 12px; 
  font-weight: 800; 
  background: rgba(0, 0, 0, 0.06); 
  padding: 2px 6px; 
  border-radius: 4px; 
  font-family: monospace;
}

.name-text { 
  font-size: 15px; 
  font-weight: 800; 
  margin-top: 8px; 
  letter-spacing: 0.5px;
}

.star-row { 
  margin-top: 6px; 
  line-height: 1;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.sun-inline-icon {
  width: 1em;
  height: 1em;
  vertical-align: -0.08em;
}


/* ================= 数据图表与统计区 ================= */
.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); 
  gap: 24px;
}

.analysis-slide-enter-active,
.analysis-slide-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.analysis-slide-enter-from { opacity: 0; transform: translateX(14px); }
.analysis-slide-leave-to { opacity: 0; transform: translateX(-14px); }

@keyframes statRowIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes statFillIn {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

.data-table-box, .chart-box { 
  background: #FFFFFF; 
  border-radius: 16px; 
  padding: 20px 16px; 
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); 
  border: 1px solid #E2E8F0;
  min-width: 0; 
  overflow: hidden; 
}
.data-table-box { border-top: 4px solid #4CAF50; }
.chart-box { border-top: 4px solid #3B82F6; }

.table-head { 
  font-weight: 800; 
  font-size: 17px; 
  margin-bottom: 20px; 
  color: #2C3E50; 
  text-align: center; 
}

.stat-list { 
  display: flex; 
  flex-direction: column; 
  gap: 10px; 
}

.dimension-group-row {
  font-size: 14px;
  font-weight: 800;
  color: #64748B;
  margin-top: 10px;
  padding-bottom: 6px;
  border-bottom: 2px dashed #E2E8F0;
}

.stat-row {
  position: relative;
  border-radius: 8px;
  background: #F8FAFC;
  border: 1px solid #F1F5F9;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.15s ease;
  opacity: 0;
  animation: statRowIn 0.8s ease forwards;
}
.stat-row:active { transform: scale(0.98); }

.stat-bg {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  background: linear-gradient(90deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.2));
  border-right: 2px solid #4CAF50;
  transition: width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 1;
  transform-origin: left center;
  animation: statFillIn 1s cubic-bezier(0.22, 0.8, 0.34, 1) both;
}
.resource-bg { 
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.2)); 
  border-right-color: #F59E0B; 
}

.stat-content {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
}

.stat-label { font-size: 14px; color: #334155; font-weight: 700; }
.stat-value { font-size: 15px; color: #2C3E50; font-weight: 900; }

.echart-instance { width: 100%; height: 300px; }

/* ================= 响应式调整 ================= */
@media (max-width: 900px) {
  .tables-head-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .analysis-switch {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .analysis-grid { grid-template-columns: 1fr; }
}


/* ================= 学生详情侧边抽屉 ================= */
.loading-box { height: 100%; display: flex; justify-content: center; align-items: center; }
.detail-panel { height: 100%; display: flex; flex-direction: column; min-height: 0; }
.scroll-body {
  flex: 1;
  min-height: 0;
  padding: 24px 20px;
  overflow-y: auto;
  background: #F4F7F5; 
  -webkit-overflow-scrolling: touch;
}

.module-title { 
  font-size: 17px; 
  font-weight: 800; 
  color: #2C3E50; 
  margin-bottom: 16px; 
  padding-left: 10px; 
  border-left: 4px solid #4CAF50; 
}
.module-gap { margin-top: 32px; }

.pre-media-box { 
  background: #FFFFFF; 
  padding: 16px; 
  border-radius: 12px; 
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02); 
}
.plant-photos { display: flex; gap: 12px; }
.p-img { 
  flex: 1; 
  height: 120px; 
  border-radius: 6px; 
  overflow: hidden; 
  border: 1px solid #CBD5E1; 
  cursor: pointer; 
  transition: transform 0.2s;
}
.empty-text { font-size: 14px; color: #94A3B8; text-align: center; padding: 24px; font-weight: 700;}

.star-detail-box { 
  background: #FFFFFF; 
  padding: 16px; 
  border-radius: 12px; 
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02); 
  display: flex; 
  flex-direction: column; 
  gap: 12px; 
}
.star-stage-item { 
  border: 1px solid #E2E8F0; 
  border-radius: 8px; 
  padding: 14px; 
  background: #F8FAFC; 
}
.star-stage-head { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 8px; 
}
.stage-name { font-size: 15px; font-weight: 800; color: #334155; }
.stage-stars { font-size: 16px; font-weight: 900; color: #F59E0B; }
.stage-selection { font-size: 14px; line-height: 1.5; color: #64748B; font-weight: 500;}

.star-total-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 14px 16px; 
  border-radius: 8px; 
  background: #F0FAF4; 
  border: 1px solid #A2D8B6; 
  font-size: 16px; 
  font-weight: 800; 
  color: #246B3E; 
  margin-top: 4px;
}
.total-stars { font-size: 20px; font-weight: 900; color: #F59E0B; }


/* ================= 选择人员弹窗 ================= */
.selection-popup { padding: 20px; }
.selection-title { font-size: 20px; font-weight: 800; color: #2C3E50; margin-bottom: 6px; }
.selection-subtitle { font-size: 14px; color: #64748B; margin-bottom: 16px; font-weight: 700;}

.selection-grid { 
  max-height: 60vh; 
  overflow: auto; 
  display: grid; 
  grid-template-columns: repeat(3, minmax(0, 1fr)); 
  gap: 12px; 
  padding: 4px; 
}
.selection-grid .student-card { height: 80px; cursor: default; }
.selection-grid .id-tag { top: 6px; left: 8px; font-size: 13px; }
.selection-grid .name-text { font-size: 16px; font-weight: 800; }

@media (max-width: 768px) { 
  .selection-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } 
}
</style>

