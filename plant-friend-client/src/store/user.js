import { defineStore } from 'pinia';
import axios from 'axios';

export const useUserStore = defineStore('user', {
  state: () => ({
    studentId: '',
    studentName: '',
    prePlantPhotos: [], 
    currentStage: '0'
  }),
  actions: {
    setUserInfo(data) {
      this.studentId = data.student_id;
      this.studentName = data.student_name;

      this.prePlantPhotos = [
        data.pre_plant_1,
        data.pre_plant_2,
        data.pre_plant_3
      ].filter(url => url);

      this.currentStage = '1';
      
    },
    setStage(stage) {
      this.currentStage = stage;
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
    },
  }
});