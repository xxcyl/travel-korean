# 本地韓文 TTS（MeloTTS-KR）

## 重新產生音檔
改了 index.html 裡的韓文後：

    node extract.mjs                 # 更新 phrases.json
    .venv/bin/python gen_audio.py    # 只補新句子；加 --force 全部重做

## 重建環境時的注意事項（macOS / Apple Silicon）
- Python 3.11；torch 鎖 2.5.1（2.6+ 的 torch.load 預設 weights_only 可能讀不了模型）
- PyPI 官方很慢時：torch 從 https://download.pytorch.org/whl/cpu，其餘用 --index-url https://mirrors.aliyun.com/pypi/simple
- MeloTTS 用 `--no-deps` 安裝，相依套件照 requirements.lock（避開 gradio 等造成的解析回溯）
- 需要 `setuptools<81`（librosa 0.9 用到 pkg_resources）
- 日文字典改指向 unidic_lite：`ln -s ../unidic_lite/dicdir site-packages/unidic/dicdir`
- NLTK 資料：`SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())") python -m nltk.downloader -d .venv/nltk_data cmudict averaged_perceptron_tagger averaged_perceptron_tagger_eng`
- 韓文 mecab（python-mecab-ko）和日文 MeCab 在不分大小寫的 APFS 上會撞名，
  所以韓文版裝在 `.venv/mecab_ko`（`--target`），再用 site-packages/zz_mecab_ko.pth 加入路徑

## 預覽
音檔要透過 http 載入，直接雙擊開 file:// 在部分瀏覽器會退回系統語音：

    python3 -m http.server 8765
