export const toDisplayImageUrl = (url) => {
  const raw = String(url || '').trim();
  if (!raw) return '';

  if (/^https?:\/\/[^\s]*aliyuncs\.com/i.test(raw)) {
    return `/api/student/proxy-image?url=${encodeURIComponent(raw)}`;
  }

  return raw;
};
