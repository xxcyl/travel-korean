/* 離線支援：
   - 頁面、唸法、音檔清單：先抓網路（有更新就用新的），抓不到或太慢才用快取
   - 音檔：有快取就直接用；沒有就下載並存起來。支援 Range 請求（iPhone Safari 播放音檔需要）
   - Google 字型：先用快取，背景更新
   YouGlish、YouTube 等外部服務不快取，離線時就無法使用。 */
const SHELL = 'shell-v1';
const AUDIO = 'audio-v1';
const FONTS = 'fonts-v1';
const CORE = ['./', 'index.html', 'pron.js', 'audio/manifest.js', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/favicon-64.png', 'icons/apple-touch-icon.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => ![SHELL, AUDIO, FONTS].includes(k)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    if (/\/audio\/[ns]\/[^/]+\.mp3$/.test(url.pathname)) e.respondWith(audio(req));
    else e.respondWith(networkFirst(req));
  } else if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(staleWhileRevalidate(req, FONTS));
  }
});

function networkFirst(req) {
  const fromCache = () => caches.match(req, { ignoreSearch: true })
    .then((r) => r || (req.mode === 'navigate' ? caches.match('./') : undefined));
  const net = fetch(req).then((res) => {
    if (res.ok) { const copy = res.clone(); caches.open(SHELL).then((c) => c.put(req, copy)); }
    return res;
  });
  // 網路太慢時（例如訊號很差），4 秒後改用快取
  const slow = new Promise((resolve) => setTimeout(resolve, 4000)).then(fromCache);
  return Promise.race([net, slow.then((r) => r || net)])
    .catch(() => fromCache().then((r) => r || Response.error()));
}

async function audio(req) {
  const cache = await caches.open(AUDIO);
  const key = req.url.split('#')[0];
  let res = await cache.match(key);
  if (!res) {
    try {
      const full = await fetch(key);           // 不帶 Range，拿完整檔案才能快取
      if (!full.ok) return full;
      await cache.put(key, full.clone());
      res = full;
    } catch (err) {
      return Response.error();
    }
  }
  return withRange(req, res);
}

async function withRange(req, res) {
  const range = req.headers.get('range');
  if (!range) return res;
  const buf = await res.arrayBuffer();
  const m = /bytes=(\d*)-(\d*)/.exec(range) || [];
  const size = buf.byteLength;
  let start = m[1] ? parseInt(m[1], 10) : 0;
  let end = m[2] ? parseInt(m[2], 10) : size - 1;
  if (!m[1] && m[2]) { start = Math.max(0, size - parseInt(m[2], 10)); end = size - 1; }
  end = Math.min(end, size - 1);
  return new Response(buf.slice(start, end + 1), {
    status: 206,
    headers: {
      'Content-Type': res.headers.get('Content-Type') || 'audio/mpeg',
      'Content-Range': `bytes ${start}-${end}/${size}`,
      'Content-Length': String(end - start + 1),
      'Accept-Ranges': 'bytes',
    },
  });
}

function staleWhileRevalidate(req, name) {
  return caches.open(name).then((c) => c.match(req).then((hit) => {
    const net = fetch(req).then((res) => { if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; })
      .catch(() => hit || Response.error());
    return hit || net;
  }));
}
