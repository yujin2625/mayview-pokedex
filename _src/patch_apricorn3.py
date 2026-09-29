p='_src/apricorn.body.html'; s=open(p,encoding='utf8').read()
def rep(a,b):
    global s
    assert a in s, a[:70]; s=s.replace(a,b,1)
A=lambda c,n:f'<span class="apr" style="background:{c}"></span>{n}'
R,B,K,Y,G,W=('#d9463b','빨'),('#3d6fd1','파'),('#2a2a2a','검'),('#e6c229','노'),('#4c9a4a','초'),('#f2f2ee','하')
ap=lambda *p:' '.join(A(c[0],f'{c[1]}{n}') for c,n in p)

rep('색깔별 창고에 모아 포획 배율 2배 이상인 볼만 만드는 데 쓰고,','색깔별 창고에 모아 하이퍼볼·루어볼·타이머볼·퀵볼을 3:2:2:1로 만들고,')
rep('<span>규토리 4개 + 주괴(철·금·다이아) 1 → 볼 4개. 2배 이상 볼 19종 기준</span>','<span>규토리 4개 + 주괴 1 → 볼 4개. 하이퍼·루어·타이머·퀵 = 3:2:2:1</span>')
rep('<span>색깔별 창고. 2배 이상 볼만 조합합니다.</span>','<span>색깔별 창고. 볼 4종을 3:2:2:1로 조합합니다.</span>')

start=s.index('<div class="tbl"><table>\n    <thead><tr><th>볼</th><th>배율</th>'); end=s.index('</table></div>',start)+len('</table></div>')
rows=[('하이퍼볼','3','2배','항상',ap((K,2),(Y,2)),'금'),
      ('루어볼','2','4배','낚싯대로 낚은 포켓몬',ap((R,1),(B,2),(G,1)),'철'),
      ('타이머볼','2','최대 4배','턴마다 약 0.3배씩 누적',ap((R,1),(W,2),(K,1)),'금'),
      ('퀵볼','1','5배','배틀 첫 턴',ap((B,2),(Y,2)),'금')]
t='<div class="tbl"><table>\n    <thead><tr><th>볼</th><th>비율</th><th>배율</th><th>조건</th><th>규토리 (조합 1회)</th><th>주괴</th></tr></thead>\n    <tbody>\n'
t+='\n'.join(f'      <tr><td>{a}</td><td class="mono">{b}</td><td class="mono">{c}</td><td>{d}</td><td>{e}</td><td>{f}</td></tr>' for a,b,c,d,e,f in rows)
t+='\n      <tr><td colspan="6" class="muted">한 바퀴(조합 8회) = 하이퍼 12 · 루어 8 · 타이머 8 · 퀵 4 = 볼 32개. 규토리 32개, 금 주괴 6개, 철 주괴 2개. 다른 2배 이상 볼(다크볼, 네트볼, 다이브볼 등)은 필요할 때 손으로 만드세요.</td></tr>\n    </tbody>\n  </table></div>'
s=s[:start]+t+s[end:]

start=s.index('<h3>D-2 색 배분'); end=s.index('</table></div>',start)+len('</table></div>')
alloc='''<h3>D-2 색 배분 (모듈 1개 = 252자리)</h3>
  <p>3:2:2:1 한 바퀴에 검정 8, 노랑 8, 파랑 6, 빨강 4, 하양 4, 초록 2개가 들어갑니다(분홍은 안 씀). 이 비율로 252자리를 나누면 아래와 같습니다. 벽 한 면이 42자리라, 검정·노랑은 한 면 반씩 차지합니다.</p>
  <div class="tbl"><table>
    <thead><tr><th>색</th><th>한 바퀴</th><th>자리</th><th>쓰는 볼</th></tr></thead>
    <tbody>
      <tr><td><span class="apr" style="background:#2a2a2a"></span>검정</td><td class="mono">8</td><td class="mono">63</td><td>하이퍼볼, 타이머볼</td></tr>
      <tr><td><span class="apr" style="background:#e6c229"></span>노랑</td><td class="mono">8</td><td class="mono">63</td><td>하이퍼볼, 퀵볼</td></tr>
      <tr><td><span class="apr" style="background:#3d6fd1"></span>파랑</td><td class="mono">6</td><td class="mono">47</td><td>루어볼, 퀵볼</td></tr>
      <tr><td><span class="apr" style="background:#d9463b"></span>빨강</td><td class="mono">4</td><td class="mono">32</td><td>루어볼, 타이머볼</td></tr>
      <tr><td><span class="apr" style="background:#f2f2ee"></span>하양</td><td class="mono">4</td><td class="mono">31</td><td>타이머볼</td></tr>
      <tr><td><span class="apr" style="background:#4c9a4a"></span>초록</td><td class="mono">2</td><td class="mono">16</td><td>루어볼</td></tr>
    </tbody>
  </table></div>'''
s=s[:start]+alloc+s[end:]

rep('가장 많이 쓰는 3~4종(예: 하이퍼볼·퀵볼·다크볼·리피트볼)만 자동 세트를 두고, 나머지는 색깔 창고에서 꺼내 손으로 조합하세요.',
    '하이퍼볼·루어볼·타이머볼·퀵볼 4세트를 둡니다. 세트끼리 같은 색(검정·노랑·파랑·빨강)을 나눠 쓰므로, 비율은 볼 상자마다 문턱 스위치로 맞춥니다. 예를 들어 하이퍼볼 3세트분, 루어·타이머 2세트분, 퀵볼 1세트분이 차면 그 조합기의 팔을 멈추게 하면 됩니다.')
rep(" 고대 볼의 텀블스톤은 Cobbleworkers 텀블스톤 채집 포켓몬으로 모을 수 있습니다.","")
rep("[['하이퍼볼',140],['퀵볼',300],['다크볼',460]]","[['하이퍼 3',70],['루어 2',230],['타이머 2',390],['퀵 1',550]]")
rep("const cols=Object.entries(COL);","const cols=Object.entries(COL).filter(([k])=>k!=='pink');")
rep('<li>지하 벨트, 7색 분류, 자주 쓰는 볼 3~4종 자동 조합기</li>','<li>지하 벨트, 6색 분류, 볼 4종 자동 조합기</li>')
rep("`한 시간 동안 규토리 ${fmt(apr)}개. 전부 볼로 만들면 약 ${fmt(apr)}개이고, 주괴(철·금·다이아)가 ${fmt(apr/4)}개 필요합니다.",
    "`한 시간 동안 규토리 ${fmt(apr)}개 → 하이퍼볼 ${fmt(apr*12/32)} · 루어볼 ${fmt(apr*8/32)} · 타이머볼 ${fmt(apr*8/32)} · 퀵볼 ${fmt(apr*4/32)}개. 금 주괴 ${fmt(apr*6/32)}개, 철 주괴 ${fmt(apr*2/32)}개가 필요합니다.")
# plan colors: mix slots use white/green instead of pink
rep("const mix=['pink','green','white'];","const mix=['white','green','white'];")
rep("APR[x]==='mix'?COL.pink[0]","APR[x]==='mix'?COL.white[0]")
rep("const WALLS=[1,6,11], APR={0:'red',2:'red',5:'blue',7:'black',10:'yellow',12:'mix'};","const WALLS=[1,6,11], APR={0:'black',2:'yellow',5:'black',7:'yellow',10:'blue',12:'mix'};")
open(p,'w',encoding='utf8').write(s); print('ok')
