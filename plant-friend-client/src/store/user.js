import { defineStore } from 'pinia';
import axios from 'axios';

let heartbeatTimer = null; // 全局心跳定时器

export const useUserStore = defineStore('user', {
  state: () => ({
    studentId: '',
    studentName: '',
    prePhotoUrl: '',
    currentStage: '0'
  }),
  actions: {
    setUserInfo(data) {
      this.studentId = data.student_id;
      this.studentName = data.student_name;
      this.prePhotoUrl = data.pre_photo_url;
      this.currentStage = '1';
      
      this.startHeartbeat(); // 登录成功，开始心脏跳动
    },
    async reset() {
      if (this.studentId) {
        try {
          await axios.post('/api/student/stage0/logout', { student_id: this.studentId });
        } catch (e) {}
      }
      this.studentId = '';
      this.studentName = '';
      this.currentStage = '0';
      
      this.stopHeartbeat(); // 退出登录，心跳停止
    },
    
    // --- 核心机制：隐形心跳 ---
    startHeartbeat() {
      this.stopHeartbeat(); // 防止重复开启
      heartbeatTimer = setInterval(async () => {
        if (!this.studentId) return;
        try {
          // 每 5 秒告诉 Python：我还活着
          await axios.post('/api/student/stage0/heartbeat', { student_id: this.studentId });
        } catch (e) {
          console.warn("心跳发送失败，可能是网络波动");
        }
      }, 5000); 
    },
    stopHeartbeat() {
      if (heartbeatTimer) {
        clearInterval(heartbeatTimer);
        heartbeatTimer = null;
      }
    }
  }
});