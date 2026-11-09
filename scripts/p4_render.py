#!/usr/bin/env python3
"""Render report/REPORT.md -> report/REPORT.html -> report/REPORT.pdf (python-markdown + weasyprint). Usage: /tmp/rv/bin/python scripts/p4_render.py  (weasyprint via the named venv)."""
import markdown,subprocess,re,os
os.chdir('report'); src=open('REPORT.md').read()
title=src.split('\n',1)[0].lstrip('# ').strip(); body=src.split('\n',1)[1]
html=markdown.markdown(body,extensions=['tables','md_in_html'])
css="""@page{size:A4;margin:2.1cm 2.1cm 2.2cm 2.1cm;@bottom-center{content:counter(page);font-size:9pt;color:#555}}
body{font-family:'DejaVu Serif',Georgia,serif;font-size:10pt;line-height:1.38;color:#111;text-align:justify;hyphens:auto}
h1{font-size:17pt;text-align:center;margin:0 0 .5em;line-height:1.2}
h2{font-size:12.5pt;margin:1.1em 0 .35em;border-bottom:.6pt solid #888;padding-bottom:2pt}
h3{font-size:10.6pt;margin:.9em 0 .3em}
.authors{display:flex;justify-content:center;gap:3.5em;text-align:center;margin-bottom:1em;font-size:10pt}
.abstract{margin:0 1.4em 1em;font-size:9.4pt;background:#f6f6f6;padding:.6em .9em;border-left:2pt solid #2e86c1}
table{border-collapse:collapse;margin:.4em auto .8em;font-size:8.6pt;text-align:left}
th,td{border-bottom:.4pt solid #bbb;padding:2pt 6pt}th{border-bottom:1pt solid #333;background:#f1f1f1}
figure{margin:.6em 0;text-align:center;page-break-inside:avoid}figure img{width:100%}
figcaption{font-size:8.4pt;text-align:left;color:#222;margin-top:2pt}
code{font-size:8.8pt}ul,ol{margin:.3em 0 .5em;padding-left:1.4em}li{margin:.15em 0}
.pagebreak{page-break-before:always}.footnote-line{font-size:8pt;color:#555;margin-top:1.5em;border-top:.4pt solid #aaa;padding-top:3pt}
a{color:#1a5276;text-decoration:none}"""
doc=f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{css}</style></head><body><h1>{title}</h1>{html}</body></html>"
open('REPORT.html','w').write(doc)
subprocess.run(['weasyprint','REPORT.html','REPORT.pdf'],check=True)
