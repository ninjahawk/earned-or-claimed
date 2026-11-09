import sys; sys.stdout.reconfigure(encoding="utf-8",errors="replace")
import subprocess, pathlib
P=pathlib.Path(__file__).parent
def pd(src): return subprocess.run(["pandoc",str(P/src),"-f","markdown","-t","latex","--wrap=preserve","--columns=200"],capture_output=True,text=True,encoding="utf-8",check=True).stdout
t=(P/"template.tex").read_text(encoding="utf-8")
title=(P/"title.txt").read_text(encoding="utf-8").strip()
import re
title=re.sub(r'"([^"]+)"',r"``\1''",title)
t=t.replace("$title$",title).replace("$abstract$",pd("abstract.md")).replace("$body$",pd("body.md"))
(P/"paper.tex").write_text(t,encoding="utf-8")
for _ in range(2):
    r=subprocess.run(["xelatex","-interaction=nonstopmode","-halt-on-error","paper.tex"],cwd=P,capture_output=True,text=True,encoding="utf-8",errors="replace")
print(r.stdout[-1500:])
