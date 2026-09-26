// 產生可發佈成 claude.ai Artifact 的版本到 dist/：
//   dist/index.html      去掉 <html>/<head>/<body> 外殼（發佈時會自動包上）
//   dist/audio-data.json 所有 mp3 以 base64 打包（Artifact 最多 255 個檔案，296 個 mp3 放不下）
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';

const dir = new URL('./', import.meta.url);
const read = p => readFileSync(new URL(p, dir));
const html = read('index.html').toString();

const manifest = JSON.parse(read('audio/manifest.js').toString().replace(/^window\.KO_AUDIO=/, '').replace(/;\s*$/, ''));
const data = { map: manifest, n: {}, s: {} };
for (const id of Object.values(manifest)) {
  for (const sub of ['n', 's']) data[sub][id] = read(`audio/${sub}/${id}.mp3`).toString('base64');
}

const loader = `<script>
(function(){
  var d=null;
  window.KO_AUDIO_SRC=function(id,sub){return d&&d[sub][id]?'data:audio/mpeg;base64,'+d[sub][id]:null;};
  fetch('audio-data.json').then(function(r){return r.json();}).then(function(j){d=j;window.KO_AUDIO=j.map;}).catch(function(){});
})();
</script>`;

const head = html.match(/<head>([\s\S]*?)<\/head>/)[1]
  .replace(/<meta [^>]*>\s*/g, '')
  .replace(/<title>[^<]*<\/title>/, '<title>韓國旅遊速成教材</title>')
  // 深色模式時讓表單元件、捲軸也跟著變深
  .replace(/(:root:not\(\[data-theme="light"\]\)\{)/, '$1color-scheme:dark;')
  .replace(/(:root\[data-theme="dark"\]\{)/, '$1color-scheme:dark;');
const body = html.match(/<body>([\s\S]*?)<\/body>/)[1]
  .replace('<script src="audio/manifest.js"></script>', loader);

mkdirSync(new URL('dist/', dir), { recursive: true });
writeFileSync(new URL('dist/index.html', dir), head.trim() + '\n' + body.trim() + '\n');
writeFileSync(new URL('dist/audio-data.json', dir), JSON.stringify(data));
console.log('dist ready');
