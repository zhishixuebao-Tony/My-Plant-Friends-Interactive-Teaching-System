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

// 环节3：提交初稿并请求 AI 评价
export const submitDraftAiApi = (studentId, imgUrl) => {
  return axios.post('/api/ai/stage3/submit-draft-and-ai', {
    student_id: studentId,
    draft_img_url: imgUrl
  });
};

// 环节4：完成资源包与习题
export const completeResourceApi = (studentId) => {
  return axios.post('/api/student/stage4/complete-resources', {
    student_id: studentId
  });
};

// 环节5：提交最终定稿照片
export const submitFinalApi = (studentId, imgUrl) => {
  return axios.post('/api/student/stage5/final', {
    student_id: studentId,
    img_url: imgUrl
  });
};