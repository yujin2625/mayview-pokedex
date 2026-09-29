import re
p='skyris-factory.html'; s=open(p,encoding='utf8').read()
a=' 톱이 원목도 판자로 잘라 준다면(EMI에서 톱 레시피 확인) 이 칸도 톱으로 바꿔 한 줄로 끝낼 수 있습니다.</td></tr>'
assert a in s; s=s.replace(a,' 기계식 톱은 스카이리스 원목을 판자로 자르지 못합니다(게임에서 확인). 원목 → 판자는 조합기, 판자 → 계단은 톱으로 나눕니다.</td></tr>')
s=re.sub(r'<li><input type="checkbox" id="c7">.*?</li>\n    ','',s,flags=re.S)
assert 'id="c7"' not in s
tower='''
<!-- A-2 TOWER -->
<section class="sheet" id="tower">
  <div class="sheet-head"><span class="sheet-no">A-2</span><h2>수직 확장 (타워형)</h2><span class="sub">강제 로드 4청크로 포드 20개</span></div>
  <p>청크 강제 로드는 그 청크의 맨 아래부터 맨 위까지 전부 로드하므로, 포드를 옆으로 늘리지 않고 위로 쌓으면 청크를 거의 쓰지 않습니다. 2×2청크 발판에 층마다 포드 4개를 넣고, 나무 높이(최대 약 37칸)에 설비층 6칸을 더해 <b>층 높이 45칸</b>으로 잡으면 지면 위로 5층, 포드 20개가 들어갑니다. 가로 배치에서 24청크가 들던 규모입니다.</p>
  <div class="two">
    <figure class="frame" style="margin:0"><svg id="towerSvg" role="img" aria-label="타워 입면도"></svg>
      <figcaption class="muted mono" style="font-size:11.5px;text-align:center;margin-top:6px">A-2 입면도 · 지면 Y=64 기준 예시</figcaption></figure>
    <figure class="frame" style="margin:0"><svg id="floorSvg" role="img" aria-label="타워 한 층 평면도"></svg>
      <figcaption class="muted mono" style="font-size:11.5px;text-align:center;margin-top:6px">A-3 한 층 평면도 · 32×32 · 포드 4 + 가운데 코어</figcaption></figure>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>항목</th><th>가로 배치 (A-1)</th><th>타워 배치 (A-2)</th></tr></thead>
    <tbody>
      <tr><td>포드 20개 강제 로드</td><td class="mono">24청크</td><td class="mono">4청크 (가공동 포함)</td></tr>
      <tr><td>포드 방향</td><td>모두 같은 방향, 척추가 남쪽</td><td>층마다 4개를 대칭으로 두고 통로가 가운데 십자로 모이게</td></tr>
      <tr><td>원목 이동</td><td>본선 벨트 16칸 × 구간 수</td><td>코어의 수직 슈트로 떨어뜨림. 층마다 깔때기로 슈트 옆에 넣기만 하면 됩니다</td></tr>
      <tr><td>뼛가루 공급</td><td>척추에 비료 벨트 1줄</td><td>위로 올려야 함: Create 6 패키지(체인 컨베이어 연결당 32칸) + 층별 프로그포트, 또는 AE2</td></tr>
      <tr><td>사람 이동</td><td>척추 통로를 걸어서</td><td>코어의 엘리베이터(Elevator 모드) 또는 사다리</td></tr>
      <tr><td>시공량</td><td>포드마다 바닥 1장</td><td>층마다 바닥·벽·천장 조명. 32×32×45 공간을 감싸는 벽이 필요해 재료가 더 듭니다</td></tr>
      <tr><td>확장 한계</td><td>강제 로드 25청크</td><td>월드 높이. 지면 위 5층, 땅을 파 내려가면 더</td></tr>
    </tbody>
  </table></div>
  <div class="note gold"><b>층 높이를 줄이면</b><span>천장이 낮아도 묘목은 자라려고 하지만, 키 큰 모양이 뽑히면 공간이 막혀 실패하고 뼛가루만 씁니다. 다음 시도에서 다른 모양이 나오면 자라므로 층을 35칸 정도로 줄여 6층을 만드는 것도 가능합니다. 대신 원목이 적은 작은 나무 비율이 늘어납니다. 시험 포드에서 확인한 뒤 정하세요.</span></div>
  <div class="note"><b>밝기와 몹</b><span>층이 완전히 막혀 어두워지므로 천장(S+38) 줄에 조명을 촘촘히 넣습니다. 뼛가루 성장은 밝기와 상관없지만, 어두우면 층 안에 몹이 생깁니다.</span></div>
</section>
'''
anchor='<!-- B POD -->'
assert anchor in s; s=s.replace(anchor,tower+'\n'+anchor,1)
js=r'''
/* ---------- A-2 TOWER ---------- */
(function(){
  const s=document.getElementById('towerSvg');
  const k=1.25, W=380, ox=62, base=64, top=320, H=(top-base+20)*k+40;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('width',W);s.setAttribute('height',H);
  const Y=y=>20+(top-y)*k;
  const w=32*4.2, x0=ox+30;
  s.append(el('rect',{x:ox-10,y:Y(base),width:W-ox,height:18,fill:V('c-dirt'),opacity:.5}));
  s.append(el('text',{x:ox-14,y:Y(base)+4,'text-anchor':'end','font-size':9,class:'mono',fill:V('muted')},'Y64'));
  s.append(el('rect',{x:x0,y:Y(base+12),width:w,height:12*k,fill:V('c-vault'),stroke:V('ink')}));
  s.append(el('text',{x:x0+w/2,y:Y(base+6)+4,'text-anchor':'middle','font-size':10,'font-weight':700,fill:V('panel')},'가공동 + AFK'));
  for(let f=0;f<5;f++){
    const S=82+45*f;
    s.append(el('rect',{x:x0,y:Y(S-1),width:w,height:5*k,fill:V('c-stone'),stroke:V('ink'),'stroke-width':.6}));
    s.append(el('rect',{x:x0,y:Y(S+38),width:w,height:38*k,fill:V('c-glass'),'fill-opacity':.12,stroke:V('ink'),'stroke-width':.6}));
    [x0+w*.25,x0+w*.75].forEach(cx=>{
      s.append(el('rect',{x:cx-2,y:Y(S+20),width:4,height:20*k,fill:V('c-log')}));
      s.append(el('ellipse',{cx,cy:Y(S+26),rx:w*.2,ry:11*k,fill:V('c-leaf'),opacity:.8}));
    });
    s.append(el('text',{x:ox-14,y:Y(S)+4,'text-anchor':'end','font-size':9,class:'mono',fill:V('muted')},'S='+S));
    s.append(el('text',{x:x0+w+8,y:Y(S+20),'font-size':10,fill:V('ink')},(f+1)+'층 · 포드 4'));
  }
  s.append(el('rect',{x:x0+w/2-4,y:Y(82+45*4+38),width:8,height:(82+45*4+38-(base+12))*k,fill:V('c-belt'),opacity:.85}));
  s.append(el('line',{x1:x0+w/2-1,y1:Y(290),x2:x0+w/2-1,y2:Y(base+14),stroke:V('skyris'),'stroke-width':2,class:'flowdash'}));
  s.append(el('text',{x:x0+w+8,y:Y(base+18),'font-size':9.5,fill:V('skyris')},'↓ 원목 슈트'));
  s.append(el('text',{x:x0+w+8,y:Y(base+30),'font-size':9.5,fill:V('gold')},'↑ 뼛가루 패키지'));
  s.append(el('text',{x:ox-14,y:Y(top)+4,'text-anchor':'end','font-size':9,class:'mono',fill:V('muted')},'Y320'));
  s.append(el('line',{x1:ox-8,y1:Y(top),x2:W-6,y2:Y(top),stroke:V('bloom'),'stroke-dasharray':'4 3'}));
  s.append(el('text',{x:W-8,y:Y(top)-4,'text-anchor':'end','font-size':9.5,fill:V('bloom')},'월드 최고 높이'));
})();
(function(){
  const s=document.getElementById('floorSvg');
  const C=10, ox=16, oy=16, N=32, W=ox+N*C+16, H=oy+N*C+30;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('width',W);s.setAttribute('height',H);
  [[0,0],[16,0],[0,16],[16,16]].forEach(([qx,qz])=>{
    s.append(el('rect',{x:ox+qx*C,y:oy+qz*C,width:16*C,height:16*C,fill:V('c-stone'),stroke:V('ink'),'stroke-width':1}));
    const gx=qx===0?0:1, gz=qz===0?0:1;
    s.append(el('rect',{x:ox+(qx+gx)*C,y:oy+(qz+gz)*C,width:15*C,height:15*C,fill:V('c-leaf'),'fill-opacity':.3,stroke:V('c-glass'),'stroke-width':2}));
    const cx=qx+gx+7, cz=qz+gz+7;
    s.append(el('circle',{cx:ox+(cx+.5)*C,cy:oy+(cz+.5)*C,r:7.5*C,fill:'none',stroke:V('skyris'),'stroke-dasharray':'4 3'}));
    s.append(el('rect',{x:ox+cx*C,y:oy+cz*C,width:C,height:C,fill:V('c-dirt')}));
  });
  s.append(el('rect',{x:ox+15*C,y:oy,width:2*C,height:N*C,fill:V('c-walk'),opacity:.9}));
  s.append(el('rect',{x:ox,y:oy+15*C,width:N*C,height:2*C,fill:V('c-walk'),opacity:.9}));
  s.append(el('rect',{x:ox+15*C,y:oy+15*C,width:2*C,height:2*C,fill:V('c-belt'),stroke:V('ink')}));
  s.append(el('text',{x:ox+16*C,y:oy+N*C+18,'text-anchor':'middle','font-size':10.5,fill:V('muted')},'가운데 2×2 코어: 슈트 · 엘리베이터 · 체인 컨베이어'));
})();
'''
anchor2='/* ---------- E-1 CALC ---------- */'
assert anchor2 in s; s=s.replace(anchor2,js+anchor2,1)
a='포드는 척추 벨트 1구간 + 동력축 1구간만 이어 붙이면 됩니다.</span></div>'
assert a in s; s=s.replace(a,'포드는 척추 벨트 1구간 + 동력축 1구간만 이어 붙이면 됩니다. 강제 로드가 모자라면 A-2 타워형으로 가세요. 4청크 안에 같은 포드 20개가 들어갑니다.</span></div>')
s=s.replace('<div>도면</div><div>설계도 세트 A–G (7장)</div>','<div>도면</div><div>설계도 세트 A–G (8장)</div>')
s=s.replace('G-1 검증 후 계산기 가정을 조정하세요.</span>','G-1 검증 후 계산기 가정을 조정하세요.</span>\n  <span>{{XLINKS}}</span>',1)
open(p,'w',encoding='utf8').write(s)
print('ok')
