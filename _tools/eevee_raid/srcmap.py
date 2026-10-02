import zipfile,json,re,sys
J=r"C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)/mods/Cobblemon-neoforge-1.7.3+1.21.1.jar"
z=zipfile.ZipFile(J)
paths={n.split('/')[-1][:-5]:n for n in z.namelist() if '/species/generation' in n and n.endswith('.json')}
t=open('template.html',encoding='utf-8').read()
out={}
for sp,body in re.findall(r'\n (\w+):\{ko:.*?mv:\[(.*?\])\],',t,re.S):
    mv=json.loads(z.read(paths[sp]))['moves']; src={}
    for m in mv:
        k,v=m.split(':',1); src.setdefault(v,[]).append(k)
    res={}
    for en in re.findall(r'\["[^"]+","([^"]+)"\]',body):
        mid=re.sub(r"[^a-z0-9]","",en.lower()); s=src.get(mid,[])
        lv=[int(x) for x in s if x.isdigit()]
        res[en]=('L%d'%min(lv)) if lv else ('E' if s==['egg'] else ('T' if s else '?'))
    out[sp]=res
print(json.dumps(out,ensure_ascii=False,indent=0),file=sys.stderr)
json.dump(out,open('src.json','w',encoding='utf-8'),ensure_ascii=False)
