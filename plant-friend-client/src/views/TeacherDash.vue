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
            {{ formatStars(getFinalStars(student)) }}
          </div>
          <div v-if="student.final_img" class="medal-icon">🏅</div>
        </div>
      </div>

      <div class="section-title tables-title">实时统计与可视化</div>
      <div class="analysis-grid">
        <div class="data-table-box">
          <div class="table-head">观察方法统计</div>
          <div class="stat-list">
            <div class="stat-row" v-for="row in sensoryRows" :key="row.key" @click="openSelectionPopup('sensory', row)">
              <div class="stat-bg" :style="{ width: getPercentage(getSensoryCount(row.key)) + '%' }"></div>
              <div class="stat-content">
                <span class="stat-label">{{ row.label }}</span>
                <span class="stat-value">{{ getSensoryCount(row.key) }} 人</span>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-box"><div ref="chart1Ref" class="echart-instance"></div></div>

        <div class="data-table-box">
          <div class="table-head">新发现统计</div>
          <div class="stat-list">
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
        </div>
        <div class="chart-box"><div ref="chart2Ref" class="echart-instance"></div></div>

        <div class="data-table-box">
          <div class="table-head">资源点击统计</div>
          <div class="stat-list">
            <div class="stat-row" v-for="row in resourceRows" :key="row.key" @click="openSelectionPopup('resource', row)">
              <div class="stat-bg resource-bg" :style="{ width: Math.min((getResourceCount(row.key) / 100) * 100, 100) + '%' }"></div>
              <div class="stat-content">
                <span class="stat-label">{{ row.label }}</span>
                <span class="stat-value">{{ getResourceUserCount(row.key) }} 人 {{ getResourceCount(row.key) }} 次</span>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-box"><div ref="chart3Ref" class="echart-instance"></div></div>

        <div class="data-table-box">
          <div class="table-head">写作目标达成统计</div>
          <div class="stat-list">
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
        <div class="chart-box"><div ref="chart4Ref" class="echart-instance"></div></div>
      </div>
    </div>

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

    <!-- 选择弹窗 -->
    <van-popup v-model:show="showSelectionPopup" position="center" round :style="{ width: '480px', maxWidth: '92vw' }">
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
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue';
import axios from 'axios';
import { showImagePreview, showToast } from 'vant';
import * as echarts from 'echarts';
import { preloadTeacherAllImages } from '../utils/imagePreloader';

// --- 数据状态 ---
const studentList = ref([]);
const stats = ref({ online: 0, total: 50, table1: {}, table2: {}, table3: {}, table4: {}, table5: 0, resource_completed: 0 });

const showDrawer = ref(false);
const activeData = ref(null);
const detailLoading = ref(false);
const showSelectionPopup = ref(false);
const selectionTitle = ref('');
const selectedStudents = ref([]);
const selectedCount = ref(0);

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
  { key: '我的植物朋友照片', label: '我的植物朋友照片点击次数' },
  { key: '感受小锦囊', label: '感受小锦囊' },
  { key: '顺序百宝箱', label: '顺序百宝箱' },
  { key: '词语百花园', label: '词语百花园' },
  { key: '__none_clicked__', label: '未点击任何资源人数' },
];

const writingRows = [
  { key: 'writing-group-clarity', label: '1. 我试着写清楚了：', type: 'group' },
  { key: '（1）我能从多方面介绍', label: '（1）我能从多方面介绍' },
  { key: '（2）我能有顺序介绍', label: '（2）我能有顺序介绍' },
  { key: '2.我分享了我的习作', label: '2.我分享了我的习作' },
];

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
    '（1）我能从多方面介绍': ['（1）我能从多方面介绍', '（1）我能从多方面介绍。（√）'],
    '（2）我能有顺序介绍': ['（2）我能有顺序介绍', '（2）我能有顺序介绍。（√）'],
    '2.我分享了我的习作': ['2.我分享了我的习作', '我分享了我的习作'],
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

const formatStars = (count) => {
  const n = Math.max(0, Number(count) || 0);
  return n > 0 ? `⭐`.repeat(n) : '';
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
  const aliasMap = { '（1）我能从多方面介绍': ['（1）我能从多方面介绍', '（1）我能从多方面介绍。（√）'], '（2）我能有顺序介绍': ['（2）我能有顺序介绍', '（2）我能有顺序介绍。（√）'], '2.我分享了我的习作': ['2.我分享了我的习作', '我分享了我的习作'] };
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
      table5: res.data.table5_ai_count || 0,  
      resource_completed: res.data.resource_completed_count || 0,
    };
    preloadTeacherAllImages(studentList.value).catch((error) => {
      console.warn('Teacher image preloading failed:', error);
    });
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

// ================= ECharts 可视化图表逻辑 =================
const chart1Ref = ref(null);
const chart2Ref = ref(null);
const chart3Ref = ref(null);
const chart4Ref = ref(null);
let charts = [];

const initCharts = () => {
  if (!chart1Ref.value) return;
  const c1 = echarts.init(chart1Ref.value);
  const c2 = echarts.init(chart2Ref.value);
  const c3 = echarts.init(chart3Ref.value);
  const c4 = echarts.init(chart4Ref.value);
  charts = [c1, c2, c3, c4];

  c1.on('click', (params) => {
    const row = sensoryRows.find((r) => r.key === params?.name);
    if (row) openSelectionPopup('sensory', row);
  });

  const dimensionChartMap = {
    '无新发现': '我暂时没有新的发现',
    '新观察': '我已经有了新的发现：（1）有以前没观察到的',
    '新感受': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
  };
  c2.on('click', (params) => {
    const key = dimensionChartMap[params?.name];
    if (!key) return;
    const row = dimensionRows.find((r) => r.key === key);
    if (row) openSelectionPopup('dimension', row);
  });

  c3.on('click', (params) => {
    const row = resourceRows.find((r) => r.label === params?.name);
    if (row) openSelectionPopup('resource', row);
  });

  const writingChartMap = {
    '多方介绍': '（1）我能从多方面介绍',
    '有序介绍': '（2）我能有顺序介绍',
    '分享习作': '2.我分享了我的习作',
  };
  c4.on('click', (params) => {
    const key = writingChartMap[params?.name];
    if (!key) return;
    const row = writingRows.find((r) => r.key === key);
    if (row) openSelectionPopup('writing', row);
  });

  updateCharts();
};

const updateCharts = () => {
  if (charts.length === 0) return;

  // 1. 观察方法 (柱状图)
  charts[0].setOption({
    title: { text: '观察方法使用倾向', textStyle: { fontSize: 14, color: '#666' }, left: 'center' },
    tooltip: { trigger: 'axis' },
    color: ['#07c160'],
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: sensoryRows.map(r => r.key), axisLabel: { interval: 0, rotate: 30 } },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'bar', barWidth: '40%', data: sensoryRows.map(r => getSensoryCount(r.key)), itemStyle: { borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}人' } }]
  });

  // 2. 新发现 (玫瑰图) - 智能短化标签
  const dData = dimensionRows.filter(r => r.type !== 'group').map(r => {
    const shortNames = {
      '我暂时没有新的发现': '无新发现',
      '我已经有了新的发现：（1）有以前没观察到的': '新观察',
      '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': '新感受'
    };
    return { name: shortNames[r.key] || r.key, value: getDimensionCount(r.key) };
  }).filter(d => d.value > 0);

  charts[1].setOption({
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

  // 3. 资源点击 (横向条形图) - 使用完整的 r.label
  charts[2].setOption({
    title: { text: '资源包热度排行', textStyle: { fontSize: 14, color: '#666' }, left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    color: ['#f2bd27'],
    grid: { left: '3%', right: '24%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', inverse: true, data: resourceRows.map(r => r.label), axisLabel: { width: 140, overflow: 'truncate' } },
    series: [{
      type: 'bar',
      data: resourceRows.map((r) => ({
        value: getResourceCount(r.key),
        userCount: getResourceUserCount(r.key),
      })),
      label: { show: true, position: 'right', formatter: (params) => `${params.data.userCount}人 ${params.data.value}次` },
      itemStyle: { borderRadius: [0, 4, 4, 0] },
    }]
  });

  // 4. 写作目标 (环形图) - 智能短化标签
  const wData = writingRows.filter(r => r.type !== 'group').map(r => {
    const shortNames = {
      '（1）我能从多方面介绍': '多方介绍',
      '（2）我能有顺序介绍': '有序介绍',
      '2.我分享了我的习作': '分享习作'
    };
    return { name: shortNames[r.key] || r.key, value: getWritingCount(r.key) };
  }).filter(d => d.value > 0);

  charts[3].setOption({
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

watch(() => stats.value, () => { nextTick(updateCharts); }, { deep: true });

onMounted(() => {
  fetchDashboardData();
  initWebSocket();
  pollTimer = setInterval(fetchDashboardData, 60000);

  nextTick(() => {
    initCharts();
    window.addEventListener('resize', () => charts.forEach(c => c.resize()));
  });
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (socket) {
    socket.onclose = null;
    socket.close();
  }
  window.removeEventListener('resize', () => charts.forEach(c => c.resize()));
});
</script>

<style scoped>
/* ================= 核心修复：防止导航栏遮挡 ================= */
.teacher-container { 
  height: 100%; 
  background-color: #f2f3f5; 
  display: flex; 
  flex-direction: column; 
  overflow-y: auto; 
  overflow-x: hidden; 
  padding-bottom: 100px;
}

.main-content { 
  padding: 60px 24px 24px 24px; /* 顶部留出 60px 安全距离，避免被 fixed 的 nav-bar 遮挡 */
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
    padding: 60px 36px 36px 36px;
  }
  .tables-title { margin-top: 48px; }
  .matrix-grid { grid-template-columns: repeat(7, 1fr); gap: 16px; }
  .student-card { height: 92px; }
  .name-text { font-size: 16px; }
  .section-title { font-size: 22px; }
  .highlight { font-size: 28px; }
}

.section-title { font-size: 20px; font-weight: 700; color: #333; margin-bottom: 20px; border-left: 5px solid #07c160; padding-left: 12px; }
.tables-title { margin-top: 36px; border-left-color: #1989fa; }
.highlight { color: #07c160; font-size: 26px; }

/* 学生卡片 */
.matrix-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 12px; }
.student-card { height: 82px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; cursor: pointer; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); transition: transform 0.15s; }
.student-card:active { transform: scale(0.98); }
.s-online { background-color: #eafaf1; border: 1px solid #8ce6b0; color: #1e8e3e; }
.s-offline { background-color: #fff; border: 1px solid #dcdee0; color: #969799; }
.id-tag { position: absolute; top: 4px; left: 6px; font-size: 12px; font-weight: 700; background: rgba(0, 0, 0, 0.05); padding: 2px 6px; border-radius: 4px; }
.name-text { font-size: 15px; font-weight: 700; margin-top: 6px; }
.star-row { margin-top: 4px; font-size: 14px; line-height: 1; letter-spacing: 1px; color: #f59e0b; font-weight: 700; }
.medal-icon { position: absolute; top: -8px; right: -6px; font-size: 18px; }

/* 表格与图表布局 */
.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); 
  gap: 24px;
}

.data-table-box, .chart-box { 
  background: #fff; 
  border-radius: 12px; 
  padding: 16px 12px; 
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04); 
  border-top: 4px solid #07c160; 
  min-width: 0; 
  overflow: hidden; 
}
.chart-box { border-top-color: #1989fa; }

.table-head { font-weight: 700; font-size: 16px; margin-bottom: 14px; color: #333; text-align: center; }

/* ================= 进度条表格样式 ================= */
.stat-list { display: flex; flex-direction: column; gap: 8px; }

.dimension-group-row {
  font-size: 13px;
  font-weight: 700;
  color: #969799;
  margin-top: 8px;
  padding-bottom: 4px;
  border-bottom: 1px dashed #ebedf0;
}

.stat-row {
  position: relative;
  border-radius: 6px;
  background: #f7f8fa;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.1s;
}
.stat-row:active { transform: scale(0.98); }
.stat-row:hover { background: #f0f3f6; }

/* 进度条背景 */
.stat-bg {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  background: rgba(7, 193, 96, 0.12);
  transition: width 0.5s ease-out;
  z-index: 1;
}
.resource-bg { background: rgba(242, 189, 39, 0.15); border-left: 2px solid #f2bd27; }

.stat-content {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
}

.stat-label { font-size: 14px; color: #323233; font-weight: 500; }
.stat-value { font-size: 14px; color: #07c160; font-weight: bold; }

/* 图表区 */
.echart-instance { width: 100%; height: 280px; }

@media (max-width: 900px) { .analysis-grid { grid-template-columns: 1fr; } }

/* 详情抽屉 */
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

/* 弹窗 */
.selection-popup { padding: 16px; }
.selection-title { font-size: 18px; font-weight: 700; color: #1f2937; margin-bottom: 4px; }
.selection-subtitle { font-size: 13px; color: #6b7280; margin-bottom: 10px; }
.selection-grid { max-height: 50vh; overflow: auto; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; padding: 4px; }
.selection-grid .student-card { height: 58px; }
.selection-grid .id-tag { top: 3px; left: 5px; font-size: 11px; }
.selection-grid .name-text { font-size: 14px; }
@media (max-width: 768px) { .selection-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
