import json,os
S=os.path.dirname(os.path.abspath(__file__))
t=open(S+'/template.html',encoding='utf-8').read().replace('__DATA__',open(S+'/data.json',encoding='utf-8').read())
out=r"C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)/guides/raids.html"
open(out,'w',encoding='utf-8').write(t); print(len(t.encode()))
