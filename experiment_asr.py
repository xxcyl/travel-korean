"""比較不同 TTS 設定在問題字詞上的 Whisper 辨識率（實驗用，不影響正式音檔）。"""
import difflib
import re
import subprocess
import tempfile
from pathlib import Path

import mlx_whisper
from melo.api import TTS

MODEL = "mlx-community/whisper-large-v3-turbo"
ITEMS = ["어", "오", "우", "유", "으", "나", "바", "차", "카", "타", "파", "하",
         "역", "팔", "십", "백", "셋", "넷", "출구", "공항", "환전", "택시", "마트",
         "여섯", "아홉", "냉면", "소주", "비빔밥", "와이파이", "삼겹살", "무료", "휴무"]
SINO = dict(zip("0123456789", ["영", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]))
RUNS = 3


def clean(s):
    s = "".join(SINO.get(c, c) for c in s)
    return re.sub(r"[^가-힣]", "", s)


def heard(path):
    r = mlx_whisper.transcribe(str(path), path_or_hf_repo=MODEL, language="ko",
                               temperature=0.0, condition_on_previous_text=False, verbose=None)
    return r["text"].strip()


def score(target, text):
    return difflib.SequenceMatcher(None, clean(target), clean(text)).ratio()


model = TTS(language="KR", device="cpu")
spk = model.hps.data.spk2id["KR"]
VARIANTS = {
    "melo 目前設定": dict(suffix="", kw={}),
    "melo 加句號": dict(suffix=".", kw={}),
    "melo 低雜訊": dict(suffix="", kw=dict(sdp_ratio=0.0, noise_scale=0.3, noise_scale_w=0.4)),
    "melo 加句號+低雜訊": dict(suffix=".", kw=dict(sdp_ratio=0.0, noise_scale=0.3, noise_scale_w=0.4)),
}

tmp = Path(tempfile.mkdtemp())
results = {}
for name, v in VARIANTS.items():
    per = {}
    for it in ITEMS:
        ss = []
        for k in range(RUNS):
            p = tmp / "x.wav"
            model.tts_to_file(it + v["suffix"], spk, str(p), quiet=True, **v["kw"])
            ss.append((score(it, h := heard(p)), h))
        per[it] = ss
    results[name] = per

per = {}
for it in ITEMS:
    p = tmp / "y.aiff"
    subprocess.run(["say", "-v", "Yuna", "-o", str(p), it], check=True)
    per[it] = [(score(it, h := heard(p)), h)]
results["macOS Yuna（對照）"] = per

print("平均相符率（1.00 = 全對）")
for name, per in results.items():
    allv = [s for ss in per.values() for s, _ in ss]
    exact = sum(1 for ss in per.values() for s, _ in ss if s == 1) / len(allv)
    print(f"  {name:22s} 平均 {sum(allv)/len(allv):.2f}   完全相符 {exact:.0%}")
print()
print("逐字（每格為各次辨識結果）")
names = list(results)
for it in ITEMS:
    print(it.ljust(5), " | ".join(",".join(h for _, h in results[n][it]) for n in names))
