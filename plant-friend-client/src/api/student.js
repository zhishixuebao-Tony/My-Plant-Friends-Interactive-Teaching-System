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

export const uploadImageFlow = async (studentId, moduleName, file) => {
  const ticketRes = await axios.post('/api/student/get-oss-ticket', {
    student_id: studentId,
    module_name: moduleName,
    file_extension: 'jpg',
  });

  const { upload_url, access_url } = ticketRes.data.data;

  await axios.put(upload_url, file, {
    headers: { 'Content-Type': 'image/jpeg' },
  });

  return access_url;
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
