import axios from 'axios';

export const loginApi = (studentId) => {
  return axios.post('/api/student/stage0/login', {
    student_id: studentId,
  });
};

export const submitSensoryApi = (studentId, checks) => {
  return axios.post('/api/student/stage1/sensory', {
    student_id: studentId,
    checks,
  });
};

export const completeResourceApi = (studentId) => {
  return axios.post('/api/student/stage4/complete-resources', {
    student_id: studentId,
  });
};

export const submitFinalApi = (studentId) => {
  return axios.post('/api/student/stage5/final', {
    student_id: String(studentId),
  });
};

export const getStudentInfoApi = (studentId) => {
  return axios.get(`/api/student/student/info/${studentId}`);
};
