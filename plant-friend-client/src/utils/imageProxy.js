export const toDisplayImageUrl = (url) => {
  const raw = String(url || '').trim();
  if (!raw) return '';
  return raw;
};
