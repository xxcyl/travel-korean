"""用 MeloTTS-KR 把 phrases.json 的每句韓文產生成 mp3。

輸出：
  audio/n/<id>.mp3   正常語速
  audio/s/<id>.mp3   慢速
  audio/manifest.js  window.KO_AUDIO = {韓文: id}，給頁面查詢用
已存在的檔案會略過；加 --force 全部重做。
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from melo.api import TTS

ROOT = Path(__file__).parent
OUT = ROOT / "audio"
SPEEDS = {"n": 1.0, "s": 0.75}
FORCE = "--force" in sys.argv


def audio_id(key: str) -> str:
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]


def to_mp3(wav: Path, mp3: Path) -> None:
    # 去掉頭尾靜音、音量標準化，轉成單聲道 mp3
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
         "-af", "silenceremove=start_periods=1:start_threshold=-45dB,"
                "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                "adelay=80,apad=pad_dur=0.15,loudnorm=I=-16:TP=-1.5",
         "-ac", "1", "-ar", "24000", "-b:a", "64k", str(mp3)],
        check=True,
    )


def main() -> None:
    phrases = json.loads((ROOT / "phrases.json").read_text("utf-8"))
    model = TTS(language="KR", device="cpu")
    spk = model.hps.data.spk2id["KR"]

    manifest = {}
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "x.wav"
        for i, p in enumerate(phrases, 1):
            aid = audio_id(p["key"])
            manifest[p["key"]] = aid
            for sub, speed in SPEEDS.items():
                mp3 = OUT / sub / f"{aid}.mp3"
                if mp3.exists() and not FORCE:
                    continue
                mp3.parent.mkdir(parents=True, exist_ok=True)
                model.tts_to_file(p["text"], spk, str(wav), speed=speed, quiet=True)
                to_mp3(wav, mp3)
            print(f"[{i}/{len(phrases)}] {p['text']}", flush=True)

    # 刪掉已經不在頁面上的舊音檔
    keep = set(manifest.values())
    for sub in SPEEDS:
        for f in (OUT / sub).glob("*.mp3"):
            if f.stem not in keep:
                f.unlink()

    (OUT / "manifest.js").write_text(
        "window.KO_AUDIO=" + json.dumps(manifest, ensure_ascii=False) + ";\n", "utf-8"
    )
    print(f"done: {len(manifest)} phrases")


if __name__ == "__main__":
    main()
