import json,glob,os,sys,collections
INST=r"C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)"
S=os.path.dirname(os.path.abspath(__file__)); P=os.path.dirname(S)
MV=json.load(open(P+'/mv2.json')); KO=json.load(open(P+'/ko.json',encoding='utf-8'))
D=json.load(open(INST+'/guides/pokedex/data/pokedex.json',encoding='utf-8')); DEX={p['id']:p for p in D['pokemon']}
SPR=json.load(open(INST+'/guides/pokedex/data/sprites.json'))
TIERS=['one','two','three','four','five','six','seven']
FILES={}
for d in [os.environ['RDJAR']+'/data/cobblemonraiddens/raid/boss', INST+'/kubejs/data/cobblemonraiddens/raid/boss']:
    for f in glob.glob(d+'/*.json'): FILES[os.path.basename(f)]=f
LEG={'legendary','mythical','ultra_beast','paradox'}
bosses=[]; miss=[]; nospr=[]
for f in sorted(FILES.values()):
    fn=os.path.basename(f)[:-5]; j=json.load(open(f,encoding='utf-8')); pk=j['pokemon']
    sp=pk['species'].split(':')[-1]; p=DEX.get(sp)
    if not p or not j.get('raid_tier'): miss.append(fn); continue
    asp=set()
    for cp in pk.get('custom_properties',[]): asp.add(cp['name'] if cp['value'] is True else str(cp['value']))
    base=fn[len(sp)+1:] if fn.startswith(sp+'_') else ''
    feat=(j.get('raid_feature') or 'DEFAULT').lower()
    if feat=='mega': asp.add(base or 'mega')
    if feat=='dynamax' and base=='gmax': asp.add('gmax')
    t=p['t']; en,ko=p['n']; slug=''
    for fm in p.get('forms',[]):
        if set(fm.get('asp') or []) & asp:
            t=fm['t']; slug=fm.get('slug') or ''
            fe,fk=(fm.get('n') or ['',''])
            en=fe if (fe and p['n'][0] in fe) else (f"{p['n'][0]} ({fe})" if fe else en)
            ko=fk if (fk and p['n'][1] in fk) else (f"{p['n'][1]} ({fk.replace('의 모습','')})" if fk else ko)
            break
    key=sp+('__'+slug if slug else '')
    if key not in SPR['map']:
        if sp in SPR['map']: nospr.append(key); key=sp
        else: nospr.append(key); key=''
    mv=[]
    for m in pk.get('moves',[]):
        k=m.replace(' ','').replace('-','').lower(); d=MV.get(k)
        if d: mv.append([d['n'],KO.get('cobblemon.move.'+k,d['n']),d['t'],d['c'],d['bp']])
        else: mv.append([m,KO.get('cobblemon.move.'+k,m),'','',0])
    bosses.append({'sp':sp,'no':p['no'],'k':key,'n':[en,ko],'t':t,'tier':TIERS.index(j['raid_tier'].split('_')[-1].lower())+1,
        'f':feat,'rt':(j.get('raid_type') or '').lower(),'mv':mv,'leg':[l for l in p.get('lab',[]) if l in LEG]})
bosses.sort(key=lambda b:(-b['tier'],b['no'],b['n'][0]))
# legendaries
legs=[]
for p in D['pokemon']:
    lab=[l for l in p.get('lab',[]) if l in LEG]
    if not lab: continue
    r=sorted({(b['tier'],b['f']) for b in bosses if b['sp']==p['id']})
    legs.append({'sp':p['id'],'no':p['no'],'k':p['id'] if p['id'] in SPR['map'] else '','n':p['n'],'t':p['t'],'leg':lab,'wild':bool(p.get('sp')),'r':r,'ni':bool(p.get('ni'))})
keys={b['k'] for b in bosses}|{l['k'] for l in legs}; keys.discard('')
spr={'sheets':[s['f'] .replace('sprites/','')+'|%d|%d'%(s['cols'],s['rows']) for s in SPR['sheets']],'map':{k:SPR['map'][k] for k in keys}}
tierc=collections.Counter(b['tier'] for b in bosses)
print('bosses',len(bosses),'miss',len(miss),'nospr',len(nospr),nospr[:15],'legs',len(legs),'legs no raid',sum(1 for l in legs if not l['r']),file=sys.stderr)
json.dump({'b':bosses,'l':legs,'spr':spr,'tc':tierc},open(S+'/data.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(os.path.getsize(S+'/data.json'),file=sys.stderr)
