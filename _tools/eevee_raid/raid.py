import json,glob,os,math,collections,sys
INST=r"C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)"
S=os.path.dirname(os.path.abspath(__file__))
MV=json.load(open(S+'/mv.json')); KO=json.load(open(S+'/ko.json',encoding='utf-8'))
D=json.load(open(INST+'/guides/pokedex/data/pokedex.json',encoding='utf-8')); DEX={p['id']:p for p in D['pokemon']}
CH={'normal':{'rock':.5,'ghost':0,'steel':.5},'fire':{'fire':.5,'water':.5,'grass':2,'ice':2,'bug':2,'rock':.5,'dragon':.5,'steel':2},'water':{'fire':2,'water':.5,'grass':.5,'ground':2,'rock':2,'dragon':.5},'electric':{'water':2,'electric':.5,'grass':.5,'ground':0,'flying':2,'dragon':.5},'grass':{'fire':.5,'water':2,'grass':.5,'poison':.5,'ground':2,'flying':.5,'bug':.5,'rock':2,'dragon':.5,'steel':.5},'ice':{'fire':.5,'water':.5,'grass':2,'ice':.5,'ground':2,'flying':2,'dragon':2,'steel':.5},'fighting':{'normal':2,'ice':2,'poison':.5,'flying':.5,'psychic':.5,'bug':.5,'rock':2,'ghost':0,'dark':2,'steel':2,'fairy':.5},'poison':{'grass':2,'poison':.5,'ground':.5,'rock':.5,'ghost':.5,'steel':0,'fairy':2},'ground':{'fire':2,'electric':2,'grass':.5,'poison':2,'flying':0,'bug':.5,'rock':2,'steel':2},'flying':{'electric':.5,'grass':2,'fighting':2,'bug':2,'rock':.5,'steel':.5},'psychic':{'fighting':2,'poison':2,'psychic':.5,'dark':0,'steel':.5},'bug':{'fire':.5,'grass':2,'fighting':.5,'poison':.5,'flying':.5,'psychic':2,'ghost':.5,'dark':2,'steel':.5,'fairy':.5},'rock':{'fire':2,'ice':2,'fighting':.5,'ground':.5,'flying':2,'bug':2,'steel':.5},'ghost':{'normal':0,'psychic':2,'ghost':2,'dark':.5},'dragon':{'dragon':2,'steel':.5,'fairy':0},'dark':{'fighting':.5,'psychic':2,'ghost':2,'dark':.5,'fairy':.5},'steel':{'fire':.5,'water':.5,'electric':.5,'ice':2,'rock':2,'steel':.5,'fairy':2},'fairy':{'fire':.5,'fighting':2,'poison':.5,'dragon':2,'dark':2,'steel':.5}}
def eff(a,ts): 
    m=1
    for t in ts: m*=CH[a].get(t,1)
    return m
EE={'sylveon':(['fairy'],['fairy'],None,5),'vaporeon':(['water'],['water'],'water',4.5),'umbreon':(['dark'],['dark'],None,4),
    'leafeon':(['grass'],['grass','dark'],None,4),'glaceon':(['ice'],['ice'],None,3.5),'espeon':(['psychic'],['psychic','fairy'],None,3),
    'jolteon':(['electric'],['electric'],'electric',2),'flareon':(['fire'],['fire'],'fire',2)}
TIERS=['one','two','three','four','five','six','seven']
def types_for(sp,fn,j):
    p=DEX.get(sp); 
    if not p: return None,None
    asp=set()
    for cp in j['pokemon'].get('custom_properties',[]):
        asp.add(cp['name'] if cp['value'] is True else str(cp['value']))
    base=fn[len(sp)+1:] if fn.startswith(sp+'_') else ''
    if j.get('raid_feature')=='MEGA': asp.add(base or 'mega')
    if j.get('raid_feature')=='DYNAMAX' and base=='gmax': asp.add('gmax')
    ko=p['n'][1]; t=p['t']
    for f in p.get('forms',[]):
        fa=set(f.get('asp') or [])
        if fa & asp:
            t=f['t']; fn2=f['n'][1] if f.get('n') else ''
            ko=fn2 if (fn2 and ko in fn2) else (f'{ko} ({fn2})' if fn2 else ko); break
    return t,ko
out=[]; miss=[]
FILES={}
for d in [os.environ['RDJAR']+'/data/cobblemonraiddens/raid/boss', INST+'/kubejs/data/cobblemonraiddens/raid/boss']:
    for f in glob.glob(d+'/*.json'): FILES[os.path.basename(f)]=f
for f in sorted(FILES.values()):
    fn=os.path.basename(f)[:-5]; j=json.load(open(f,encoding='utf-8')); sp=j['pokemon']['species'].split(':')[-1]
    t,ko=types_for(sp,fn,j)
    if t is None or not j.get('raid_tier') or not j['pokemon'].get('moves'): miss.append(fn); continue
    tier=TIERS.index(j['raid_tier'].split('_')[-1].lower())+1
    mv=[]
    for m in j['pokemon']['moves']:
        k=m.replace(' ','').replace('-','').lower(); d=MV.get(k)
        if not d: mv.append({'k':KO.get('cobblemon.move.'+k,k),'t':None,'c':'?'}); continue
        mv.append({'k':KO.get('cobblemon.move.'+k,k),'t':d['t'],'c':{'Physical':'P','Special':'S','Status':'-'}[d['c']]})
    dmg=[x for x in mv if x['c'] in 'PS' and x['t']]
    ranks=[]
    for e,(dt,at,imm,bulk) in EE.items():
        off=max(eff(a,t) for a in at)
        thr=max([0 if x['t']==imm else eff(x['t'],dt) for x in dmg] or [0.5])
        sc=math.log2(max(off,.25))-math.log2(max(thr,.25))+bulk*0.12
        mark='best' if off>=2 and thr<=1 else ('good' if off>=1 and thr<=.5 else ('ok' if off>=1 and thr<=1 else 'bad'))
        ranks.append((sc,e,mark,off,thr))
    ranks.sort(reverse=True)
    pick=[(e,mk) for sc,e,mk,o,th in ranks if mk!='bad'][:3]
    out.append({'id':fn,'n':ko,'tier':tier,'f':(j.get('raid_feature') or 'DEFAULT').lower(),'t':t,'mv':mv,'pick':pick,
                'ph':sum(1 for x in mv if x['c']=='P'),'sp':sum(1 for x in mv if x['c']=='S')})
print('bosses',len(out),'missing',miss,file=sys.stderr)
cnt=collections.defaultdict(collections.Counter)
for b in out:
    for i,(e,mk) in enumerate(b['pick']):
        if i==0: cnt[e]['top_'+('hi' if b['tier']>=5 else 'lo')]+=1
        if mk=='best': cnt[e]['best_'+('hi' if b['tier']>=5 else 'lo')]+=1
none=[ (b['n'],b['tier']) for b in out if not b['pick']]
print({e:dict(c) for e,c in cnt.items()},file=sys.stderr)
print('no pick',len(none),[x for x in none if x[1]>=5][:40],file=sys.stderr)
print('tiers',collections.Counter(b['tier'] for b in out),file=sys.stderr)
json.dump(out,open(S+'/bosses.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
