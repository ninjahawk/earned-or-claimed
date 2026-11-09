#!/usr/bin/env python3
"""v3 packet: report/v3/REPORT-v3.md -> report/v3/REPORT-v3.html -> report/REPORT-final.pdf (python-markdown + weasyprint).
Layout only: the text is the input file's, untouched except: author lines under the title are replaced by the fixed title block,
[FIGn] + the following '*Figure n.*' caption line become a <figure> with report/v3/fig images.
Usage: python3 scripts/p7_packet.py [input.md] [output.pdf]"""
import markdown,subprocess,re,os,sys,html as H
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'report/v3/REPORT-v3.md')
out_pdf=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,'report/REPORT-final.pdf')
src=open(src_path,newline='').read().replace('\r\n','\n').replace('\\\n','  \n')
FIG={'1':'fig/fig1_claims.png','2':'fig/fig2_evidence.png','3':'fig/fig3_scorers.png'}
title=src.split('\n',1)[0].lstrip('# ').strip().replace('**','')
rest=src.split('\n',1)[1]
i=rest.find('## Abstract'); rest=rest[i:] if i>=0 else rest          # drop the writer's author lines; fixed block below
def fig(m):
    n,cap=m.group(1),(m.group(2) or '').strip()
    cap=cap.replace(chr(92)+'*','&#42;'); cap=re.sub(r'^\*?(Figure \d+\.)\*?',r'<b>\1</b>',cap.strip('_'))
    cap=re.sub(r'\*\*?([^*]+)\*\*?',r'<em>\1</em>',cap)
    return f'\n<figure class="fig{n}"><img src="{FIG[n]}"><figcaption>{cap}</figcaption></figure>\n'
rest=re.sub(r'^\[FIG(\d)\][ \t]*\n+(?:[ \t]*(\*?_?Figure \d+\..*))?$',fig,rest,flags=re.M)
# abstract box
rest=re.sub(r'## Abstract\n(.*?)(?=\n<figure|\n## )',lambda m:'<section class="abstract"><h2 class="abs">Abstract</h2>\n\n'+m.group(1).strip()+'\n\n</section>\n',rest,count=1,flags=re.S)
# references + appendices start on a new page
rest=re.sub(r'\n## (References)',r'\n<div class="pagebreak"></div>\n\n## \1',rest,count=1)
body=markdown.markdown(rest,extensions=['tables','md_in_html','sane_lists'])
body=re.sub(r'<section class="abstract"><h2 class="abs">Abstract</h2>\s*(.*?)</section>',lambda m:'<section class="abstract"><h2 class="abs">Abstract</h2>'+markdown.markdown(m.group(1))+'</section>',body,flags=re.S)
body=body.replace('<blockquote>\n<p>Why this matters for swarms.','<blockquote>\n<p><strong>Why this matters for swarms.</strong>')
body=body.replace('<p>&lt;section class="abstract"&gt;','<p>')
css="""@page{size:A4;margin:1.75cm 1.85cm 1.9cm 1.85cm;@bottom-center{content:counter(page);font:8.5pt 'Nimbus Sans',sans-serif;color:#666}
 @top-right{content:"Earned or Claimed?  ·  Apart Swarm Alignment Hackathon 2026";font:7.5pt 'Nimbus Sans',sans-serif;color:#8a929a}}
@page:first{@top-right{content:none}}
body{font-family:'Bitstream Charter','Charter','DejaVu Serif',serif;font-size:9.7pt;line-height:1.34;color:#16202a;text-align:justify;hyphens:auto}
h1{font-family:'Nimbus Sans','Ubuntu Sans',sans-serif;font-size:19pt;line-height:1.18;text-align:center;margin:0 0 .35em;color:#12263a;font-weight:700}
.byline{text-align:center;font-family:'Nimbus Sans',sans-serif;font-size:9.6pt;color:#333;margin-bottom:.9em;line-height:1.35}
.byline .name{font-size:11pt;font-weight:700;color:#12263a}
.byline .venue{color:#2a6f97;font-size:8.8pt;margin-top:.2em}
h2{font-family:'Nimbus Sans','Ubuntu Sans',sans-serif;font-size:12pt;color:#12263a;margin:.8em 0 .3em;padding-bottom:2pt;border-bottom:.7pt solid #2a6f97;page-break-after:avoid}
h3{font-family:'Nimbus Sans','Ubuntu Sans',sans-serif;font-size:10.4pt;color:#12263a;margin:.6em 0 .2em;page-break-after:avoid}
p{margin:.25em 0 .4em;orphans:2;widows:2}
.abstract{background:#f3f6f9;border-left:3pt solid #2a6f97;padding:.55em 1em .45em;margin:0 .6em .6em;font-size:9.5pt;line-height:1.4}
.abstract h2.abs{border:none;margin:0 0 .2em;font-size:9.6pt;letter-spacing:.08em;text-transform:uppercase;color:#2a6f97}
blockquote{margin:.7em .4em;padding:.55em .9em;background:#fdf6ec;border:.8pt solid #e0b872;border-left:3.5pt solid #d68910;border-radius:2pt;font-size:9.6pt;page-break-inside:avoid}
blockquote p{margin:.2em 0}
table{border-collapse:collapse;margin:.35em auto .5em;font-size:8.3pt;text-align:left;page-break-inside:avoid}
td:first-child,th:first-child{white-space:nowrap}th,td{border-bottom:.4pt solid #c5ccd3;padding:1.4pt 6pt}th{border-bottom:1pt solid #12263a;background:#eef2f6;font-family:'Nimbus Sans',sans-serif}
figure{margin:.35em 0 .55em;text-align:center;page-break-inside:avoid}figure img{width:92%}
figure.fig1 img{width:100%}figure.fig3 img{width:74%}
figcaption{font-size:8.5pt;text-align:left;color:#2b3640;margin-top:3pt;line-height:1.35}
code{font-size:8.6pt;font-family:'DejaVu Sans Mono',monospace}ul,ol{margin:.3em 0 .5em;padding-left:1.4em}li{margin:.12em 0}
strong{color:#0f1f2e}
.pagebreak{page-break-before:always}
a{color:#1f5f8b;text-decoration:none}"""
byline=('<div class="byline"><div class="name">Nathan Langley</div>Undergraduate, University of North Carolina at Greensboro<br>'
        'With Apart Research<div class="venue">Research conducted at the Apart Swarm Alignment Hackathon, November 2026</div></div>')
doc=(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{H.escape(title)}</title><meta name='author' content='Nathan Langley'>"
     f"<style>{css}</style></head><body><h1>{H.escape(title)}</h1>{byline}{body}</body></html>")
os.chdir(os.path.join(ROOT,'report/v3')); open('REPORT-v3.html','w').write(doc)
subprocess.run(['weasyprint','REPORT-v3.html',out_pdf],check=True)
print('wrote',out_pdf)
