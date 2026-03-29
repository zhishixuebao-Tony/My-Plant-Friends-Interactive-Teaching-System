<template>
  <div class="teacher-container">
    <van-nav-bar title="教师端指挥中心 - 实时监控与数据看板" fixed placeholder />

    <div class="main-content">
      
      <!-- 上半部分：学生在线状态矩阵 (50个格子，仅绿/灰两色) -->
      <div class="section-title">全班学生在线状态 (<span class="highlight">{{ stats.online }}</span>/50)</div>
      <div class="matrix-grid">
        <div 
          v-for="student in studentList" 
          :key="student.student_id"
          class="student-card"
          :class="student.is_logged_in ? 's-online' : 's-offline'"
          @click="openDetail(student.student_id)"
        >
          <div class="id-tag">{{ student.student_id }}</div>
          <div class="name-text">{{ student.student_name || '待登入' }}</div>
        </div>
      </div>

      <!-- 下半部分：全班课堂数据统计四大表格 -->
      <div class="section-title" style="margin-top: 40px;">各环节数据实时统计</div>
      <div class="tables-container">
        
        <!-- 表格 1：感官观察统计 (环节1，强制固定顺序) -->
        <div class="data-table-box">
          <div class="table-head">表1：感官观察统计</div>
          <table class="custom-table">
            <thead><tr><th>观察项</th><th>勾选人数</th></tr></thead>
            <tbody>
              <tr><td>👀 看了看</td><td>{{ stats.table1['看了看'] || 0 }} 人</td></tr>
              <tr><td>👃 闻了闻</td><td>{{ stats.table1['闻了闻'] || 0 }} 人</td></tr>
              <tr><td>🤚 摸了摸</td><td>{{ stats.table1['摸了摸'] || 0 }} 人</td></tr>
              <tr><td>👂 听一听</td><td>{{ stats.table1['听一听'] || 0 }} 人</td></tr>
              <tr><td>💭 想一想</td><td>{{ stats.table1['想一想'] || 0 }} 人</td></tr>
            </tbody>
          </table>
        </div>

        <!-- 表格 2：记录卡评价统计 (环节2，强制固定顺序) -->
        <div class="data-table-box">
          <div class="table-head">表2：记录卡评价统计</div>
          <table class="custom-table">
            <thead><tr><th>评价维度</th><th>勾选人数</th></tr></thead>
            <tbody>
              <tr><td>评价一：能真实记录特点</td><td>{{ stats.table2['评价一'] || 0 }} 人</td></tr>
              <tr><td>评价二：能描写出植物感受</td><td>{{ stats.table2['评价二'] || 0 }} 人</td></tr>
              <tr><td>评价三：书写认真工整</td><td>{{ stats.table2['评价三'] || 0 }} 人</td></tr>
            </tbody>
          </table>
        </div>

        <!-- 表格 3：魔法资源包点击热度 & 习题通关 (环节4，强制固定顺序) -->
        <div class="data-table-box">
          <div class="table-head">表3：资源包学习热度</div>
          <table class="custom-table">
            <thead><tr><th>资源名称</th><th>点击次数</th></tr></thead>
            <tbody>
              <tr><td>资源 1</td><td>{{ stats.table3['资源 1'] || 0 }} 次</td></tr>
              <tr><td>资源 2</td><td>{{ stats.table3['资源 2'] || 0 }} 次</td></tr>
              <tr><td>资源 3</td><td>{{ stats.table3['资源 3'] || 0 }} 次</td></tr>
              <tr class="highlight-row" style="background-color: #f6ffed; font-weight: bold;">
                <td style="color: #07c160;">🚩 资源习题通关人数：</td>
                <td style="color: #07c160;">{{ stats.resource_completed }} 人</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 表格 4：AI 批改使用情况 (环节3) -->
        <div class="data-table-box">
          <div class="table-head">表4：AI 批改使用情况</div>
          <div class="ai-stat-circle">
            <van-circle 
              v-model:current-rate="aiCurrentRate" 
              :rate="(stats.table4 / (stats.total || 50)) * 100" 
              size="120px" 
              color="#07c160"
              layer-color="#ebedf0"
              stroke-width="80"
            >
              <div class="circle-text">
                <h2 style="margin:0; font-size:28px;">{{ stats.table4 }}人</h2>
                <p style="margin:5px 0 0; color:#666;">已完成AI评价</p>
              </div>
            </van-circle>
          </div>
        </div>

      </div>
    </div>

    <!-- 弹出抽屉：点击格子查看学生个人详细档案 -->
    <van-popup v-model:show="showDrawer" position="right" :style="{ width: '500px', height: '100%' }">
      <div v-if="detailLoading" class="loading-box">
        <van-loading size="24px" vertical>正在获取该生详细档案...</van-loading>
      </div>
      
      <div v-else-if="activeData" class="detail-panel">
        <van-nav-bar 
          :title="`${activeData.student_id}号 ${activeData.student_name} 的详细档案`" 
          left-text="关闭" 
          @click-left="showDrawer = false" 
        />
        
        <div class="scroll-body">
          <!-- 任务完成状态 -->
          <van-divider>通关进度状态</van-divider>
          <van-cell-group inset>
            <van-cell title="环节3: AI 作文评价" :value="activeData.has_completed_ai ? '已完成 ✅' : '未完成 ❌'" />
            <van-cell title="环节4: 资源包与习题" :value="activeData.has_viewed_resources ? '已完成 ✅' : '未完成 ❌'" />
          </van-cell-group>

          <!-- 核心图片存档 -->
          <van-divider>作品图片存档</van-divider>
          <div class="img-group">
            <div class="img-item">
              <p>课前预置照片</p>
              <van-image :src="activeData.pre_photo_url" fit="cover" lazy-load @click="preview(activeData.pre_photo_url)">
                <template #error>未获取</template>
              </van-image>
            </div>
            <div class="img-item">
              <p>修改后的记录卡</p>
              <van-image :src="activeData.record_card_img" fit="cover" lazy-load @click="preview(activeData.record_card_img)">
                <template #error>未上传</template>
              </van-image>
            </div>
            <div class="img-item">
              <p>习作初稿</p>
              <van-image :src="activeData.draft_img" fit="cover" lazy-load @click="preview(activeData.draft_img)">
                <template #error>未上传</template>
              </van-image>
            </div>
            <div class="img-item">
              <p>定稿作文</p>
              <van-image :src="activeData.final_img" fit="cover" lazy-load @click="preview(activeData.final_img)">
                <template #error>未上传</template>
              </van-image>
            </div>
          </div>

          <!-- AI 评语展示 -->
          <van-divider>AI 老师评语</van-divider>
          <div class="ai-comment">
            {{ activeData.ai_feedback_text || '尚未生成评语' }}
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { showImagePreview, showToast } from 'vant';

const studentList = ref([]);
const stats = ref({
  online: 0,
  total: 50,
  table1: {},
  table2: {},
  table3: {},
  table4: 0,
  resource_completed: 0
});
const aiCurrentRate = ref(0);

const showDrawer = ref(false);
const activeData = ref(null);
const detailLoading = ref(false);

const socket = new WebSocket('wss://f2d9f8f.r35.cpolar.top/ws/stats');

socket.onopen = () => {
  console.log('✅ 穿透环境 WebSocket 连接成功');
};

let pollTimer = null;

// --- 核心：自动轮询大屏数据 (每 3 秒绝对刷新一次) ---
const fetchDashboardData = async () => {
  try {
    const res = await axios.get('/api/teacher/dashboard/statistics');
    studentList.value = res.data.students_list; 
    
    stats.value = {
      online: res.data.logged_in_count,
      total: res.data.total_students,
      table1: res.data.table1_sensory || {},
      table2: res.data.table2_dimension || {},
      table3: res.data.table3_resource || {},
      table4: res.data.table4_ai_count || 0,
      // 【关键修复】确保 res.data 里的字段名和 stats 里的字段名完全一致
      resource_completed: res.data.resource_completed_count || 0 
    };
  } catch (err) {
    console.error("刷新大屏失败:", err);
  }
};

// 获取学生详情
const openDetail = async (studentId) => {
  showDrawer.value = true;
  detailLoading.value = true;
  try {
    const res = await axios.get(`/api/teacher/dashboard/student-detail/${studentId}`);
    activeData.value = res.data;
  } catch (err) {
    showToast('获取该生详情失败');
    showDrawer.value = false;
  } finally {
    detailLoading.value = false;
  }
};

const preview = (url) => {
  if (url) showImagePreview([url]);
};

// 页面加载完毕即开启轮询
onMounted(() => {
  fetchDashboardData(); // 马上加载第一次
  pollTimer = setInterval(fetchDashboardData, 3000); // 启动 3 秒轮询
});

// 页面销毁时清除定时器，防止内存泄漏
onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});
</script>

<style scoped>
.teacher-container { min-height: 100vh; background-color: #f0f2f5; padding-bottom: 50px; }
.main-content { padding: 20px; }

.section-title { font-size: 20px; font-weight: bold; color: #333; margin-bottom: 20px; border-left: 5px solid #07c160; padding-left: 10px; }
.highlight { color: #07c160; font-size: 24px; }

/* 矩阵区：仅区分在线(绿)和离线(灰) */
.matrix-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 12px; }
.student-card {
  height: 60px; border-radius: 6px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; position: relative; cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: transform 0.1s;
}
.student-card:active { transform: scale(0.95); }

.s-online { background-color: #e6ffed; border: 1px solid #b7eb8f; color: #237804; }
.s-offline { background-color: #f5f5f5; border: 1px solid #d9d9d9; color: #999; }

.id-tag { position: absolute; top: 4px; left: 6px; font-size: 12px; font-weight: bold; opacity: 0.8; }
.name-text { font-size: 16px; font-weight: bold; margin-top: 5px; }

/* 四大数据表格区 */
.tables-container { display: flex; gap: 20px; flex-wrap: wrap; }
.data-table-box { flex: 1; min-width: 250px; background: #fff; border-radius: 8px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.table-head { font-weight: bold; font-size: 16px; margin-bottom: 15px; color: #333; text-align: center; }

.custom-table { width: 100%; border-collapse: collapse; text-align: left; }
.custom-table th, .custom-table td { padding: 12px 10px; border-bottom: 1px solid #f0f0f0; }
.custom-table th { background: #fafafa; color: #666; font-weight: normal; }
.custom-table td { color: #333; font-weight: 500; }
.highlight-row td { background-color: #f6ffed; } /* 资源包完成人数高亮 */

.ai-stat-circle { display: flex; justify-content: center; padding: 20px 0; align-items: center; height: 100%; }

/* 详情抽屉区 */
.loading-box { height: 100%; display: flex; justify-content: center; align-items: center; }
.scroll-body { padding: 20px; overflow-y: auto; height: calc(100vh - 46px); background: #f7f8fa; }
.img-group { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.img-item { background: #fff; padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.img-item p { margin: 0 0 8px 0; font-size: 14px; font-weight: bold; color: #555; }
.img-item .van-image { width: 100%; height: 180px; border-radius: 4px; overflow: hidden; background: #eee; cursor: pointer; }
.ai-comment { background: #fffbe6; padding: 15px; border-radius: 8px; line-height: 1.6; color: #d48806; border-left: 4px solid #ffe58f; font-size: 15px; }
</style>