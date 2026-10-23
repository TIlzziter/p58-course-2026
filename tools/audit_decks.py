"""Ищет слайды, содержимое которых не помещается в 1280×720 (в простом и техническом режиме).

python tools/audit_decks.py lessons/*/lecture.html   — печатает переполненные слайды.
Нужен Google Chrome / Chromium.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROBE = """<script>addEventListener('load',()=>{const out=[];const ss=[...document.querySelectorAll('.slide')];
for(const mode of ['simple','technical']){document.body.dataset.mode=mode;
ss.forEach((s,i)=>{ss.forEach(x=>x.classList.remove('active'));s.classList.add('active');s.style.animation='none';
const cs=getComputedStyle(s);const avail=s.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom);
const kids=[...s.children].filter(k=>k.offsetParent!==null&&getComputedStyle(k).position!=='absolute');
if(!kids.length)return;let top=1e9,bot=-1e9;kids.forEach(k=>{const r=k.getBoundingClientRect();top=Math.min(top,r.top);bot=Math.max(bot,r.top+Math.max(r.height,k.scrollHeight))});
let wide=0;s.querySelectorAll('pre,table').forEach(p=>{if(p.offsetParent&&p.scrollWidth>p.clientWidth+2)wide=1});
const h=Math.round(bot-top);if(h>avail+2||wide)out.push(mode[0]+(i+1)+'='+h+'/'+Math.round(avail)+(wide?'w':''))})}
const p=document.createElement('pre');p.id='audit';p.textContent='@@'+out.join(' ')+'@@';document.body.append(p)})</script>"""


def audit(path: Path) -> list[str]:
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    html = path.read_text(encoding="utf-8").replace("</body>", PROBE + "</body>")
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=path.parent, delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = Path(f.name)
    try:
        res = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--window-size=1280,900",
                              "--virtual-time-budget=4000", "--dump-dom", tmp.as_uri()],
                             capture_output=True, text=True, timeout=120)
    finally:
        tmp.unlink()
    m = re.search(r'id="audit">@@(.*?)@@', res.stdout)
    return m.group(1).split() if m else ["нет результата"]


if __name__ == "__main__":
    bad = 0
    for a in sys.argv[1:]:
        r = audit(Path(a))
        if r:
            bad += 1
            print(a, r)
    print("переполненных файлов:", bad)
