import { toDisplayImageUrl } from './imageProxy';

const loadedUrls = new Set();
const loadingUrls = new Set();
const scheduledStudentPreloadIds = new Set();

const STUDENT_WELCOME_CRITICAL_URLS = [
  '/login/background.jpg',
  '/welcome/background.jpg',
  '/welcome/book-page.png',
  '/welcome/school-badge.png',
  '/welcome/course-title.png',
];

const STUDENT_FRONTEND_STATIC_IMAGE_URLS = [
  ...STUDENT_WELCOME_CRITICAL_URLS,
  '/transition-pages/sensory-transition/background.jpg',
  '/transition-pages/sensory-transition/book-page.png',
  '/transition-pages/recordcard-transition/background.jpg',
  '/transition-pages/recordcard-transition/book-page.png',
  '/resources/feeling.jpg',
  '/resources/orderly.jpg',
  '/resources/vocabulary.jpg',
  '/ViewRecordCards/RecordCard1.png',
  '/ViewRecordCards/RecordCard2.png',
  '/ViewRecordCards/RecordCard3.png',
  '/ViewRecordCards/RecordCard4.png',
  '/final-draft/three-trees.jpg',
  '/final-draft/background.jpg',
  '/final-draft/book-page.png',
  '/sun.svg',
  '/icons.svg',
  '/favicon.svg',
  '/favicon1.svg',
];

const STUDENT_POST_WELCOME_IMAGE_URLS = STUDENT_FRONTEND_STATIC_IMAGE_URLS.filter(
  (url) => !STUDENT_WELCOME_CRITICAL_URLS.includes(url)
);

const toSafeUrl = (url) => {
  const raw = String(url || '').trim();
  if (!raw) return '';
  return toDisplayImageUrl(raw);
};

const collectStudentDynamicUrls = (studentData = {}) => {
  return [
    studentData.pre_plant_1,
    studentData.pre_plant_2,
    studentData.pre_plant_3,
    studentData.pre_record_card,
  ]
    .map(toSafeUrl)
    .filter(Boolean);
};

const loadOneImage = (url) =>
  new Promise((resolve) => {
    const img = new Image();
    img.onload = resolve;
    img.onerror = resolve;
    img.src = url;
  });

export const preloadImages = async (urls, options = {}) => {
  if (typeof window === 'undefined' || typeof Image === 'undefined') return;

  const concurrency = Math.max(1, Number(options.concurrency) || 6);
  const queue = [...new Set((urls || []).map(toSafeUrl).filter(Boolean))].filter(
    (url) => !loadedUrls.has(url) && !loadingUrls.has(url)
  );
  if (queue.length === 0) return;

  let cursor = 0;
  const worker = async () => {
    while (cursor < queue.length) {
      const index = cursor;
      cursor += 1;
      const url = queue[index];
      loadingUrls.add(url);
      await loadOneImage(url);
      loadingUrls.delete(url);
      loadedUrls.add(url);
    }
  };

  const workers = Array.from({ length: Math.min(concurrency, queue.length) }, () => worker());
  await Promise.all(workers);
};

export const preloadStudentAllImages = async (studentData) => {
  const urls = [
    ...STUDENT_WELCOME_CRITICAL_URLS,
    ...STUDENT_POST_WELCOME_IMAGE_URLS,
    ...collectStudentDynamicUrls(studentData),
  ];
  await preloadImages(urls, { concurrency: 4 });
};

export const scheduleStudentPreloadAfterWelcome = (studentData, options = {}) => {
  const sid = String(studentData?.student_id || '').trim();
  if (!sid) return;
  if (scheduledStudentPreloadIds.has(sid)) return;
  scheduledStudentPreloadIds.add(sid);

  const delayMs = Math.max(0, Number(options.delayMs) || 120);
  const task = async () => {
    const urls = [
      ...STUDENT_POST_WELCOME_IMAGE_URLS,
      ...collectStudentDynamicUrls(studentData),
    ];
    try {
      await preloadImages(urls, { concurrency: 6 });
    } catch (_) {
      // Keep preload best-effort and non-blocking.
    }
  };

  window.setTimeout(() => {
    task();
  }, delayMs);
};

export const preloadTeacherAllImages = async (students = []) => {
  const dynamicUrls = students.flatMap((student) => collectStudentDynamicUrls(student));
  const urls = [...STUDENT_WELCOME_CRITICAL_URLS, ...STUDENT_POST_WELCOME_IMAGE_URLS, ...dynamicUrls];
  await preloadImages(urls, { concurrency: 10 });
};

