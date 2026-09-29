import re
p='_src/apricorn.body.html'; s=open(p,encoding='utf8').read()
def rep(a,b,count=1):
    global s
    assert a in s, a[:70]; s=s.replace(a,b,count)

rep('색깔별 창고에 모아 몬스터볼 재료로 쓰고,','색깔별 창고에 모아 포획 배율 2배 이상인 볼만 만드는 데 쓰고,')
rep('<div class="ratio"><b class="g">규토리 1 = 볼 1</b><span>같은 색 4개 + 주괴 1 → 볼 4개 (몬스터볼: 빨강 + 구리)</span></div>',
    '<div class="ratio"><b class="g">규토리 1 = 볼 1</b><span>규토리 4개 + 주괴(철·금·다이아) 1 → 볼 4개. 2배 이상 볼 19종 기준</span></div>')
rep('<li class="dia"><b>자급</b><span>색깔별 창고. 볼 조합기가 여기서 꺼내 씁니다.</span><span class="io">규토리 4 + 주괴 → 볼 4</span></li>',
    '<li class="dia"><b>자급</b><span>색깔별 창고. 2배 이상 볼만 조합합니다.</span><span class="io">규토리 4 + 주괴 → 볼 4</span></li>')

# ball table
start=s.index('<div class="tbl"><table>\n    <thead><tr><th>볼</th><th>규토리</th>'); end=s.index('</table></div>',start)+len('</table></div>')
A=lambda c,n:f'<span class="apr" style="background:{c}"></span>{n}'
R,B,K,Y,P,G,W=[('#d9463b','빨'),('#3d6fd1','파'),('#2a2a2a','검'),('#e6c229','노'),('#e58bb6','분'),('#4c9a4a','초'),('#f2f2ee','하')]
def ap(*pairs): return ' '.join(A(c[0],f'{c[1]}{n}') for c,n in pairs)
rows=[
 ('하이퍼볼','2배','항상',ap((K,2),(Y,2)),'금'),
 ('퀵볼','5배','배틀 첫 턴',ap((B,2),(Y,2)),'금'),
 ('러브볼','8배 / 2.5배','같은 종·다른 성별 / 다른 종·다른 성별',ap((W,1),(P,3)),'금'),
 ('다크볼','3.5배 / 3배','밝기 0 / 밝기 1–7',ap((G,2),(K,2)),'금'),
 ('리피트볼','3.5배','도감에 이미 있는 포켓몬',ap((K,1),(R,2),(Y,1)),'금'),
 ('타이머볼','최대 4배','턴이 지날수록 약 0.3배씩',ap((R,1),(W,2),(K,1)),'금'),
 ('드림볼','4배','잠든 포켓몬',ap((R,1),(P,2),(B,1)),'다이아'),
 ('스피드볼','4배','기본 스피드 100 이상',ap((R,1),(Y,2),(W,1)),'철'),
 ('루어볼','4배','낚싯대로 낚은 포켓몬',ap((R,1),(B,2),(G,1)),'철'),
 ('다이브볼','3.5배','물속에 있는 포켓몬',ap((W,1),(B,3)),'철'),
 ('넷볼','3배','벌레·물 타입',ap((K,1),(B,2),(W,1)),'철'),
 ('파크볼','2.5배','숲·평원 바이옴',ap((R,1),(G,3)),'철'),
 ('레벨볼','1–4배','내 파티 레벨이 높을수록',ap((K,1),(P,2),(R,1)),'철'),
 ('헤비볼','1–4배','무거운 포켓몬일수록',ap((K,2),(B,2)),'철'),
 ('문볼','1–4배','밤, 보름달에 가까울수록',ap((Y,2),(B,1),(K,1)),'철'),
 ('네스트볼','1–4배','레벨 30보다 낮을수록',ap((G,2),(Y,2)),'철'),
 ('고대 하이퍼볼','2배','항상 · 텀블스톤 2',ap((Y,1),(K,1)),'금'),
 ('고대 제트볼','2배','멀리 던짐 · 하늘 텀블스톤 2',ap((B,1),(W,1)),'금'),
 ('고대 기가톤볼','2배','짧게 던짐 · 검은 텀블스톤 2',ap((K,2)),'금'),
]
tbl='<div class="tbl"><table>\n    <thead><tr><th>볼</th><th>배율</th><th>조건</th><th>규토리</th><th>주괴</th></tr></thead>\n    <tbody>\n'
tbl+='\n'.join(f'      <tr><td>{a}</td><td class="mono">{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>' for a,b,c,d,e in rows)
tbl+='\n      <tr><td colspan="5" class="muted">만들지 않음: 몬스터볼·색깔볼·프리미어볼(1배), 슈퍼볼·사파리볼·스포츠볼(1.5배), 프렌드·럭셔리·힐볼(1배, 부가 효과용), 고대 몬스터·슈퍼·페더·윙·헤비·레덴볼. 모두 한 조합에 볼 4개.</td></tr>\n    </tbody>\n  </table></div>'
s=s[:start]+tbl+s[end:]

# color allocation
start=s.index('<h3>D-2 색 배분'); end=s.index('</table></div>',start)+len('</table></div>')
alloc='''<h3>D-2 색 배분 (모듈 1개 = 252자리)</h3>
  <p>위 19종을 한 번씩 만들면 규토리가 검정 14, 파랑 14, 노랑 12, 빨강·초록 8, 하양·분홍 7개 들어갑니다. 이 비율대로 252자리를 나눴습니다. 자주 쓰는 볼이 정해지면(예: 하이퍼볼·퀵볼·다크볼 위주면 검정·노랑·파랑·초록) 그쪽으로 벽 한 면씩 바꿔 심으세요.</p>
  <div class="tbl"><table>
    <thead><tr><th>색</th><th>자리</th><th>많이 쓰는 볼</th></tr></thead>
    <tbody>
      <tr><td><span class="apr" style="background:#2a2a2a"></span>검정</td><td class="mono">50</td><td>하이퍼볼, 다크볼, 헤비볼, 고대 기가톤볼</td></tr>
      <tr><td><span class="apr" style="background:#3d6fd1"></span>파랑</td><td class="mono">50</td><td>퀵볼, 다이브볼, 넷볼, 루어볼</td></tr>
      <tr><td><span class="apr" style="background:#e6c229"></span>노랑</td><td class="mono">43</td><td>하이퍼볼, 퀵볼, 네스트볼, 스피드볼</td></tr>
      <tr><td><span class="apr" style="background:#d9463b"></span>빨강</td><td class="mono">29</td><td>리피트볼, 타이머볼, 드림볼</td></tr>
      <tr><td><span class="apr" style="background:#4c9a4a"></span>초록</td><td class="mono">29</td><td>다크볼, 파크볼, 네스트볼</td></tr>
      <tr><td><span class="apr" style="background:#f2f2ee"></span>하양</td><td class="mono">25</td><td>타이머볼, 다이브볼, 러브볼</td></tr>
      <tr><td><span class="apr" style="background:#e58bb6"></span>분홍</td><td class="mono">26</td><td>러브볼, 드림볼, 레벨볼</td></tr>
    </tbody>
  </table></div>'''
s=s[:start]+alloc+s[end:]

rep('볼 조합법은 3×3 가운데 십자 모양(위·왼쪽·오른쪽·아래가 규토리, 가운데가 주괴)이라 기계식 조합기 5대를 십자로 붙이면 됩니다. 볼 종류마다 한 세트씩 두고, 기계식 팔이 색깔 창고와 주괴 상자에서 꺼내 채웁니다.',
    '볼 조합법은 모두 3×3 가운데 십자 모양(위·왼쪽·오른쪽·아래가 규토리나 텀블스톤, 가운데가 주괴)입니다. 기계식 조합기 5대를 십자로 붙이면 되지만, 볼마다 칸별 재료 위치가 달라서 한 세트가 한 종류만 만듭니다. 가장 많이 쓰는 3~4종(예: 하이퍼볼·퀵볼·다크볼·리피트볼)만 자동 세트를 두고, 나머지는 색깔 창고에서 꺼내 손으로 조합하세요. 고대 볼의 텀블스톤은 Cobbleworkers 텀블스톤 채집 포켓몬으로 모을 수 있습니다.')
rep("[['몬스터볼',140],['슈퍼볼',300],['하이퍼볼',460]]","[['하이퍼볼',140],['퀵볼',300],['다크볼',460]]")
rep('<small>몬스터볼 환산/시간</small>','<small>볼 환산/시간</small>')
rep("`한 시간 동안 규토리 ${fmt(apr)}개. 전부 몬스터볼로 만들면 약 ${fmt(apr)}개(규토리 4 + 구리 1 → 볼 4, 구리 주괴 ${fmt(apr/4)}개 필요).",
    "`한 시간 동안 규토리 ${fmt(apr)}개. 전부 볼로 만들면 약 ${fmt(apr)}개이고, 주괴(철·금·다이아)가 ${fmt(apr/4)}개 필요합니다.")
rep('<li>지하 벨트, 7색 분류, 볼 조합기</li>','<li>지하 벨트, 7색 분류, 자주 쓰는 볼 3~4종 자동 조합기</li>')
rep('(열매 블록: 가로 방향 4면','(볼 조합법 전체, 열매 블록: 가로 방향 4면')
rep('<code>config/cobbleworkers.json</code>','포획 배율: Cobblemon 위키 · <code>config/cobbleworkers.json</code>')
open(p,'w',encoding='utf8').write(s); print('ok')
