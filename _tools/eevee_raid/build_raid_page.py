import json,os
S=os.path.dirname(os.path.abspath(__file__))
TK=["normal","fire","water","electric","grass","ice","fighting","poison","ground","flying","psychic","bug","rock","ghost","dragon","dark","steel","fairy"]
B=json.load(open(S+'/bosses.json',encoding='utf-8'))
F={'default':0,'mega':1,'dynamax':2}
out=[[b['n'].replace('의 모습)',')'),b['tier'],F.get(b['f'],0),[TK.index(t) for t in b['t']],[[m['k'],TK.index(m['t']) if m['t'] else -1,{'P':0,'S':1}.get(m['c'],2)] for m in b['mv']]] for b in B]
print('features',set(b['f'] for b in B))
t=open(S+'/template.html',encoding='utf-8').read()
t=t.replace('__SRC__',open(S+'/src.json',encoding='utf-8').read()).replace('__DONORS__',open(S+'/donors.json',encoding='utf-8').read())
t=t.replace('__BOSSES__',json.dumps(out,ensure_ascii=False,separators=(',',':'))).replace('__N__',f'{len(out):,}')
t=t.replace("마릴리 > 저승갓숭 ≈ 루카리오 > 메타그로스","마릴리 > 루카리오 ≈ 저승갓숭 > 메타그로스")
t=t.replace("어떤 조합으로 계산해도 이 둘이 빠지지 않았어요","상위 조합에 거의 항상 이 둘이 들어갔어요")
t=t.replace("고티어에 많은 드래곤·비행 보스를","드래곤·비행 보스를")
p=r"C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)/guides/eevee-team.html"
open(p,'w',encoding='utf-8').write(t); print(len(t.encode()))
