p='_src/food.body.html'; s=open(p,encoding='utf8').read()
def rep(a,b):
    global s
    assert a in s, a[:70]; s=s.replace(a,b,1)

sheet='''
<section class="sheet" id="eff">
  <div class="sheet-head"><span class="sheet-no">A-2</span><h2>시간·공간 효율</h2><span class="sub">층 = 1청크 × 높이 4 · 플레이어가 근처에 있을 때</span></div>
  <p>원재료가 적게 드는 것과 층당 많이 버는 것은 다릅니다. 작물은 종류마다 수확량이 다르고, 서로 다른 작물을 한 줄씩 번갈아 심으면 성장이 2배 빨라지는 바닐라 규칙이 있어서 여러 작물이 들어가는 요리가 층당 효율에서 유리합니다. 아래는 작물 층 1개(경작지 210칸)가 시간당 버는 금화와, 비리디움 판매함 1대(시간당 금화 360)를 채우는 데 드는 전체 층 수입니다.</p>
  <div class="frame"><svg id="effSvg" role="img" aria-label="층당 시간당 금화 막대그래프"></svg></div>
  <div class="tbl"><table>
    <thead><tr><th>음식</th><th>작물 층 1개 금화/시간</th><th>판매함 1대(360) 채우는 층</th><th>전체 층당 금화/시간</th><th>근거·가정</th></tr></thead>
    <tbody>
      <tr class="hl"><td><b>맥주</b></td><td class="mono">264</td><td class="mono">밀 1.4 + 버섯 1 + 통 1 ≈ 4</td><td class="mono">≈ 90</td><td>밀 한 가지만 심어 성장 느림(시간당 1.26회). 버섯 층·발효 시간은 추정(10분, 통 60개)</td></tr>
      <tr class="hl"><td><b>양배추 롤</b></td><td class="mono">104</td><td class="mono">작물 3.5 + 가공 0.5 ≈ 4</td><td class="mono">≈ 90</td><td>양배추·감자 번갈아 심기(2.51회). 묶음이 40동화라 판매함은 1.6대 필요</td></tr>
      <tr><td>비건 피자</td><td class="mono">97</td><td class="mono">작물 3.7 + 가공 1 ≈ 5</td><td class="mono">≈ 72</td><td>밀·토마토·피망·양파·감자 번갈아 심기. 토마토는 밀과 같은 속도로 가정</td></tr>
      <tr><td>쿠키</td><td class="mono">33</td><td class="mono">밀 11 + 코코아 0.4 ≈ 12</td><td class="mono">≈ 30</td><td>판매 1회에 밀 8개. 코코아 층은 시간당 약 4,000개라 남음</td></tr>
      <tr><td class="muted">비교: 스카이리스 포드</td><td class="mono">300 (포드 1개)</td><td class="mono">포드 1.2 (높이 45)</td><td class="mono">≈ 27 (높이 4 환산)</td><td>뼛가루 모드. 24시간 돌지만 뼛가루(시간당 약 350)가 듭니다</td></tr>
    </tbody>
  </table></div>
  <div class="two">
    <div class="note gold"><b>결론</b><span>시간·공간 효율은 <b>맥주와 양배추 롤이 공동 1위</b>(전체 층당 시간당 금화 약 90), 비건 피자가 그다음이고, 쿠키는 원재료가 단순한 대신 층당 효율이 3분의 1입니다. 맥주는 통 자동화와 발효 시간 확인이 남아 있어서, 확실한 쪽은 양배추 롤입니다(요리 냄비·도마는 Central Kitchen·Slice and Dice로 자동화).</span></div>
    <div class="note"><b>하루 단위로 보면</b><span>작물은 기지에 있는 시간에만 자랍니다. 하루 4시간이면 양배추 롤 4층 ≈ 금화 1,440입니다. 스카이리스는 24시간 돌지만 결국 뼛가루(기지에 있을 때 만드는)에 묶이므로, 둘 다 "기지에 있는 시간"이 공통 한계입니다. 스포너 1개·1시간의 뼛가루로 금화 약 1,280(스카이리스 포드 4.3시간분)이라, 기지에 있는 시간당으로는 뼛가루 공장 + 스카이리스가 가장 셉니다. 음식 타워는 그 옆에 쌓아 같은 시간에 함께 돌리는 용도입니다.</span></div>
  </div>
  <p class="muted" style="font-size:12.5px">계산: 무작위 틱은 블록당 시간당 52.7회. 작물(7단계)은 물 젖은 경작지에서 틱당 성장 확률 1/3(다른 작물과 번갈아 심을 때) 또는 1/6(같은 작물만 빽빽할 때) → 시간당 수확 2.51회 / 1.26회. 순수확(다시 심는 1개 제외): 밀·양배추·토마토 1, 감자·당근·양파·피망 1.71. 코코아는 2단계 × 확률 1/5, 수확당 3개.</p>
</section>
'''
rep('<section class="sheet" id="tower">', sheet+'\n<section class="sheet" id="tower">')

# calculator inputs
rep('<select id="prod"><option value="cookie" selected>쿠키</option><option value="beer">맥주</option></select></label>',
    '<select id="prod"><option value="cabbage" selected>양배추 롤</option><option value="beer">맥주</option><option value="pizza">비건 피자</option><option value="cookie">쿠키</option></select></label>')
rep('<label for="wf">밀 층 수 <span class="mono" id="wfOut">6</span><input type="range" id="wf" min="1" max="20" value="6"></label>',
    '<label for="wf">작물 층 수 <span class="mono" id="wfOut">4</span><input type="range" id="wf" min="1" max="20" value="4"></label>')
rep('<label for="h">작물 1칸 시간당 수확 횟수\n        <select id="h"><option value="1.25">1.25 · 느리게</option><option value="1.5" selected>1.5 · 보통</option><option value="2.5">2.5 · 물길 옆 줄 심기</option></select></label>',
    '<label for="h">성장 속도 가정\n        <select id="h"><option value="0.5">계산값의 절반 (보수적)</option><option value="1" selected>바닐라 계산값</option></select></label>')
rep('<input type="number" id="bins" min="1" value="1"></label>','<input type="number" id="bins" min="1" value="2"></label>')
rep('<p class="muted" style="font-size:12px">가정: 밀 층 210칸, 수확 1회 = 밀 1. 코코아 층은 1개로 충분(시간당 3,000개 이상). 수확 횟수는 바닐라 성장 확률로 추정한 값입니다.</p>',
    '<p class="muted" style="font-size:12px">가정: 작물 층 210칸. 층당 금화/시간 = 양배추 롤 104 · 맥주 264(밀 기준) · 비건 피자 97 · 쿠키 33 (A-2 계산). 코코아·가공 층은 따로 셉니다.</p>')
rep('<div class="kpi"><small>밀/시간</small><b id="kWheat">–</b></div>','<div class="kpi"><small>작물 층이 만드는 금화/시간</small><b id="kWheat">–</b></div>')

start=s.index('function calc(){'); end=s.index("['prod','wf','h','mush','kegs','ft','tier','bins']")
calc='''function calc(){
  const prod=$('prod').value, wf=+$('wf').value, h=+$('h').value, t=+$('tier').value, bins=Math.max(1,+$('bins').value||1);
  $('wfOut').textContent=wf;
  const beer=prod==='beer';
  ['mushL','kegL','ftL'].forEach(id=>$(id).hidden=!beer);
  const per={cabbage:104,beer:264,pizza:97,cookie:33}[prod]*h;
  const lotV=prod==='cabbage'?40/64:1;
  const crop=wf*per, cap=bins*3600/t*lotV;
  const opts=[[crop,'작물'],[cap,'판매함']];
  let extra='';
  if(beer){
    const mush=+$('mush').value||0, kegs=Math.max(1,+$('kegs').value||1), ft=Math.max(1,+$('ft').value||10);
    opts.push([mush,'버섯'],[kegs*60/ft,'통']);
    extra=` 탱커드가 필요하면 판매 1회에 판자 5 + 철 조각 2(약 5.5동화, 수입의 9%).`;
  }
  if(prod==='cabbage') extra=' 묶음이 40동화라 판매함 1회가 금화 0.63개입니다.';
  if(prod==='cookie') extra=' 코코아 층 1개면 작물 층 30개분까지 충분합니다.';
  opts.sort((a,b)=>a[0]-b[0]);
  const gold=opts[0][0], neck=opts[0][1];
  $('kWheat').textContent=fmt(crop);$('kLots').textContent=fmt(gold/lotV);$('kCap').textContent=fmt(cap);
  $('kGold').textContent=fmt(gold);$('kDia').textContent=fmt(gold/8);$('kNeck').textContent=neck;
  $('status').className='status'+(neck==='판매함'?' warn':'');
  $('status').textContent=(neck==='판매함'?'판매함이 병목입니다. 판매함을 늘리면 금화가 더 나옵니다.':`${neck}이(가) 병목입니다.`)+extra;
}
'''
s=s[:start]+calc+s[end:]
rep('<div class="kpi"><small>판매 가능 묶음/시간</small>','<div class="kpi"><small>판매 횟수/시간</small>')
rep('<span class="sub">시간당 · 추정치 기반</span></div>\n  <div class="calc">','<span class="sub">시간당 · 플레이어가 근처에 있을 때</span></div>\n  <div class="calc">')

# chart script
chart=r'''/* eff chart */
(function(){
  const s=document.getElementById('effSvg');
  const rows=[['맥주',264,90],['양배추 롤',104,90],['비건 피자',97,72],['쿠키',33,30],['스카이리스 (참고)',null,27]];
  const W=640, lx=130, bw=420, rh=34, H=rows.length*rh+50, max=280;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('width',W);s.setAttribute('height',H);
  const X=v=>lx+v/max*bw;
  [0,70,140,210,280].forEach(v=>{s.append(el('line',{x1:X(v),y1:14,x2:X(v),y2:H-30,stroke:V('grid')}));s.append(el('text',{x:X(v),y:H-14,'text-anchor':'middle','font-size':10,class:'mono',fill:V('muted')},v))});
  rows.forEach(([n,a,b],i)=>{
    const y=20+i*rh;
    s.append(el('text',{x:lx-8,y:y+15,'text-anchor':'end','font-size':12,fill:V('ink')},n));
    if(a!=null){s.append(el('rect',{x:lx,y:y,width:X(a)-lx,height:10,fill:V('c-leaf')}));s.append(el('text',{x:X(a)+5,y:y+9,'font-size':10,class:'mono',fill:V('muted')},a));}
    s.append(el('rect',{x:lx,y:y+12,width:X(b)-lx,height:10,fill:V('gold')}));
    s.append(el('text',{x:X(b)+5,y:y+21,'font-size':10,class:'mono',fill:V('ink')},b));
  });
  s.append(el('rect',{x:W-190,y:H-44,width:10,height:8,fill:V('c-leaf')}));s.append(el('text',{x:W-175,y:H-37,'font-size':10,fill:V('muted')},'작물 층 1개'));
  s.append(el('rect',{x:W-110,y:H-44,width:10,height:8,fill:V('gold')}));s.append(el('text',{x:W-95,y:H-37,'font-size':10,fill:V('muted')},'전체 층당'));
})();
'''
rep('/* tower */', chart+'/* tower */')
rep('설계도 세트 A–E (6장)','설계도 세트 A–E (7장)')
rep('<li><b>쿠키 · 조합</b>','<li><b>양배추 롤 · 손질</b><span>디플로이어 도마(Slice and Dice)로 양배추 → 잎 2장, 감자 → 조각 2개.</span><span class="io">양배추 1 → 잎 2</span></li>\n    <li><b>양배추 롤 · 요리</b><span>요리 냄비(Central Kitchen)에 잎 1 + 감자 조각 1. 한 번에 약 10초.</span><span class="io">→ 양배추 롤 1</span></li>\n    <li class="money"><b>양배추 롤 · 판매</b><span>4개가 판매 1회(40동화).</span><span class="io">롤 4 → 동화 40</span></li>\n    <li><b>쿠키 · 조합</b>')
rep('<span class="sub">쿠키는 확실, 맥주는 검증 후</span>','<span class="sub">양배추 롤·쿠키는 확실, 맥주는 검증 후</span>')
open(p,'w',encoding='utf8').write(s); print('ok')
