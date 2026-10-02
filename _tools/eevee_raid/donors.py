import zipfile,json,re,sys
INST=r"C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)"
z=zipfile.ZipFile(INST+"/mods/Cobblemon-neoforge-1.7.3+1.21.1.jar")
D={p['id']:p for p in json.load(open(INST+'/guides/pokedex/data/pokedex.json',encoding='utf-8'))['pokemon']}
src=json.load(open('src.json',encoding='utf-8'))
need=sorted({en for sp in src.values() for en,s in sp.items() if not s.startswith('L')})
ids={en:re.sub(r"[^a-z0-9]","",en.lower()) for en in need}
learn={en:[] for en in need}
RK={'common':0,'uncommon':1,'rare':2,'ultra-rare':3}
for n in z.namelist():
    if '/species/generation' not in n or not n.endswith('.json'): continue
    sp=n.split('/')[-1][:-5]; p=D.get(sp)
    if not p or not p.get('sp'): continue
    rk=min(RK.get(s.get('k'),3) for s in p['sp'])
    if rk>1: continue
    mv=json.loads(z.read(n)).get('moves',[])
    for m in mv:
        k,v=m.split(':',1)
        if k.isdigit():
            for en,i in ids.items():
                if v==i: learn[en].append((int(k),rk,p['n'][1],sp))
out={}
for en,l in learn.items():
    l.sort(key=lambda x:(x[0]>1 and 0, x[0], x[1]))  # prefer real level-up over lv1 relearn
    seen=[];res=[]
    for lv,rk,ko,sp in sorted(l,key=lambda x:(x[1],x[0])):
        if ko in seen: continue
        seen.append(ko); res.append([ko,lv])
        if len(res)==3: break
    out[en]=res
    print(en,res,file=sys.stderr)
json.dump(out,open('donors.json','w',encoding='utf-8'),ensure_ascii=False)
