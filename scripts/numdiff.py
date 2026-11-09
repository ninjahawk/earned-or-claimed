import re,sys
out=open(sys.argv[1]).read(); facts=open(sys.argv[2]).read()
out=re.split(r'\n## References',out)[0]
def nums(t):
    return set(re.findall(r'(?<![\w.])[-+]?\d+(?:[.,]\d+)?',t))
fn=nums(facts)
fn |= {('0'+x) if x.startswith('.') else x for x in re.findall(r'(?<!\d)\.\d+',facts)}
fn |= {x.lstrip('0') for x in fn}
miss=[]
for m in re.finditer(r'(?<![\w.])[-+]?\d+(?:[.,]\d+)?',out):
    n=m.group(0)
    if n not in fn and n.lstrip('+-') not in fn and n.lstrip('0') not in fn:
        miss.append((n,out[max(0,m.start()-50):m.end()+30].replace('\n',' ')))
for n,c in miss: print(n,'|',c)
print('MISSING',len(miss))
