# 여행 한국어｜韓國旅遊速成教材

給零基礎台灣旅客的 30 天韓語教材：讀得出招牌、開口點餐問路、遇到狀況求得到救。

**線上版：** https://<帳號>.github.io/travel-korean/

- 韓文字母（每個字母搭配例字）、招牌、數字與價錢、6 種旅遊情境會話
- 點任何韓文都能聽發音，可切換慢速／正常
- 30 天計畫與出發前檢查清單，勾選進度存在自己的瀏覽器
- 搭配 Claude 語音模式練習的提示詞

## 發音

所有韓文發音都是用開源的 [MeloTTS](https://github.com/myshell-ai/MeloTTS)（MIT）在本機預先產生的 mp3，放在 `audio/`。
沒有對應音檔的文字會改用瀏覽器內建語音。

TTS 唸單一音節不太穩定，所以字母卡會連同例字一起唸（例如 ㅋ →「카, 커피」）。發音以真人為準，這裡只是輔助。

## 修改內容後重新產生音檔

    node extract.mjs                 # 從 index.html 擷取要發音的韓文 → phrases.json
    .venv/bin/python gen_audio.py    # 只產生新句子，並刪掉用不到的舊音檔

環境建置（macOS / Apple Silicon 上的各種相容問題）見 [SETUP.md](SETUP.md)。
`check_asr.py` 可用 Whisper 把音檔轉回文字，找出可能唸錯的句子。

## 本機預覽

    python3 -m http.server 8765

## 授權

MIT。發音由 MeloTTS 產生；文中的旅遊資訊（緊急電話、入境規定等）請以官方最新公告為準。
