import { defineStore } from 'pinia';
import axios from 'axios';

export const useUserStore = defineStore('user', {
  state: () => {
    // 尝试从 localStorage 恢复状态
    const savedState = localStorage.getItem('plant-friend-user-state');
    const initialState = savedState ? JSON.parse(savedState) : null;
    
    return {
      studentId: initialState?.studentId || '',
      studentName: initialState?.studentName || '',
      prePlantPhotos: [], // 不保存图片URL到本地存储，每次重新获取
      currentStage: initialState?.currentStage || '0',
      finalSubmitted: initialState?.finalSubmitted || false  // 是否已提交最终阶段
    };
  },
  
  getters: {
    // 检查是否已领取奖状
    hasFinalSubmitted: (state) => {
      return state.finalSubmitted;
    }
  },
  
  actions: {
    // 恢复完整状态（从后端数据）
    setUserInfo(data) {
      this.studentId = data.student_id;
      this.studentName = data.student_name;

      this.prePlantPhotos = [
        data.pre_plant_1,
        data.pre_plant_2,
        data.pre_plant_3
      ].filter(url => url);

      this.currentStage = '1';
      
      // 保存到本地存储
      this.saveToStorage();
    },
    
    // 切换阶段
    setStage(stage) {
      this.currentStage = stage;
      this.saveToStorage();
    },
    
    // 重置（退出登录）
    async reset() {
      if (this.studentId) {
        try {
          await axios.post('/api/student/stage0/logout', { student_id: this.studentId });
        } catch (e) {}
      }
      this.studentId = '';
      this.studentName = '';
      this.prePlantPhotos = [];
      this.currentStage = '0';
      
      // 清除本地存储
      localStorage.removeItem('plant-friend-user-state');
    },
    
    // 从存储中恢复植物照片（需要在组件中调用）
    async restorePlantPhotos() {
      if (!this.studentId) return;
      
      try {
        // 重新获取学生数据
        const res = await axios.post('/api/student/stage0/login', {
          student_id: this.studentId
        });
        
        if (res.data && res.data.status === 'success') {
          const data = res.data.data;
          this.prePlantPhotos = [
            data.pre_plant_1,
            data.pre_plant_2,
            data.pre_plant_3
          ].filter(url => url);
        }
      } catch (err) {
        console.warn('恢复植物照片失败:', err);
        // 如果无法恢复，保持空数组
      }
    },
    
    // 私有方法：保存状态到 localStorage
    saveToStorage() {
      const stateToSave = {
        studentId: this.studentId,
        studentName: this.studentName,
        currentStage: this.currentStage,
        finalSubmitted: this.finalSubmitted
        // 注意：不保存 prePlantPhotos，因为需要从服务器重新获取
      };
      
      localStorage.setItem('plant-friend-user-state', JSON.stringify(stateToSave));
    },
    
    // 完成所有阶段
    finishAll() {
      this.currentStage = '5';
      this.finalSubmitted = true;
      this.saveToStorage();
    }
  }
});
