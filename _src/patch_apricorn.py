import re
p='_src/apricorn.body.html'; s=open(p,encoding='utf8').read()
def rep(a,b):
    global s
    assert a in s, a[:60]; s=s.replace(a,b,1)

rep('<p>7색 규토리 나무를 1청크 모듈에 심고, 목장(파스처)에 둔 벌레 타입 포켓몬이 열매를 따서 상자에 넣습니다.',
    '<p>나무를 키우지 않고, 가위로 얻은 규토리 잎을 벽처럼 쌓아 양쪽 면에 씨앗을 우클릭해 열매를 답니다. 목장(파스처)에 둔 벌레 타입 포켓몬이 익은 열매를 따서 상자에 넣습니다.')
rep('<div class="ratio"><b class="s">나무는 남김</b><span>익은 규토리를 따면 열매 블록이 0단계로 돌아가고 나무는 그대로. 베지 않는 과수원</span></div>',
    '<div class="ratio"><b class="s">잎 1 = 열매 2</b><span>열매는 잎 옆면(동서남북)에 붙습니다. 1칸 두께 잎 벽이면 잎마다 양쪽 2개. 따면 0단계로 돌아가 다시 자람</span></div>')
rep('<li><b>재배</b><span>7색 나무 8그루(빨강 2). 열매가 익기를 기다립니다.</span><span class="io">씨앗 → 나무</span></li>',
    '<li><b>심기</b><span>잎 벽 양쪽 면에 씨앗을 우클릭. 색은 씨앗 색으로 정해지므로 필요한 비율대로 심습니다.</span><span class="io">씨앗 → 잎 옆 열매</span></li>')

# replace plan section
start=s.index('<section class="sheet" id="plan">'); end=s.index('</section>',start)+len('</section>')
plan='''<section class="sheet" id="plan">
  <div class="sheet-head"><span class="sheet-no">C-1 · C-2</span><h2>잎 벽 모듈</h2><span class="sub">1청크(16×16) · 목장 1 · 열매 자리 252</span></div>
  <p>잎 벽(두께 1, 높이 3, 길이 14) 3줄을 5칸 간격으로 세웁니다. 벽 양쪽에 열매가 붙고, 열매 사이에는 포켓몬이 다닐 2칸 통로가 남습니다. 목장은 가운데 통로에 두어 모든 벽이 수확 반경 8 안에 들어오게 합니다. 벽 양 끝(z=0, z=15)은 통로를 서로 잇는 길로 비워 둡니다.</p>
  <div class="two">
    <figure class="frame" style="margin:0"><svg id="planSvg" role="img" aria-label="잎 벽 모듈 평면도"></svg>
      <figcaption class="muted mono" style="font-size:11.5px;text-align:center;margin-top:6px">C-1 평면도 · 16×16</figcaption></figure>
    <figure class="frame" style="margin:0"><svg id="secSvg" role="img" aria-label="잎 벽 모듈 단면도"></svg>
      <figcaption class="muted mono" style="font-size:11.5px;text-align:center;margin-top:6px">C-2 단면도 · 벽을 가로로 자른 면 · 2층 적층</figcaption></figure>
  </div>
  <div class="legend" id="aprLegend"></div>
  <div class="tbl"><table>
    <thead><tr><th>부품</th><th>위치</th><th>설정·메모</th></tr></thead>
    <tbody>
      <tr><td>규토리 잎 벽 ×3</td><td class="mono">x = 1, 6, 11 · z 1–14 · G+1–G+3</td><td>규토리 나무 잎을 가위나 섬세한 손길로 캐서 쌓습니다. 직접 놓은 잎은 사라지지 않습니다. 벽 하나 42칸 × 양면 = 열매 84.</td></tr>
      <tr><td>열매 자리</td><td class="mono">x = 0, 2, 5, 7, 10, 12</td><td>씨앗 우클릭. 모듈 합계 252. 색 배분은 D-1 표 참고.</td></tr>
      <tr><td>목장(파스처)</td><td class="mono">8, G+1, 8</td><td>가운데 통로. 포켓몬 최대 16마리, 청크당 2개까지.</td></tr>
      <tr><td>통 ×2</td><td class="mono">(8,7), (8,9)</td><td>목장 바로 옆. 수확물이 들어오면 아래 깔때기로 지하 벨트에.</td></tr>
      <tr><td>지하 벨트</td><td class="mono">G−1</td><td>통 → 창고. 층을 쌓으면 슈트로 아래층 벨트에 떨어뜨립니다.</td></tr>
      <tr><td>천장 조명</td><td class="mono">G+4</td><td>층을 쌓으면 윗층 바닥이 천장. 조명은 통로 위에만 달아 열매 자리를 막지 않게.</td></tr>
    </tbody>
  </table></div>
</section>'''
s=s[:start]+plan+s[end:]

# color allocation table + calc into store section (after the ball table)
rep('''  <div class="note"><b>자동 볼 조합</b>''','''  <h3>D-2 색 배분 (모듈 1개 = 252자리)</h3>
  <div class="tbl"><table>
    <thead><tr><th>색</th><th>자리</th><th>이유</th></tr></thead>
    <tbody>
      <tr><td><span class="apr" style="background:#d9463b"></span>빨강</td><td class="mono">84 (벽 1줄)</td><td>몬스터볼 4개, 슈퍼볼 2개씩 들어가 가장 많이 씀</td></tr>
      <tr><td><span class="apr" style="background:#3d6fd1"></span>파랑</td><td class="mono">42</td><td>슈퍼볼</td></tr>
      <tr><td><span class="apr" style="background:#2a2a2a"></span>검정 · <span class="apr" style="background:#e6c229"></span>노랑</td><td class="mono">42 · 42</td><td>하이퍼볼</td></tr>
      <tr><td><span class="apr" style="background:#e58bb6"></span>분홍 · <span class="apr" style="background:#4c9a4a"></span>초록 · <span class="apr" style="background:#f2f2ee"></span>하양</td><td class="mono">14 · 14 · 14</td><td>특수볼·주스용. 필요하면 벽 한 면을 통째로 바꿔 심으면 됩니다</td></tr>
    </tbody>
  </table></div>
  <div class="calc">
    <div class="calc-in">
      <label for="mods">모듈(층) 수 <span class="mono" id="modsOut">2</span><input type="range" id="mods" min="1" max="6" value="2"></label>
      <label for="ripe">열매 1개가 익는 평균 시간(분)<input type="number" id="ripe" min="5" max="120" value="30"></label>
      <p class="muted" style="font-size:12px">익는 시간은 모드 파일로 확인하지 못한 추정값입니다. 한 번 심고 시계로 재서 넣으세요. 플레이어가 근처에 있는 시간 기준입니다.</p>
    </div>
    <div class="calc-out" aria-live="polite">
      <div class="kpis">
        <div class="kpi"><small>열매 자리</small><b id="kSlots">–</b></div>
        <div class="kpi"><small>규토리/시간</small><b id="kApr">–</b></div>
        <div class="kpi"><small>씨앗/시간</small><b id="kSeed">–</b></div>
        <div class="kpi"><small>몬스터볼 환산/시간</small><b id="kBall">–</b></div>
        <div class="kpi g"><small>전부 팔 때 금화/시간</small><b id="kGold">–</b></div>
        <div class="kpi"><small>필요 포켓몬(추정)</small><b id="kMon">–</b></div>
      </div>
      <p class="status" id="aStatus">–</p>
    </div>
  </div>
  <div class="note"><b>자동 볼 조합</b>''')

# expansion section
start=s.index('<section class="sheet">',s.index('id="store"')); end=s.index('</section>',start)+len('</section>')
exp='''<section class="sheet">
  <div class="sheet-head"><span class="sheet-no">E-1</span><h2>확장과 검증</h2><span class="sub">층 쌓기 → 옆 청크</span></div>
  <div class="phases">
    <div class="phase"><span class="tag">1단계</span><h3>잎 벽 1줄</h3><ul><li>잎 42칸, 씨앗 84개</li><li>목장 1, 통 2</li><li>포켓몬 수확 확인</li></ul></div>
    <div class="phase"><span class="tag">2단계</span><h3>모듈 완성 + 창고</h3><ul><li>벽 3줄, 252자리</li><li>지하 벨트, 7색 분류, 볼 조합기</li><li>잉여 판매 라인</li></ul></div>
    <div class="phase"><span class="tag">3단계</span><h3>위로 한 층</h3><ul><li>층 높이 5 (바닥 1 + 벽 3 + 조명 1)</li><li>청크당 목장 2개 제한 → 한 청크에 2층까지</li><li>더 늘릴 땐 옆 청크에 같은 2층 모듈</li></ul></div>
  </div>
  <div class="note"><b>위아래 확장의 한계</b><span>수확 높이가 목장에서 위아래 5칸이라 층마다 목장이 하나씩 필요합니다. 그런데 이 팩은 목장을 청크당 2개까지만 허용하므로 한 청크 기둥에는 2층까지만 쌓입니다. 포켓몬이 움직이는 범위(플레이어에게서 수직 32칸)보다 이 제한이 먼저 걸립니다.</span></div>
  <ul class="checks" id="checkList">
    <li><input type="checkbox" id="a1"><label for="a1"><span>Cobbleworkers 포켓몬이 수확물을 목장 옆 통에 넣는가<small>다른 상자로 가면 그 상자 아래에 깔때기를 답니다.</small></span></label></li>
    <li><input type="checkbox" id="a2"><label for="a2"><span>2칸 통로에서 포켓몬이 벽 끝까지 가서 따는가<small>큰 포켓몬이 끼면 작은 벌레 타입으로 바꾸거나 통로를 3칸으로 넓힙니다(벽 2줄로 줄어듦).</small></span></label></li>
    <li><input type="checkbox" id="a3"><label for="a3"><span>벽 맨 위 칸(G+3) 열매도 수확되는가<small>안 되면 벽 높이를 2로 줄이고 층 높이도 4로.</small></span></label></li>
    <li><input type="checkbox" id="a4"><label for="a4"><span>수확할 때 씨앗도 나오는가<small>안 나오면 씨앗 줄은 빼세요.</small></span></label></li>
    <li><input type="checkbox" id="a5"><label for="a5"><span>열매 1개가 익는 시간 측정<small>재서 계산기에 넣으세요.</small></span></label></li>
  </ul>
</section>'''
s=s[:start]+exp+s[end:]

rep('(열매 블록 전리품: 3단계에서 규토리 1 + 씨앗 10%, 볼 조합법, 규토리 블록 뼛가루 적용 가능)',
    '(열매 블록: 가로 방향 4면, 3단계에서 규토리 1 + 씨앗 10%, 뼛가루 적용 가능 · 잎: 가위·섬세한 손길로 획득 · 볼 조합법)')

# replace plan script
start=s.index('/* plan */'); end=s.index('/* store */')
js=r'''/* plan */
const WALLS=[1,6,11], APR={0:'red',2:'red',5:'blue',7:'black',10:'yellow',12:'mix'};
(function(){
  const s=document.getElementById('planSvg');
  const C=20, N=16, ox=26, oy=18, W=ox+N*C+14, H=oy+N*C+28;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('width',W);s.setAttribute('height',H);
  const mix=['pink','green','white'];
  for(let x=0;x<N;x++)for(let z=0;z<N;z++){
    let f=V('c-stone'), op=1;
    if(WALLS.includes(x)&&z>=1&&z<=14) f=V('c-leaf');
    s.append(el('rect',{x:ox+x*C,y:oy+z*C,width:C,height:C,fill:f,stroke:V('grid'),'stroke-width':.6}));
    if(APR[x]!==undefined&&z>=1&&z<=14){
      const c=APR[x]==='mix'?mix[(z-1)%3]:APR[x];
      s.append(el('circle',{cx:ox+x*C+C/2,cy:oy+z*C+C/2,r:6,fill:COL[c][0],stroke:V('ink'),'stroke-width':.8}));
    }
  }
  s.append(el('rect',{x:ox+8*C,y:oy+8*C,width:C,height:C,fill:V('c-dep'),stroke:V('ink')}));
  s.append(el('text',{x:ox+8*C+C/2,y:oy+8*C+C/2+4,'text-anchor':'middle','font-size':10,'font-weight':700,fill:V('panel')},'목'));
  [7,9].forEach(z=>{s.append(el('rect',{x:ox+8*C,y:oy+z*C,width:C,height:C,fill:V('c-hopper'),stroke:V('ink')}));s.append(el('text',{x:ox+8*C+C/2,y:oy+z*C+C/2+4,'text-anchor':'middle','font-size':10,'font-weight':700,fill:V('panel')},'통'))});
  s.append(el('rect',{x:ox,y:oy,width:16*C,height:16*C,fill:'none',stroke:V('diamond'),'stroke-width':1.5,'stroke-dasharray':'6 4'}));
  [[3.5,'통로'],[8.5,'통로'],[13.5,'통로']].forEach(([x,t])=>s.append(el('text',{x:ox+x*C+C/2,y:oy+15*C+14,'text-anchor':'middle','font-size':9.5,fill:V('muted')},t)));
  s.append(el('text',{x:ox,y:oy+N*C+22,'font-size':10.5,fill:V('muted')},'초록 칸 = 잎 벽(높이 3) · 원 = 열매 자리 · 점선 = 수확 반경 8'));
})();
(function(){
  const s=document.getElementById('secSvg');
  const C=20, N=16, ox=40, oy=16, rows=11, W=ox+N*C+14, H=oy+rows*C+28;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('width',W);s.setAttribute('height',H);
  const Y=r=>oy+r*C;
  const layer=(base,tag)=>{
    for(let x=0;x<N;x++) s.append(el('rect',{x:ox+x*C,y:Y(base+4),width:C,height:C,fill:V('c-stone'),stroke:V('grid'),'stroke-width':.6}));
    for(let h=1;h<=3;h++){
      WALLS.forEach(x=>s.append(el('rect',{x:ox+x*C,y:Y(base+4-h),width:C,height:C,fill:V('c-leaf'),stroke:V('grid'),'stroke-width':.6})));
      Object.keys(APR).forEach(x=>s.append(el('circle',{cx:ox+x*C+C/2,cy:Y(base+4-h)+C/2,r:5.5,fill:APR[x]==='mix'?COL.pink[0]:COL[APR[x]][0],stroke:V('ink'),'stroke-width':.7})));
    }
    s.append(el('rect',{x:ox+8*C,y:Y(base+3),width:C,height:C,fill:V('c-dep'),stroke:V('ink')}));
    [3.5,8.5,13.5].forEach(x=>s.append(el('rect',{x:ox+x*C+4,y:Y(base)+6,width:C-8,height:5,fill:V('gold'),opacity:.8})));
    s.append(el('text',{x:ox-6,y:Y(base+2)+4,'text-anchor':'end','font-size':9.5,fill:V('muted')},tag));
  };
  layer(0,'2층'); layer(5,'1층');
  s.append(el('rect',{x:ox,y:Y(10),width:N*C,height:C*.5,fill:V('c-belt')}));
  s.append(el('text',{x:ox,y:Y(10)+C+6,'font-size':10.5,fill:V('muted')},'층 높이 5 · 노란 막대 = 통로 위 조명 · 맨 아래 = 지하 벨트'));
})();
/* calc */
(function(){
  const $=id=>document.getElementById(id);
  const fmt=n=>n>=100?Math.round(n).toLocaleString('ko-KR'):(Math.round(n*10)/10).toLocaleString('ko-KR');
  function calc(){
    const m=+$('mods').value, t=Math.max(5,+$('ripe').value||30);
    $('modsOut').textContent=m;
    const slots=252*m, apr=slots*60/t;
    $('kSlots').textContent=fmt(slots);$('kApr').textContent=fmt(apr);$('kSeed').textContent=fmt(apr*.1);
    $('kBall').textContent=fmt(apr);$('kGold').textContent=fmt(apr/128);
    $('kMon').textContent=Math.ceil(apr/300)*m>0?Math.min(16*m,Math.max(3*m,Math.ceil(apr/300))):'–';
    $('aStatus').textContent=`한 시간 동안 규토리 ${fmt(apr)}개. 전부 몬스터볼로 만들면 약 ${fmt(apr)}개(규토리 4 + 구리 1 → 볼 4, 구리 주괴 ${fmt(apr/4)}개 필요). 전부 팔면 금화 ${fmt(apr/128)}개라 스카이리스 포드 1개(뼛가루 모드 시간당 약 300 금화)에 한참 못 미칩니다. 쓰는 용도로 두고 남는 것만 파세요.`;
  }
  ['mods','ripe'].forEach(id=>$(id).addEventListener('input',calc));calc();
})();
'''
s=s[:start]+js+s[end:]
open(p,'w',encoding='utf8').write(s); print('ok')
