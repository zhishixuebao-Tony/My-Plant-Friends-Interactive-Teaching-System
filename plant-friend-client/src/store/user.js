import { defineStore } from 'pinia';
import axios from 'axios';
import { toDisplayImageUrl } from '../utils/imageProxy';
import { DEFAULT_NEXT_BUTTON_CONTROL_STATE } from '../constants/nextButtonControls';

export const useUserStore = defineStore('user', {
  state: () => {
    const savedState = localStorage.getItem('plant-friend-user-state');
    let initialState = null;

    if (savedState) {
      try {
        initialState = JSON.parse(savedState);
      } catch (error) {
        console.warn('Invalid local user state, clearing cache.', error);
        localStorage.removeItem('plant-friend-user-state');
      }
    }

    return {
      studentId: initialState?.studentId || '',
      studentName: initialState?.studentName || '',
      prePlantPhotos: [],
      preRecordCard: initialState?.preRecordCard || '',
      stage1Stars: initialState?.stage1Stars ?? 1,
      stage3Stars: initialState?.stage3Stars ?? 0,
      currentStage: initialState?.currentStage || '0',
      finalSubmitted: initialState?.finalSubmitted || false,
      // 存储用户选择的信息
      sensorySelections: initialState?.sensorySelections || [],
      dimensionSelections: initialState?.dimensionSelections || [],
      nextButtonControls: {
        ...DEFAULT_NEXT_BUTTON_CONTROL_STATE,
        ...(initialState?.nextButtonControls || {}),
      },
    };
  },

  getters: {
    hasFinalSubmitted: (state) => state.finalSubmitted,
  },

  actions: {
    mapStageForDb(stage) {
      const stageText = String(stage);
      if (stageText === '2') return '3';
      if (stageText === '3') return '2';
      return stageText;
    },

    async syncCurrentStage(stage) {
      if (!this.studentId) return;
      try {
        await axios.post('/api/student/stage/sync', {
          student_id: String(this.studentId),
          current_stage: this.mapStageForDb(stage),
        });
      } catch (_) {}
    },

    setUserInfo(data) {
      this.studentId = data.student_id;
      this.studentName = data.student_name;
      this.prePlantPhotos = [data.pre_plant_1, data.pre_plant_2, data.pre_plant_3].map((v) => toDisplayImageUrl(v)).filter(Boolean);
      this.preRecordCard = toDisplayImageUrl(data.pre_record_card || '');
      this.currentStage = 'welcome';
      this.saveToStorage();
      this.syncCurrentStage('welcome');
    },

    setStage(stage) {
      this.currentStage = stage;
      this.saveToStorage();
      this.syncCurrentStage(stage);
    },

    setStage3Stars(stars) {
      this.stage3Stars = Math.max(0, Math.min(2, Number(stars) || 0));
      this.saveToStorage();
    },

    async reset() {
      this.studentId = '';
      this.studentName = '';
      this.prePlantPhotos = [];
      this.preRecordCard = '';
      this.stage1Stars = 1;
      this.stage3Stars = 0;
      this.currentStage = '0';
      this.finalSubmitted = false;
      localStorage.removeItem('plant-friend-user-state');
    },

    async restorePlantPhotos() {
      if (!this.studentId) return;

      try {
        const res = await axios.post('/api/student/stage0/login', {
          student_id: this.studentId,
        });

        if (res.data?.status === 'success') {
          const data = res.data.data;
          this.prePlantPhotos = [data.pre_plant_1, data.pre_plant_2, data.pre_plant_3].map((v) => toDisplayImageUrl(v)).filter(Boolean);
          this.preRecordCard = toDisplayImageUrl(data.pre_record_card || '');
        }
      } catch (err) {
        console.warn('Failed to restore plant photos:', err);
      }
    },

    saveToStorage() {
      const stateToSave = {
        studentId: this.studentId,
        studentName: this.studentName,
        preRecordCard: this.preRecordCard,
        stage1Stars: this.stage1Stars,
        stage3Stars: this.stage3Stars,
        currentStage: this.currentStage,
        finalSubmitted: this.finalSubmitted,
        sensorySelections: this.sensorySelections,
        dimensionSelections: this.dimensionSelections,
        nextButtonControls: this.nextButtonControls,
      };

      localStorage.setItem('plant-friend-user-state', JSON.stringify(stateToSave));
    },

    setSensorySelections(selections) {
      this.sensorySelections = selections;
      this.saveToStorage();
    },

    setDimensionSelections(selections) {
      this.dimensionSelections = selections;
      this.saveToStorage();
    },

    finishAll() {
      this.currentStage = '5';
      this.finalSubmitted = true;
      this.saveToStorage();
      this.syncCurrentStage('5');
    },

    applyNextButtonControlState(controls) {
      this.nextButtonControls = {
        ...DEFAULT_NEXT_BUTTON_CONTROL_STATE,
        ...(controls || {}),
      };
      this.saveToStorage();
    },

    updateOneNextButtonControl(key, enabled) {
      if (!key) return;
      this.nextButtonControls = {
        ...this.nextButtonControls,
        [key]: Boolean(enabled),
      };
      this.saveToStorage();
    },

    isNextButtonEnabled(key) {
      if (!key) return true;
      return Boolean(this.nextButtonControls?.[key]);
    },
  },
});
