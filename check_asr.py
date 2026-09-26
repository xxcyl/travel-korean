"""用 Whisper 把產生的音檔轉回文字，和原文比對，列出對不上的句子。

用法：.venv/bin/python check_asr.py [n|s]   （預設 n = 正常語速）
結果另存 asr_report.json
"""
import difflib
import json
import re
import sys
from pathlib import Path

import mlx_whisper

ROOT = Path(__file__).parent
MODEL = "mlx-community/whisper-large-v3-turbo"
sub = sys.argv[1] if len(sys.argv) > 1 else "n"


def clean(s: str) -> str:
    return re.sub(r"[^가-힣]", "", s)  # 只比對韓文音節


manifest = json.loads((ROOT / "audio/manifest.js").read_text("utf-8").split("=", 1)[1].rstrip(";\n"))
rows = []
for key, aid in manifest.items():
    r = mlx_whisper.transcribe(
        str(ROOT / f"audio/{sub}/{aid}.mp3"), path_or_hf_repo=MODEL,
        language="ko", temperature=0.0, condition_on_previous_text=False, verbose=None,
    )
    heard = r["text"].strip()
    score = difflib.SequenceMatcher(None, clean(key), clean(heard)).ratio()
    rows.append({"key": key, "heard": heard, "score": round(score, 2)})

(ROOT / "asr_report.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), "utf-8")
bad = [r for r in rows if r["score"] < 1]
print(f"{len(rows) - len(bad)}/{len(rows)} 完全相符")
for r in sorted(bad, key=lambda r: r["score"]):
    print(f"{r['score']:.2f}  {r['key']}  →  {r['heard']}")
