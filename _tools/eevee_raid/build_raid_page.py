import json,os
S=os.path.dirname(os.path.abspath(__file__))
TK=["normal","fire","water","electric","grass","ice","fighting","poison","ground","flying","psychic","bug","rock","ghost","dragon","dark","steel","fairy"]
B=None
out=json.load(open(S+'/bosses_bi.json',encoding='utf-8'))
t=open(S+'/template.html',encoding='utf-8').read()
t=t.replace('__SRC__',open(S+'/src.json',encoding='utf-8').read()).replace('__DONORS__',open(S+'/donors_bi.json',encoding='utf-8').read())
t=t.replace('__BOSSES__',json.dumps(out,ensure_ascii=False,separators=(',',':'))).replace('__N__',f'{len(out):,}')
t=t.replace("마릴리 > 저승갓숭 ≈ 루카리오 > 메타그로스","마릴리 > 루카리오 ≈ 저승갓숭 > 메타그로스")
p=r"C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)/guides/eevee-team.html"
open(p,'w',encoding='utf-8').write(t); print(len(t.encode()))
