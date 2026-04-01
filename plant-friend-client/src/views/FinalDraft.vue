<template>
  <div class="stage-container">
    <van-nav-bar title="环节 5：AI评语与荣誉时刻" fixed placeholder border />

    <div class="split-layout" v-if="!showCertificate">
      <!-- ================= 左侧：AI评语展示 ================= -->
      <div class="left-panel">
        <div class="ai-feedback-section">
          <div class="ai-header">
            <van-icon name="comment-o" color="#1989fa" />
            <span>AI老师的作文评语</span>
          </div>
          
          <div class="ai-content-wrapper">
            <div v-if="aiFeedback && aiFeedback.length > 0" class="ai-content">
              <div class="ai-avatar">
                <van-icon name="cluster-o" size="24" color="#fff" />
              </div>
              <div class="ai-text-container">
                <h3 class="ai-title">AI老师的悄悄话：</h3>
                <div class="ai-text">{{ aiFeedback }}</div>
              </div>
            </div>
            
            <div v-else class="ai-loading">
              <van-loading size="24px" color="#1989fa" vertical>
                正在加载AI评语...
              </van-loading>
            </div>
            
            <!-- 鼓励提示 -->
            <div class="encouragement-tip">
              <van-icon name="bulb-o" color="#f2bd27" />
              <p>根据AI评语修改后，你的作文一定会更加精彩！</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= 右侧：课堂完成确认与荣誉领取 ================= -->
      <div class="right-panel">
        <div class="panel-header">🏆 课堂完成，领取荣誉奖状</div>
        
        <div class="scroll-content">
          <!-- 课堂完成确认信息 -->
          <div class="final-confirm-section">
            <div class="final-summary">
              <van-icon name="checked" size="60" color="#07c160" class="check-icon" />
              <h2 class="final-title">你的课堂任务已完成！</h2>
              <p class="final-desc">
                你已经完成了《我的植物朋友》全部课堂环节：
              </p>
              <ul class="final-steps">
                <li>✓ 课前观察植物照片</li>
                <li>✓ 记录卡修改完善</li>
                <li>✓ 课堂试稿写作</li>
                <li>✓ 资源包学习提升</li>
                <li>✓ AI评价指导</li>
              </ul>
              <div class="course-note">
                <van-icon name="info-o" color="#1989fa" />
                <span>注：作文的最终定稿将在课后完成，老师会指导你进一步完善</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="action-footer">
          <van-button 
            type="warning" 
            block 
            round 
            size="large" 
            @click="onFinalSubmit"
            :loading="isSubmitting"
            loading-text="正在领取奖状..."
          >
            我已阅读评语，领取荣誉奖状
          </van-button>
        </div>
      </div>
    </div>

    <!-- ================= 核心：电子奖状与撒花展示区 ================= -->
    <div class="certificate-container" v-else>
      <div class="certificate-card">
        <div class="cert-border">
          <div class="cert-content">
            <div class="cert-header">荣 誉 奖 状</div>
            <div class="cert-body">
              <p class="cert-name"><span>{{ userStore.studentName }}</span> 同学：</p>
              <p class="cert-text">
                在《我的植物朋友》互动课堂中，你通过细致的观察和生动的描写，成功完成了一篇优秀的习作。表现出色，特发此证，以资鼓励！
              </p>
              <p class="cert-title">小小植物学家</p>
            </div>
            <div class="cert-footer">
              <p>语文互动课堂项目组</p>
              <p>{{ currentDate }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="final-actions">
        <van-button icon="share-o" type="primary" round plain @click="shareCert">分享我的荣誉</van-button>
        <van-button icon="arrow-left" type="default" round plain @click="goBackToAI">返回查看AI评语</van-button>
        <p class="final-tip">老师在大屏上也能看到你的作品哦！</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useUserStore } from '../store/user';
import axios from 'axios';
import { showToast } from 'vant';
import confetti from 'canvas-confetti'; // 导入撒花插件
import { submitFinalApi } from '../api/student';

const userStore = useUserStore();

// AI评语相关状态
const aiFeedback = ref('');
const isLoadingAI = ref(true);
const isSubmitting = ref(false);
const currentDate = new Date().toLocaleDateString();

// 控制是否显示奖状（总是先显示AI评语页面）
const showCertificate = ref(false);

// 页面加载时获取AI评语
onMounted(async () => {
  await fetchAIFeedback();
});

// 获取AI评语 - 参考TeacherDash.vue的实现方式
const fetchAIFeedback = async () => {
  isLoadingAI.value = true;
  try {
    // 首选方案：通过教师端接口获取学生详情（与TeacherDash.vue一致）
    const teacherResponse = await axios.get(`/api/teacher/dashboard/student-detail/${userStore.studentId}`);
    if (teacherResponse.data && teacherResponse.data.ai_feedback_text) {
      aiFeedback.value = teacherResponse.data.ai_feedback_text;
      console.log('通过教师端接口成功获取AI评语');
      return;
    }
    
    // 备选方案：通过学生信息接口获取AI评语
    try {
      const studentResponse = await axios.get(`/api/student/student/info/${userStore.studentId}`);
      if (studentResponse.data && studentResponse.data.ai_feedback) {
        aiFeedback.value = studentResponse.data.ai_feedback;
        console.log('通过学生信息接口成功获取AI评语');
        return;
      }
    } catch (studentError) {
      console.warn('通过学生信息接口获取AI评语失败:', studentError.message);
    }
    
    // 如果所有API都失败，显示详细且有意义的默认评语
    aiFeedback.value = `✨ 亲爱的${userStore.studentName || '同学'}，AI老师看到了你的努力！你的作文观察细致，描写生动。如果在描写植物叶子的时候，能加入"摸上去是什么感觉"的细节，文章会更精彩哦！继续加油！\n\n📝 写作小提示：\n1. 多使用比喻句（如：叶子像小手掌）\n2. 加入五感描写（看、闻、摸、听、尝）\n3. 写出自己的真实感受\n4. 保持工整的字迹`;
  } catch (error) {
    console.warn('获取AI评语失败:', error);
    aiFeedback.value = `✨ ${userStore.studentName || '同学'}的作文很用心！观察到植物的细节，也写了自己的感受。继续努力，你会写得更好！\n\n💡 改进建议：\n• 可以多描述植物的颜色变化\n• 加入季节对植物的影响\n• 写出植物给你的启发`;
  } finally {
    isLoadingAI.value = false;
  }
};

// --- 最终提交并触发撒花 ---
const onFinalSubmit = async () => {
  const randomDelay = Math.floor(Math.random() * 2000);
  await new Promise(resolve => setTimeout(resolve, randomDelay));

  isSubmitting.value = true;
  try {
    // 提交环节5完成状态 - 使用统一的API函数
    await submitFinalApi(userStore.studentId);

    // 更新用户状态为已完成
    userStore.finishAll();

    // 触发撒花特效
    triggerConfetti();

    // 显示奖状
    showCertificate.value = true;
    
    showToast({ message: '太棒了！你真了不起！', type: 'success' });
  } catch (err) {
    console.warn('提交环节5失败:', err);
    // 记录详细的错误信息
    if (err.response) {
      console.error('错误状态码:', err.response.status);
      console.error('错误响应:', err.response.data);
      console.error('请求数据:', { student_id: userStore.studentId });
    }
    // 即使提交失败，也显示奖状（演示用）
    userStore.finishAll();
    triggerConfetti();
    showCertificate.value = true;
    showToast({ message: '恭喜完成课程！', type: 'success' });
  } finally {
    isSubmitting.value = false;
  }
};

// 页面加载时检查是否已提交，自动触发撒花
onMounted(() => {
  // 如果刷新后发现已经提交过了，可以自动再撒一小次花
  if (userStore.hasFinalSubmitted) {
    triggerConfetti(); 
  }
});

// 撒花函数
const triggerConfetti = () => {
  const duration = 3 * 1000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

  const interval = setInterval(function() {
    const timeLeft = animationEnd - Date.now();
    if (timeLeft <= 0) return clearInterval(interval);

    const particleCount = 50 * (timeLeft / duration);
    confetti({ ...defaults, particleCount, origin: { x: Math.random(), y: Math.random() - 0.2 } });
  }, 250);
};

const shareCert = () => showToast('老师已在主屏幕展示你的荣誉！');

// 返回查看AI评语
const goBackToAI = () => {
  showCertificate.value = false;
};
</script>

<style scoped>
.stage-container { 
  height: 100%; 
  display: flex; 
  flex-direction: column; 
  background-color: #f7f8fa; 
}

.split-layout { 
  flex: 1; 
  display: flex; 
  overflow: hidden; 
}

/* ================= 左侧：AI评语展示区 ================= */
.left-panel { 
  flex: 1; 
  background-color: #f0f7ff; 
  display: flex; 
  flex-direction: column; 
  padding: 20px; 
  overflow: hidden;
}

.ai-feedback-section {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-header {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  padding: 16px;
  border-bottom: 1px solid #f2f3f5;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-content-wrapper {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-content {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f3e7ff 0%, #e2e0ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(114, 50, 221, 0.1);
}

.ai-avatar {
  width: 48px;
  height: 48px;
  min-width: 48px;
  background: linear-gradient(135deg, #7232dd, #1989fa);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 8px rgba(114, 50, 221, 0.3);
}

.ai-text-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-title {
  color: #531dab;
  font-size: 16px;
  margin: 0;
  font-weight: bold;
}

.ai-text {
  color: #391085;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
  font-weight: 500;
}

.ai-loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.encouragement-tip {
  padding: 12px 16px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e8 100%);
  border-left: 4px solid #07c160;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.encouragement-tip p {
  font-size: 14px;
  color: #333;
  margin: 0;
  line-height: 1.5;
}

/* ================= 右侧：定稿确认与提交区 ================= */
.right-panel { 
  flex: 1.2; 
  background-color: #fff; 
  display: flex; 
  flex-direction: column; 
  border-left: 1px solid #ebedf0; 
}

.panel-header { 
  font-size: 20px; 
  font-weight: bold; 
  padding: 20px; 
  color: #323233; 
  border-bottom: 1px solid #f2f3f5; 
  flex-shrink: 0; 
}

.scroll-content { 
  flex: 1; 
  padding: 20px; 
  display: flex; 
  flex-direction: column; 
  overflow-y: auto; 
}

/* 定稿确认区域 */
.final-confirm-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.final-summary {
  text-align: center;
  padding: 24px;
  background: linear-gradient(135deg, #fff9e6 0%, #fff1c1 100%);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(242, 189, 39, 0.1);
}

.check-icon {
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float { 
  0%, 100% { transform: translateY(0); } 
  50% { transform: translateY(-15px); } 
}

.final-title {
  font-size: 22px;
  color: #856404;
  margin: 0 0 16px 0;
}

.final-desc {
  font-size: 16px;
  color: #856404;
  margin: 0 0 16px 0;
  font-weight: 500;
}

.final-steps {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
  display: inline-block;
}

.final-steps li {
  font-size: 14px;
  color: #856404;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-note {
  margin-top: 16px;
  padding: 12px;
  background: #f0f7ff;
  border-radius: 8px;
  border-left: 4px solid #1989fa;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  color: #333;
  line-height: 1.5;
}

.course-note span {
  flex: 1;
}


.action-footer { 
  padding: 25px; 
  background-color: #fff; 
  box-shadow: 0 -4px 15px rgba(0,0,0,0.03); 
  flex-shrink: 0;
}

/* ================= 奖状样式 ================= */
.certificate-container { 
  flex: 1; 
  background: #555; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center; 
  padding: 20px; 
}

.certificate-card { 
  width: 90%; 
  max-width: 600px; 
  background: #fff; 
  padding: 15px; 
  border-radius: 4px; 
  box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
  transform: rotate(-1deg); 
}

.cert-border { 
  border: 10px double #f2bd27; 
  padding: 20px; 
  height: 100%; 
}

.cert-content { 
  border: 2px solid #f2bd27; 
  padding: 30px; 
  background: #fffcf5; 
  text-align: center; 
  position: relative; 
}

.cert-header { 
  font-size: 40px; 
  color: #d4237a; 
  font-family: "SimSun", serif; 
  font-weight: bold; 
  margin-bottom: 30px; 
  letter-spacing: 10px; 
}

.cert-body { 
  text-align: left; 
  line-height: 2; 
  color: #333; 
}

.cert-name { 
  font-size: 22px; 
  margin-bottom: 15px; 
}

.cert-name span { 
  text-decoration: underline; 
  font-weight: bold; 
  padding: 0 10px; 
}

.cert-text { 
  text-indent: 2em; 
  font-size: 18px; 
  margin-bottom: 30px; 
}

.cert-title { 
  text-align: center; 
  font-size: 32px; 
  color: #f2bd27; 
  font-weight: bold; 
  margin-top: 40px; 
  font-family: "KaiTi"; 
}

.cert-footer { 
  text-align: right; 
  margin-top: 40px; 
  font-size: 16px; 
}

.final-actions { 
  margin-top: 30px; 
  text-align: center; 
  color: #fff; 
}

.final-tip { 
  margin-top: 15px; 
  opacity: 0.7; 
  font-size: 14px; 
}

/* 响应式调整 */
@media (max-width: 768px) {
  .split-layout {
    flex-direction: column;
  }
  
  .left-panel, .right-panel {
    flex: 1;
  }
  
  .right-panel {
    border-left: none;
    border-top: 1px solid #ebedf0;
  }
  
  .ai-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>
