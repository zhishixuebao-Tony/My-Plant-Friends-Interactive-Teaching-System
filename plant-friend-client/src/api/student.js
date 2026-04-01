import axios from 'axios';

// 环节0 定义登录接口：发送学号，返回姓名
export const loginApi = (studentId) => {
  return axios.post('/api/student/stage0/login', { 
    student_id: studentId 
  });
};

// 环节1：提交感官自评数据
export const submitSensoryApi = (studentId, checks) => {
  return axios.post('/api/student/stage1/sensory', {
    student_id: studentId,
    checks: checks
  });
};

// 环节2：提交认知自评数据
export async function uploadImageFlow(studentId, moduleName, file) {
  // 1. 获取签名
  const ticketRes = await axios.post('/api/student/get-oss-ticket', {
    student_id: studentId,
    module_name: moduleName,
    file_extension: 'jpg'
  });
  const { upload_url, access_url } = ticketRes.data.data;

  // 2. 直传 OSS (PUT 方法)
  await axios.put(upload_url, file, {
    headers: { 'Content-Type': 'image/jpeg' }
  });

  return access_url; // 返回永久访问地址
}

// 环节3：保存初稿
export const saveDraftApi = (studentId, imgUrl) => {
  return axios.post('/api/student/stage3/save-draft', {
    student_id: studentId,
    img_url: imgUrl
  });
};

// 环节3：提交初稿并请求 AI 评价
export const submitDraftAiApi = (studentId, imgUrl) => {
  // 确保参数类型正确，避免422错误
  const sid = String(studentId || '').trim();
  const url = String(imgUrl || '').trim();
  
  console.log('提交AI评价参数:', { sid, url, original: { studentId, imgUrl } });
  
  return axios.post('/api/ai/stage3/submit-draft-ai', {
    student_id: sid,
    img_url: url
  }).catch(error => {
    console.error('AI评价请求失败:', {
      status: error.response?.status,
      data: error.response?.data,
      config: {
        url: error.config?.url,
        data: error.config?.data
      }
    });
    throw error;
  });
};

// 环节4：完成资源包与习题
export const completeResourceApi = (studentId) => {
  return axios.post('/api/student/stage4/complete-resources', {
    student_id: studentId
  });
};

// 环节5：完成本课程
export const submitFinalApi = (studentId) => {
  return axios.post('/api/student/stage5/final', {
    student_id: String(studentId),
  });
};

// 获取学生信息
export const getStudentInfoApi = (studentId) => {
  return axios.get(`/api/student/student/info/${studentId}`);
};
