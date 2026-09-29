import re,sys,json
src=open('skyris-factory.html',encoding='utf8').read()
style=re.search(r'<style>\n(.*?)\n</style>',src,re.S).group(1)
links=json.load(open('_src/links.json',encoding='utf8')) if __import__('os').path.exists('_src/links.json') else {}
def L(skip):
    items=[(k,v) for k,v in links.items() if k!=skip]
    return ('같이 보기: '+' · '.join(f'<a href="{u}" style="color:var(--skyris)">{n}</a>' for n,u in items)) if items else ''
for body,out,name in [('_src/bonemeal.body.html','bonemeal-works.html','뼛가루 공장'),('_src/apricorn.body.html','apricorn-orchard.html','규토리 과수원'),('_src/food.body.html','food-works.html','음식 공장'),('_src/kitchen.body.html','home-kitchen.html','생활 주방'),('_src/master.body.html','factory-campus.html','메이뷰 공장 단지')]:
    t=open(body,encoding='utf8').read().replace('{{STYLE}}',style).replace('{{LINKS}}',L(name))
    t=re.sub(r'\{\{L:(.+?)\}\}',lambda m:(f'<a href="{links[m.group(1)]}">상세 도면 →</a>' if m.group(1) in links else ''),t)
    open(out,'w',encoding='utf8').write(t)
print('ok')
