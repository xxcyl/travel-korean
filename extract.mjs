// 從 index.html 的資料陣列擷取所有要發音的韓文，輸出 phrases.json
// 規則：引號內含韓文音節、且不含漢字的字串（排除說明文字、提示詞）
import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync(new URL('./index.html', import.meta.url), 'utf8');
// 只掃資料區，避免把介面用的 HTML 字串當成句子
const script = html.slice(html.indexOf('/* ---------- data ---------- */'), html.indexOf('/* ---------- phrase index ---------- */'));
const HANGUL = /[\uAC00-\uD7A3]/;
const HAN = /[\u4E00-\u9FFF]/;

// 與頁面 speak() 相同的正規化
export const norm = s => s.replace(/[?？!！]/g, '').trim();

// key：頁面查詢用；text：保留問號，讓 TTS 唸出疑問語調
const map = new Map();
for (const m of script.matchAll(/"([^"\\]*)"/g)) {
  const s = m[1].trim();
  if (HANGUL.test(s) && !HAN.test(s) && !map.has(norm(s))) map.set(norm(s), s);
}
// 字母卡唸的是「音節, 例字」，是執行時組出來的，要從 VOW/CON 陣列另外組合（與頁面 hc() 相同）
for (const name of ['VOW', 'CON']) {
  const arr = JSON.parse(script.match(new RegExp(`var ${name}=(\\[.*?\\]\\]);`))[1]);
  for (const a of arr) { const s = a[1] + ', ' + a[4]; map.set(norm(s), s); }
}
const list = [...map].map(([key, text]) => ({ key, text }));
writeFileSync(new URL('./phrases.json', import.meta.url), JSON.stringify(list, null, 1));
console.log(list.length + ' phrases');
