import zipfile,json,re,collections
z=zipfile.ZipFile('mods/Cobblemon-neoforge-1.7.3+1.21.1.jar')
out={}
for n in z.namelist():
    if n.startswith('data/cobblemon/recipe/') and n.endswith('_ball.json'):
        r=json.loads(z.read(n))
        if r.get('type')!='minecraft:crafting_shaped': 
            out[n.split('/')[-1]]=r.get('type'); continue
        cnt=collections.Counter()
        for row in r['pattern']:
            for ch in row:
                if ch==' ':continue
                k=r['key'][ch]; k=k if isinstance(k,dict) else k[0]
                cnt[k.get('item') or '#'+k.get('tag')]+=1
        out[n.split('/')[-1][:-5]]=(dict(cnt),r['result'].get('count'))
for k,v in sorted(out.items()): print(k,v)
