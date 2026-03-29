<template>
  <div class="teacher-container">
    <van-nav-bar title="👨‍🏫 教师指挥中心 - 实时监控与数据看板" fixed placeholder />

    <div class="main-content">
      
      <!-- 上半部分：学生在线状态矩阵 -->
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
          <div v-if="student.final_img" class="medal-icon">🏆</div>
        </div>
      </div>

      <!-- 下半部分：四大表格 (保持不变) -->
      <div class="section-title" style="margin-top: 40px;">各环节数据实时统计</div>
      <div class="tables-container">
        
        <div class="data-table-box">
          <div class="table-head">表1：感官观察统计 (环节1)</div>
          <table class="custom-table">
            <thead><tr><th>观察项</th><th>勾选人数</th></tr></thead>
            <tbody>
              <tr><td>👀看了看</td><td>{{ stats.table1['看了看'] || 0 }} 人</td></tr>
              <tr><td>👃闻了闻</td><td>{{ stats.table1['闻了闻'] || 0 }} 人</td></tr>
              <tr><td>🤚摸了摸</td><td>{{ stats.table1['摸了摸'] || 0 }} 人</td></tr>
              <tr><td>👂听一听</td><td>{{ stats.table1['听一听'] || 0 }} 人</td></tr>
              <tr><td>👅尝了尝</td><td>{{ stats.table1['尝了尝'] || 0 }} 人</td></tr>
            </tbody>
          </table>
        </div>

        <div class="data-table-box">
          <div class="table-head">表2：记录卡自评统计 (环节2)</div>
          <table class="custom-table">
            <thead><tr><th>评价维度</th><th>勾选人数</th></tr></thead>
            <tbody>
              <tr><td>真实记录特点</td><td>{{ stats.table2['评价一：能真实记录植物特点'] || stats.table2['评价一'] || 0 }} 人</td></tr>
              <tr><td>描写出感受</td><td>{{ stats.table2['评价二：能描写出自己的感受'] || stats.table2['评价二'] || 0 }} 人</td></tr>
              <tr><td>书写认真工整</td><td>{{ stats.table2['评价三：书写认真、字迹工整'] || stats.table2['评价三'] || 0 }} 人</td></tr>
            </tbody>
          </table>
        </div>

        <div class="data-table-box">
          <div class="table-head">表3：资源包学习热度 (环节4)</div>
          <table class="custom-table">
            <thead><tr><th>资源名称</th><th>点击次数</th></tr></thead>
            <tbody>
              <tr><td>资源 1</td><td>{{ stats.table3['资源 1'] || 0 }} 次</td></tr>
              <tr><td>资源 2</td><td>{{ stats.table3['资源 2'] || 0 }} 次</td></tr>
              <tr><td>资源 3</td><td>{{ stats.table3['资源 3'] || 0 }} 次</td></tr>
              <tr class="highlight-row">
                <td style="color: #07c160;">🚩 习题通关人数：</td>
                <td style="color: #07c160; font-weight: bold; font-size: 16px;">{{ stats.resource_completed }} 人</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="data-table-box">
          <div class="table-head">表4：AI 批改覆盖率 (环节3)</div>
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

    <!-- 弹出抽屉：学生详细档案 -->
    <van-popup v-model:show="showDrawer" position="right" :style="{ width: '550px', height: '100%' }">
      <div v-if="detailLoading" class="loading-box">
        <van-loading size="24px" vertical>正在调取该生详细档案...</van-loading>
      </div>
      
      <div v-else-if="activeData" class="detail-panel">
        <van-nav-bar 
          :title="`🧑‍🎓 ${activeData.student_id}号 ${activeData.student_name} 的档案`" 
          left-text="关闭" 
          @click-left="showDrawer = false" 
          fixed placeholder border
        />
        
        <div class="scroll-body">
          
          <!-- ================= 核心修复：课前素材与视频区 ================= -->
          <div class="module-title">🌿 课前准备：植物照片与视频</div>
          <div class="pre-media-box">
            <!-- 3张照片 -->
            <div class="plant-photos" v-if="activeData.pre_plant_1 || activeData.pre_plant_2 || activeData.pre_plant_3">
              <van-image v-if="activeData.pre_plant_1" :src="activeData.pre_plant_1" fit="cover" class="p-img" @click="preview(activeData.pre_plant_1)" />
              <van-image v-if="activeData.pre_plant_2" :src="activeData.pre_plant_2" fit="cover" class="p-img" @click="preview(activeData.pre_plant_2)" />
              <van-image v-if="activeData.pre_plant_3" :src="activeData.pre_plant_3" fit="cover" class="p-img" @click="preview(activeData.pre_plant_3)" />
            </div>
            <div v-else class="empty-text">该生暂无预置植物照片</div>

            <!-- 课前视频播放按钮 -->
            <div class="t-video-btn" v-if="activeData.pre_video" @click="showVideoModal = true">
              <van-icon name="play-circle" size="24" color="#fff" />
              <span>播放课前观察视频</span>
            </div>
          </div>

          <!-- ================= 核心修复：记录卡与写作成长轨迹 ================= -->
          <div class="module-title" style="margin-top: 25px;">📈 写作流程档案</div>
          <div class="img-group">
            <div class="img-item">
              <div class="item-tag">1. 课前原始记录卡</div>
              <van-image :src="activeData.pre_record_card" fit="contain" lazy-load @click="preview(activeData.pre_record_card)">
                <template #error>未获取</template>
              </van-image>
            </div>
            <div class="img-item">
              <div class="item-tag highlight-tag">2. 课中修改后记录卡</div>
              <van-image :src="activeData.record_card_img" fit="contain" lazy-load @click="preview(activeData.record_card_img)">
                <template #error>未上传</template>
              </van-image>
            </div>
            <div class="img-item">
              <div class="item-tag">3. 习作初稿</div>
              <van-image :src="activeData.draft_img" fit="cover" lazy-load @click="preview(activeData.draft_img)">
                <template #error>未上传</template>
              </van-image>
            </div>
            <div class="img-item">
              <div class="item-tag highlight-tag">4. 最终定稿</div>
              <van-image :src="activeData.final_img" fit="cover" lazy-load @click="preview(activeData.final_img)">
                <template #error>未上传</template>
              </van-image>
            </div>
          </div>

          <!-- 通关与 AI 状态 -->
          <div class="module-title" style="margin-top: 25px;">🤖 AI 评语与通关状态</div>
          <van-cell-group inset style="margin: 0 0 15px 0; border: 1px solid #ebedf0;">
            <van-cell title="资源包与习题通关" :value="activeData.has_viewed_resources ? '已完成 ✅' : '未完成 ❌'" />
          </van-cell-group>
          
          <div class="ai-comment">
            <div class="ai-title">AI 老师专属评语：</div>
            <div class="ai-text">{{ activeData.ai_feedback_text || '该生尚未提交初稿进行 AI 批改' }}</div>
          </div>

        </div>
      </div>
    </van-popup>

    <!-- ================= 教师端专属：视频播放弹窗 ================= -->
    <van-popup 
      v-model:show="showVideoModal" 
      closeable 
      round 
      class="video-popup"
      @closed="onVideoClose"
      teleport="body"
    >
      <div class="popup-header">课前观察视频</div>
      <video
        ref="videoPlayer"
        :src="activeData?.pre_video"
        controls
        playsinline
        preload="metadata"
        class="full-video"
      ></video>
    </van-popup>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { showImagePreview, showToast } from 'vant';

const studentList = ref([]);
const stats = ref({
  online: 0, total: 50,
  table1: {}, table2: {}, table3: {},
  table4: 0, resource_completed: 0
});
const aiCurrentRate = ref(0);

const showDrawer = ref(false);
const activeData = ref(null);
const detailLoading = ref(false);

// 视频弹窗控制
const showVideoModal = ref(false);
const videoPlayer = ref(null);

// ================= 核心：拉取大屏数据 =================
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
      resource_completed: res.data.resource_completed_count || 0 
    };
  } catch (err) {
    console.error("刷新大屏失败:", err);
  }
};

// ================= 工业级 WebSocket (带断线重连) =================
const getWsUrl = () => {
  const base = axios.defaults.baseURL || window.location.origin;
  if (base.startsWith('https')) {
    return base.replace(/^https/, 'wss') + '/ws/stats';
  } else if (base.startsWith('http')) {
    return base.replace(/^http/, 'ws') + '/ws/stats';
  }
  return 'ws://127.0.0.1:8000/ws/stats'; // 终极保底地址
};

const wsURL = getWsUrl();
let socket = null;
let reconnectTimer = null;

const initWebSocket = () => {
  console.log('🔄 正在尝试连接 WebSocket:', wsURL); // 打印出来看看地址对不对
  socket = new WebSocket(wsURL);
  
  socket.onopen = () => {
    console.log('✅ 大屏 WebSocket 实时通道已连接！(现在可以秒刷了)');
    if (reconnectTimer) clearInterval(reconnectTimer); 
  };
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.action === 'REFRESH_DASHBOARD') {
      console.log('📡 收到学生提交信号，瞬间刷新大屏！');
      fetchDashboardData();
    }
  };

  socket.onclose = () => {
    console.warn('❌ WebSocket 断开，3秒后重连...');
    reconnectTimer = setTimeout(initWebSocket, 3000);
  };

  socket.onerror = (err) => {
    console.error('WebSocket 发生错误，准备重连');
    socket.close(); 
  };
};

// ================= 详情抽屉控制 =================
const openDetail = async (studentId) => {
  showDrawer.value = true;
  detailLoading.value = true;
  try {
    const res = await axios.get(`/api/teacher/dashboard/student-detail/${studentId}`);
    activeData.value = res.data;
  } catch (err) {
    showToast('获取档案失败');
    showDrawer.value = false;
  } finally {
    detailLoading.value = false;
  }
};

// ================= 核心修复：图片预览防卡死机制 =================
const preview = (url) => {
  if (!url) return;
  showImagePreview({
    images: [url],
    closeable: true,
    closeOnClickOverlay: true,
    teleport: 'body' 
  });
};

const onVideoClose = () => {
  if (videoPlayer.value) {
    videoPlayer.value.pause();
  }
};

// ================= 生命周期管理 =================
let pollTimer = null;

onMounted(() => {
  fetchDashboardData(); 
  initWebSocket(); 
  
  //轮询为 1 分钟 (60000 毫秒) 作为兜底保底
  pollTimer = setInterval(fetchDashboardData, 60000); 
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
  if (socket) {
    socket.onclose = null; 
    socket.close();
  }
});
</script>

<style scoped>
.teacher-container { min-height: 100vh; background-color: #f2f3f5; padding-bottom: 50px; }
.main-content { padding: 25px; }

.section-title { font-size: 20px; font-weight: bold; color: #333; margin-bottom: 20px; border-left: 5px solid #07c160; padding-left: 12px; }
.highlight { color: #07c160; font-size: 26px; }

/* 矩阵区 */
.matrix-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 15px; }
.student-card {
  height: 65px; border-radius: 8px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; position: relative; cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: transform 0.15s;
}
.student-card:active { transform: scale(0.95); }

.s-online { background-color: #eafaf1; border: 1px solid #8ce6b0; color: #1e8e3e; }
.s-offline { background-color: #fff; border: 1px solid #dcdee0; color: #969799; }

.id-tag { position: absolute; top: 4px; left: 6px; font-size: 12px; font-weight: bold; background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 4px; }
.name-text { font-size: 16px; font-weight: bold; margin-top: 8px; }
.medal-icon { position: absolute; top: -8px; right: -6px; font-size: 18px; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.2)); }

/* 数据表格区 */
.tables-container { display: flex; gap: 20px; flex-wrap: wrap; }
.data-table-box { flex: 1; min-width: 250px; background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); border-top: 4px solid #07c160; }
.table-head { font-weight: bold; font-size: 17px; margin-bottom: 15px; color: #333; text-align: center; }

.custom-table { width: 100%; border-collapse: collapse; text-align: left; }
.custom-table th, .custom-table td { padding: 12px 10px; border-bottom: 1px dashed #ebedf0; }
.custom-table th { color: #969799; font-weight: normal; font-size: 14px; }
.custom-table td { color: #323233; font-weight: 500; }
.highlight-row td { background-color: #f0f9eb; } 

.ai-stat-circle { display: flex; justify-content: center; padding: 10px 0; align-items: center; }

/* 详情抽屉区 */
.loading-box { height: 100%; display: flex; justify-content: center; align-items: center; }
.scroll-body { padding: 20px; overflow-y: auto; height: calc(100vh - 46px); background: #f7f8fa; }

.module-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 15px; padding-left: 5px; border-left: 4px solid #1989fa; }

/* 课前素材区 */
.pre-media-box { background: #fff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.plant-photos { display: flex; gap: 10px; margin-bottom: 15px; }
.p-img { flex: 1; height: 110px; border-radius: 8px; overflow: hidden; border: 1px solid #ebedf0; cursor: pointer; }
.empty-text { font-size: 13px; color: #999; text-align: center; padding: 20px; }

/* 新增：视频播放按钮 */
.t-video-btn {
  background: linear-gradient(90deg, #323233, #4b4b4b);
  color: #fff; padding: 12px; border-radius: 8px; display: flex; justify-content: center; align-items: center; gap: 10px;
  cursor: pointer; font-size: 15px; transition: transform 0.1s;
}
.t-video-btn:active { transform: scale(0.98); }

.img-group { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.img-item { background: #fff; padding: 12px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.item-tag { font-size: 13px; font-weight: bold; color: #666; margin-bottom: 10px; text-align: center; }
.highlight-tag { color: #07c160; }
.img-item .van-image { width: 100%; height: 160px; border-radius: 8px; overflow: hidden; background: #f2f3f5; cursor: pointer; border: 1px solid #f0f0f0; }

.ai-comment { background: #fffbe6; padding: 20px; border-radius: 12px; border: 1px solid #ffe58f; }
.ai-title { font-weight: bold; color: #d48806; margin-bottom: 10px; }
.ai-text { line-height: 1.6; color: #ad6800; font-size: 15px; white-space: pre-wrap; }

/* 视频弹窗 */
.video-popup { width: 90%; max-width: 500px; background: #000; border-radius: 16px; overflow: hidden; }
.popup-header { text-align: center; font-size: 16px; color: #fff; padding: 16px; background: #222; }
.full-video { width: 100%; max-height: 70vh; display: block; }
</style>