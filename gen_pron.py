"""用 g2pkk 產生每句的實際唸法，輸出 pron.js（window.KO_PRON = {句子: 唸法}）。

- g2pkk 逐音節對應，空格位置照原句放回；跨詞連音（收音移到下一個 ㅇ 開頭的字）時把兩個詞連起來寫。
- g2pkk 判斷錯的句子寫在 OVERRIDE 手動修正。
用法：.venv/bin/python gen_pron.py
"""
import json
import re
from pathlib import Path

from g2pkk import G2p

ROOT = Path(__file__).parent
H = re.compile(r"[가-힣]")

# g2pkk 的錯誤或不自然處，依標準發音手動修正
OVERRIDE = {
    "잠시만요": "잠시만뇨",          # ㄴ 添加，不是連音
    "강남역 가 주세요": "강남녁 가 주세요",  # 강남역 [강남녁]
    "지하철역 어디예요": "지하철려거디예요",  # 지하철역 [지하철력]，再連到 어디
    "지하철역": "지하철력",
    "편의점": "펴니점",              # 字中的 ㅢ 一般唸 ㅣ
}


def initial(ch: str) -> int:
    return (ord(ch) - 0xAC00) // 588


def align(orig: str, pron: str) -> str:
    """把 g2p 結果的音節放回原句的空格位置；跨詞連音時把空格拿掉。"""
    ps = [c for c in pron if H.match(c)]
    if len(ps) != sum(1 for c in orig if H.match(c)):
        return orig  # 對不上就不顯示，避免誤導
    out, i, prev_changed = [], 0, False
    chars = list(orig)
    for j, c in enumerate(chars):
        if H.match(c):
            out.append(ps[i])
            prev_changed = ps[i] != c
            i += 1
        elif c == " ":
            nxt = next((k for k in chars[j + 1:] if H.match(k)), None)
            linked = nxt and initial(nxt) == 11 and initial(ps[i]) != 11 and prev_changed
            if not linked:
                out.append(c)
        else:
            out.append(c)
    return "".join(out)


def main() -> None:
    g2p = G2p()
    phrases = json.loads((ROOT / "phrases.json").read_text("utf-8"))
    pron = {}
    for p in phrases:
        k = p["key"]
        if "," in k or sum(1 for c in k if H.match(c)) < 2:
            continue
        r = OVERRIDE.get(k) or align(k, g2p(k))
        if r != k:
            pron[k] = r
    (ROOT / "pron.js").write_text(
        "window.KO_PRON=" + json.dumps(pron, ensure_ascii=False, indent=0) + ";\n", "utf-8"
    )
    print(f"{len(pron)} phrases with pronunciation changes")
    for k, v in pron.items():
        print(f"  {k} → [{v}]")


if __name__ == "__main__":
    main()
