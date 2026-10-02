import json,itertools,math,collections,sys
exec(open('raid.py',encoding='utf-8').read().split("TIERS=")[0])  # CH, eff, EE
B=json.load(open('bosses.json',encoding='utf-8'))
FILL={'azumarill':(['water','fairy'],['water','fairy','fighting'],None,4.5),'lucario':(['fighting','steel'],['fighting','steel'],None,3.5),
 'garchomp':(['dragon','ground'],['ground','dragon'],None,3.5),'annihilape':(['fighting','ghost'],['fighting','ghost'],None,4),
 'metagross':(['steel','psychic'],['steel','ground'],None,4),'tinkaton':(['fairy','steel'],['fairy','steel'],None,4),
 'mamoswine':(['ice','ground'],['ice','ground'],None,3),'conkeldurr':(['fighting'],['fighting'],None,3.5)}
ALL={**EE,**FILL}
APT={'sylveon':1,'vaporeon':.95,'umbreon':.85,'leafeon':.85,'glaceon':.75,'espeon':.7,'jolteon':.55,'flareon':.55,'azumarill':1,'lucario':.8,'annihilape':.9,'garchomp':.75,'metagross':.8,'tinkaton':.75,'mamoswine':.65,'conkeldurr':.8}
TW=[9,15,25,25,20,5,1]; tc=collections.Counter(b['tier'] for b in B)
def val(b,e):
    dt,at,imm,bulk=ALL[e]; off=max(eff(a,b['t']) for a in at)
    dmg=[x for x in b['mv'] if x['c'] in 'PS' and x['t']]
    thr=max([0 if x['t']==imm else eff(x['t'],dt) for x in dmg] or [.5])
    if off>=2 and thr<=1: v=1
    elif off>=1 and thr<=.5: v=.7
    elif off>=1 and thr<=1: v=.35
    else: v=0
    return v*APT[e]
V={(b['id'],e):val(b,e) for b in B for e in ALL}
W={b['id']:TW[b['tier']-1]/tc[b['tier']] for b in B}
def score(team,hi=False):
    s=0;tot=0
    for b in B:
        if hi and b['tier']<4: continue
        w=W[b['id']]; tot+=w; s+=w*max(V[(b['id'],e)] for e in team)
    return s/tot

eev=list(EE)
for k,nf in ((3,3),(2,4)):
    res=[]
    for c in itertools.combinations(eev,k):
        for f in itertools.combinations(FILL,nf):
            res.append((score(c+f),score(c+f,1),c+f))
    res.sort(reverse=True)
    for x in res[:6]: print(k,'+',nf,round(x[0],3),round(x[1],3),x[2])
    best={}
    for x in res:
        best.setdefault(x[2][:k],x)
    print(' best per eevee core:')
    for c,x in sorted(best.items(),key=lambda t:-t[1][0])[:6]: print('  ',round(x[0],3),x[2])
