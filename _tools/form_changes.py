# Adds form-change info to pokedex/data/pokedex.json (run after build_data.py; idempotent).
# Each form gets "fc": {"k": kind, "h": [en, ko]}; species with forms get "fcb" for the base form.
# Sources: Mega Showdown jar (item classes, mega/battle_form data, config/mega_showdown/config.json),
# Cobblemon cosmetic_items, Cobbreeding inheritedFeatures, ATM x MSD datapack.
import json, os, re, zipfile, glob

INST = r'C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)'
DEX = os.path.join(INST, 'guides', 'pokedex', 'data', 'pokedex.json')
MSD = glob.glob(os.path.join(INST, 'mods', 'mega_showdown-*.jar'))[0]
COB = glob.glob(os.path.join(INST, 'mods', 'Cobblemon-neoforge-*.jar'))[0]
ATM = glob.glob(os.path.join(INST, 'datapacks', 'ATM x MSD*.zip'))[0]


def zjson(z, n):
    return json.loads(z.read(n).decode('utf-8-sig'))


mz, cz, az = zipfile.ZipFile(MSD), zipfile.ZipFile(COB), zipfile.ZipFile(ATM)
EN = {**zjson(cz, 'assets/cobblemon/lang/en_us.json'), **zjson(mz, 'assets/mega_showdown/lang/en_us.json')}
KO = {**zjson(cz, 'assets/cobblemon/lang/ko_kr.json'), **zjson(mz, 'assets/mega_showdown/lang/ko_kr.json')}
CFG = json.load(open(os.path.join(INST, 'config', 'mega_showdown', 'config.json')))
INHERIT = set(json.load(open(os.path.join(INST, 'config', 'cobbreeding', 'main.json')))['inheritedFeatures'])


def item(iid):
    ns, _, p = iid.partition(':') if ':' in iid else ('mega_showdown', '', iid)
    for k in ('item.%s.%s' % (ns, p), 'block.%s.%s' % (ns, p)):
        if k in EN:
            return [EN[k], KO.get(k, EN[k])]
    return [p.replace('_', ' ').title()] * 2


def move(mid):
    k = 'cobblemon.move.' + mid
    return [EN.get(k, mid), KO.get(k, EN.get(k, mid))]


# mega stones: (species, mega_evolution value) -> item id
STONES = {}
for z in (mz, az):
    for n in z.namelist():
        if re.match(r'data/mega_showdown/mega_showdown/mega/[^/]+\.json$', n):
            j = zjson(z, n)
            v = j['aspect_conditions']['apply']['aspects'][0].split('=')[1]
            for sp in j['pokemons']:
                STONES[(sp.lower(), v)] = n.rsplit('/', 1)[1][:-5]

# cosmetic items: aspect -> item id
COSMETIC = {}
for n in cz.namelist():
    if n.startswith('data/cobblemon/cosmetic_items/') and n.endswith('.json'):
        for c in zjson(cz, n).get('cosmeticItems', []):
            for a in c.get('aspects', []):
                COSMETIC[a] = c.get('consumedItem')

TYPES = ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting', 'poison', 'ground', 'flying', 'psychic',
         'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy']
PLATES = dict(zip(TYPES, ['', 'flame', 'splash', 'zap', 'meadow', 'icicle', 'fist', 'toxic', 'earth', 'sky', 'mind',
                          'insect', 'stone', 'spooky', 'draco', 'dread', 'iron', 'pixie']))
DRIVES = {'douse': 'douse_drive', 'shock': 'shock_drive', 'burn': 'burn_drive', 'chill': 'chill_drive'}
NECTAR = {'pa-u': 'pink_nectar', 'sensu': 'purple_nectar', 'pom-pom': 'yellow_nectar', '': 'red_nectar'}


def josa(t):
    # pick 을/를 from the last spoken character before '을(를)'
    def has_batchim(ch):
        if '가' <= ch <= '힣':
            return (ord(ch) - 0xAC00) % 28 != 0
        return ch.upper() in 'LMNR0136780'
    return re.sub(r'(\S)을\(를\)', lambda m: m.group(1) + ('을' if has_batchim(m.group(1)) else '를'), t)


def T(en, ko):
    return [en, josa(ko)]


def held(it, extra=('', '')):
    n = item(it)
    return 'held', T('Have it hold %s — it changes right away. Take the item back to revert.%s' % (n[0], extra[0]),
                     '%s을(를) 지니게 하면 바로 변합니다. 도구를 빼면 원래대로 돌아옵니다.%s' % (n[1], extra[1]))


def battle(en, ko, revert=True):
    return 'battle', T(en + (' Reverts after battle.' if revert else ''), ko + (' 배틀이 끝나면 원래대로 돌아옵니다.' if revert else ''))


def fixed(en, ko, feat=None):
    inh = feat in INHERIT
    return 'fixed', T(en + (' Passed on to eggs when breeding.' if inh else ''),
                      ko + (' 교배하면 알에게 유전됩니다.' if inh else ''))


BRACELET = item('mega_bracelet')
OUTSIDE = CFG.get('outSideMega')


def in_raid(p, slug):
    return any(r.get('fm') == slug for r in p.get('raid') or [])


def mega(p, slug):
    sp = p['id']
    v = slug.replace('-', '_')
    out = (' This pack also allows Mega Evolution outside battle.', ' 이 팩에서는 배틀 밖에서도 메가진화할 수 있습니다.') if OUTSIDE else ('', '')
    if sp == 'rayquaza':
        mv = move('dragonascent')
        return 'mega', T('No Mega Stone needed: Rayquaza must know %s. Wear a %s (Key Stone) and Mega Evolve.%s' % (mv[0], BRACELET[0], out[0]),
                         '메가스톤은 필요 없고, %s을(를) 배운 레쿠쟈라면 트레이너가 %s을(를) 착용한 상태로 메가진화할 수 있습니다.%s' % (mv[1], BRACELET[1], out[1]))
    st = STONES.get((sp, v))
    if not st:
        r = in_raid(p, slug)
        return 'none', T('No Mega Stone for this form exists in the pack, so players can\'t Mega Evolve it%s.' % (' (raid boss only)' if r else ''),
                         '이 팩에는 이 폼의 메가스톤이 없어 플레이어는 메가진화시킬 수 없습니다%s.' % (' (레이드 보스 전용)' if r else ''))
    n = item(st)
    return 'mega', T('Hold %s and wear a %s (Key Stone), then Mega Evolve.%s' % (n[0], BRACELET[0], out[0]),
                     '%s을(를) 지니게 하고 트레이너가 %s을(를) 착용한 뒤 메가진화합니다.%s' % (n[1], BRACELET[1], out[1]))


def gmax(p, slug):
    if not CFG.get('dynamax', True):
        r = in_raid(p, slug)
        return 'none', T('Dynamax / Gigantamax is turned off in this pack (Mega Showdown config), so players can\'t use it.%s' % (' This form only shows up as a raid boss.' if r else ''),
                         '이 팩은 다이맥스/거다이맥스가 꺼져 있어(Mega Showdown 설정) 플레이어는 쓸 수 없습니다.%s' % (' 레이드 보스로만 등장합니다.' if r else ''))
    s = item('max_soup')
    return 'gmax', T('Feed it %s to get the G-Max Factor, then Dynamax in battle with a Dynamax Band.' % s[0],
                     '%s로 거다이맥스 인자를 얻은 뒤 다이맥스밴드로 배틀 중 다이맥스합니다.' % s[1])


REGIONAL = {'alola', 'galar', 'hisui', 'paldea', 'paldea-combat', 'paldea-blaze', 'paldea-aqua'}


def rule(p, f):
    sp, s = p['id'], f['slug']
    if 'gmax' in s:
        return gmax(p, s)
    if s.startswith('mega'):
        return mega(p, s)
    if s == 'primal':
        return held('red_orb' if sp == 'groudon' else 'blue_orb',
                    (' Only one Primal at a time.', ' 원시회귀 포켓몬은 한 마리만 지닐 수 있습니다.'))
    if s in REGIONAL:
        return 'regional', T('Regional form — fixed for life. Catch one (see Where to find) or breed one; the form passes to the egg.',
                             '리전폼 — 평생 바뀌지 않습니다. 야생/레이드에서 잡거나(출현 장소 탭) 교배하면 알에게 유전됩니다.')
    if 'female' in (f.get('asp') or []):
        return 'gender', T('Female form — set by gender.', '암컷의 모습 — 성별로 정해집니다.')
    if sp == 'arceus':
        return held(PLATES[s] + '_plate')
    if sp == 'silvally':
        return held(s + '_memory')
    if sp == 'genesect':
        return held(DRIVES[s])
    if sp in ('dialga', 'palkia', 'giratina') and s == 'origin':
        return held({'dialga': 'adamant_crystal', 'palkia': 'lustrous_globe', 'giratina': 'griseous_core'}[sp])
    if sp in ('zacian', 'zamazenta'):
        return held('rusted_sword' if sp == 'zacian' else 'rusted_shield')
    if sp == 'eternatus':
        return held('star_core')
    if sp == 'ogerpon':
        if s.endswith('-tera'):
            o = item('tera_orb')
            return battle('Terastallize it in battle with a %s (Embody Aspect).' % o[0],
                          '%s로 배틀 중 테라스탈하면 변합니다 (면영 특성).' % o[1])
        return held(s + '_mask')
    if sp == 'rotom':
        c = item('rotom_catalogue')
        return 'use', T('Use the %s on Rotom and pick an appliance (or use an appliance block on it). Use it again to return to normal.' % c[0],
                        '%s을(를) 로토무에게 사용해 가전제품을 고릅니다(가전 블록을 직접 사용해도 됨). 다시 사용하면 원래대로 돌아옵니다.' % c[1])
    if sp == 'deoxys':
        m = item('deoxys_meteorite')
        return 'use', T('Use a %s on Deoxys to cycle Normal → Attack → Speed → Defense.' % m[0],
                        '%s을(를) 테오키스에게 사용할 때마다 노말 → 어택 → 스피드 → 디펜스 폼으로 바뀝니다.' % m[1])
    if sp == 'shaymin':
        g = item('gracidea_flower')
        return 'use', T('Use a %s on Shaymin. It turns back to Land Forme if it gets frozen in battle.' % g[0],
                        '%s을(를) 쉐이미에게 사용합니다. 배틀 중 얼음 상태가 되면 랜드폼으로 돌아갑니다.' % g[1])
    if s == 'therian':
        g = item('reveal_glass')
        return 'use', T('Use the %s on it to switch between Incarnate and Therian Forme.' % g[0],
                        '%s을(를) 사용할 때마다 화신폼과 영물폼이 바뀝니다.' % g[1])
    if sp == 'hoopa':
        g = item('prison_bottle')
        return 'use', T('Use the %s on Hoopa to switch between Confined and Unbound.' % g[0],
                        '%s을(를) 후파에게 사용할 때마다 굴레에 빠진 모습과 해방된 모습이 바뀝니다.' % g[1])
    if sp == 'oricorio':
        g = item(NECTAR[s])
        return 'use', T('Use %s on Oricorio. The style passes to eggs when breeding.' % g[0],
                        '%s을(를) 춤추새에게 사용합니다. 스타일은 교배 시 알에게 유전됩니다.' % g[1])
    if sp == 'kyurem':
        g, o = item('dna_splicer'), ('Reshiram', '레시라무') if s == 'white' else ('Zekrom', '제크로무')
        return 'fusion', T('Use the %s on %s to absorb it, then on Kyurem to fuse. Use it on the fused Kyurem to split them again.' % (g[0], o[0]),
                           '%s을(를) %s에게 사용해 흡수한 뒤 큐레무에게 사용하면 합체합니다. 합체한 큐레무에게 다시 사용하면 분리됩니다.' % (g[1], o[1]))
    if sp == 'calyrex':
        g, o = item('reins_of_unity'), ('Glastrier', '블리자포스') if s == 'ice' else ('Spectrier', '레이스포스')
        return 'fusion', T('Use the %s on %s, then on Calyrex to fuse. Use it again to split them.' % (g[0], o[0]),
                           '%s을(를) %s에게 사용한 뒤 버드렉스에게 사용하면 합체합니다. 다시 사용하면 분리됩니다.' % (g[1], o[1]))
    if sp == 'necrozma':
        if s == 'ultra':
            z = item('ultranecrozium_z')
            extra = ('' if CFG.get('outSideUltraBurst') else ' (Ultra Burst outside battle is off in this pack.)',
                     '' if CFG.get('outSideUltraBurst') else ' (이 팩은 배틀 밖 울트라버스트가 꺼져 있습니다.)')
            return battle('A fused Necrozma (Dusk Mane or Dawn Wings) holding %s can Ultra Burst in battle.%s' % (z[0], extra[0]),
                          '합체한 네크로즈마(황혼의 갈기/새벽의 날개)가 %s을(를) 지니면 배틀 중 울트라버스트할 수 있습니다.%s' % (z[1], extra[1]))
        g, o = (item('n_solarizer'), ('Solgaleo', '솔가레오')) if s == 'dusk-mane' else (item('n_lunarizer'), ('Lunala', '루나아라'))
        return 'fusion', T('Use the %s on %s, then on Necrozma to fuse. Use it again to split them.' % (g[0], o[0]),
                           '%s을(를) %s에게 사용한 뒤 네크로즈마에게 사용하면 합체합니다. 다시 사용하면 분리됩니다.' % (g[1], o[1]))
    if sp == 'keldeo':
        mv = move('secretsword')
        return 'move', T('Put %s in its moveset — it changes when it knows the move.' % mv[0],
                         '%s을(를) 기술 슬롯에 넣으면 변합니다.' % mv[1])
    if sp == 'greninja':
        if s == 'bond':
            c = item('ash_cap')
            return 'use', T('Use the %s on a Greninja with high friendship (%d+) to give it Battle Bond.' % (c[0], CFG.get('minBondingRequired', 200)),
                            '친밀도가 높은(%d 이상) 개굴닌자에게 %s을(를) 사용하면 유대변화 특성을 얻습니다.' % (CFG.get('minBondingRequired', 200), c[1]))
        return battle('A Battle Bond Greninja turns into Ash-Greninja after it knocks out a foe.', '유대변화 개굴닌자가 상대를 쓰러뜨리면 지우개굴닌자가 됩니다.')
    if sp == 'zygarde':
        cube = item('zygarde_cube')
        if s == 'complete':
            return battle('A Power Construct Zygarde becomes Complete Forme in battle when its HP drops below half.',
                          '스웜체인지 특성 지가르데가 배틀 중 HP가 절반 이하가 되면 퍼펙트폼이 됩니다.')
        if s == 'core':
            return 'none', T('Zygarde Core — not a battle form; Cores are collected in the %s.' % cube[0],
                             '지가르데 코어 — 배틀용 폼이 아니며, %s에 모으는 재료입니다.' % cube[1])
        pc = s.endswith('-c')
        return 'use', T('Store Zygarde Cells and Cores in the %s and use it on Zygarde to switch between 10%% and 50%%%s.' % (cube[0], ' (Power Construct version)' if pc else ''),
                        '%s에 지가르데 셀과 코어를 모아 지가르데에게 사용하면 10%%와 50%% 폼을 바꿀 수 있습니다%s.' % (cube[1], ' (스웜체인지 버전)' if pc else ''))
    if sp == 'pikachu':
        if s == 'cosplay':
            return fixed('Cosplay Pikachu — catch one in the wild.', '옷갈아입기 피카츄 — 야생에서 잡을 수 있습니다.')
        if s in ('rock-star', 'pop-star', 'phd', 'libre', 'belle'):
            c = item('pika_case')
            return 'use', T('Use the %s on a Cosplay Pikachu to cycle its outfits.' % c[0],
                            '옷갈아입기 피카츄에게 %s을(를) 사용하면 의상이 바뀝니다.' % c[1])
    a = (f.get('asp') or [''])[0]
    if a.startswith('cosmetic_item-'):
        it = COSMETIC.get(a)
        if not it:
            return 'none', T('No item in this pack applies this look, so it can\'t be obtained normally.',
                             '이 팩에는 이 모습을 입히는 아이템이 없어 일반적으로는 얻을 수 없습니다.')
        n = item(it)
        return 'cosmetic', T('Give it %s as a cosmetic item (it is used up).' % n[0], '%s을(를) 장식 아이템으로 주면 변합니다 (아이템 소모).' % n[1])
    # in-battle forms (Mega Showdown battle_form)
    B = {
        'aegislash': ('Stance Change: turns to Blade Forme when it uses an attacking move, back to Shield with King\'s Shield.', '배틀스위치: 공격 기술을 쓰면 블레이드폼, 킹실드를 쓰면 실드폼이 됩니다.'),
        'castform': ('Forecast: changes with the weather in battle (sun, rain, snow/hail).', '기분파: 배틀 중 날씨(쾌청/비/눈·싸라기눈)에 따라 바뀝니다.'),
        'cherrim': ('Flower Gift: blooms in harsh sunlight during battle.', '플라워기프트: 배틀 중 쾌청 날씨에서 변합니다.'),
        'cramorant': ('Gulp Missile: after Surf or Dive it catches prey — Gulping above half HP, Gorging at half or below.', '그대로꿀꺽미사일: 파도타기/다이빙 후 HP가 절반 초과면 그대로꿀꺽, 이하면 통째로꿀꺽 모습이 됩니다.'),
        'darmanitan': ('Zen Mode ability: switches when HP falls to half or below.', '달마모드 특성: HP가 절반 이하가 되면 변합니다.'),
        'eiscue': ('Ice Face breaks when hit by a physical move (restored by hail/snow).', '아이스페이스: 물리 기술에 맞으면 깨집니다 (싸라기눈/설경에서 회복).'),
        'meloetta': ('Using Relic Song in battle switches Aria ↔ Pirouette.', '배틀 중 옛노래를 쓰면 보이스폼 ↔ 스텝폼이 바뀝니다.'),
        'mimikyu': ('Disguise: busted after the first hit.', '탈: 처음 공격을 맞으면 벗겨집니다.'),
        'minior': ('Shields Down: Meteor Form above half HP, Core below.', '리밋실드: HP 절반 초과면 유성의 모습, 이하면 코어 모습입니다.'),
        'morpeko': ('Hunger Switch: alternates every turn in battle.', '꼬르륵스위치: 배틀 중 매 턴 번갈아 바뀝니다.'),
        'palafin': ('Zero to Hero: becomes Hero Form after switching out once in battle.', '마이티체인지: 배틀 중 한 번 교체되면 마이티폼이 됩니다.'),
        'wishiwashi': ('Schooling: School Form at Lv. 20+ while HP is above a quarter.', '어군: Lv.20 이상이고 HP가 1/4 초과일 때 군집의 모습이 됩니다.'),
        'xerneas': ('Becomes Active Mode in battle.', '배틀에 나오면 액티브모드가 됩니다.'),
    }
    if sp in B:
        if sp == 'darmanitan' and s == 'galar':
            return 'regional', T('Galarian form — fixed for life; passes to eggs. Its Zen Mode form appears in battle.',
                                 '가라르폼 — 평생 바뀌지 않으며 알에게 유전됩니다. 배틀 중 달마모드로 변합니다.')
        return battle(*B[sp])
    if sp == 'terapagos':
        if s == 'terastal':
            return battle('Tera Shift: turns Terastal Form as soon as it enters battle.', '테라체인지: 배틀에 나오자마자 테라스탈폼이 됩니다.')
        o = item('tera_orb')
        return battle('Terastallize it with a %s in battle.' % o[0], '배틀 중 %s로 테라스탈하면 변합니다.' % o[1])
    # decided at evolution
    E = {
        'lycanroc': ('Decided when Rockruff evolves (time of day; Dusk needs an Own Tempo Rockruff) — see Evolution. The form passes to eggs.', '이와이누가 진화할 때(시간대) 정해집니다. 황혼의 모습은 마이페이스 이와이누 필요 — 진화 탭 참고. 교배 시 유전됩니다.'),
        'rockruff': ('Own Tempo Rockruff that evolves into Dusk Form Lycanroc. Fixed; passes to eggs.', '황혼의 모습 루가루암으로 진화하는 마이페이스 이와이누. 고정이며 교배 시 유전됩니다.'),
        'toxtricity': ('Decided by Toxel\'s nature when it evolves — see Evolution.', '일레즌이 진화할 때 성격으로 정해집니다 — 진화 탭 참고.'),
        'urshifu': ('Decided when Kubfu evolves (Scroll of Waters vs. Scroll of Darkness) — see Evolution.', '치고마가 진화할 때(물의 족자 / 악의 족자) 정해집니다 — 진화 탭 참고.'),
        'alcremie': ('Decided when Milcery evolves (sweet held + spin) — see Evolution.', '마빌크가 진화할 때(사탕공예 + 회전) 정해집니다 — 진화 탭 참고.'),
        'maushold': ('Random when Tandemaus evolves.', '두리쥐가 진화할 때 무작위로 정해집니다.'),
        'dudunsparce': ('Random when Dunsparce evolves.', '노고치가 진화할 때 무작위로 정해집니다.'),
        'wormadam': ('Keeps the cloak Burmy had when it evolved.', '도롱충이가 진화할 때의 도롱이를 그대로 유지합니다.'),
        'polteageist': ('Evolve an Antique Sinistea with a Cracked Pot — see Evolution.', '진품 데인차를 깨진포트로 진화시킵니다 — 진화 탭 참고.'),
        'sinistcha': ('Evolve an Artisan Poltchageist with a Masterpiece Teacup — see Evolution.', '걸작 차데스를 걸작찻잔으로 진화시킵니다 — 진화 탭 참고.'),
    }
    if sp in E:
        k, h = ('evo', T(*E[sp]))
        if sp in ('wormadam',):
            return fixed(*E[sp], feat='bagworm_cloak')
        return k, h
    if sp == 'burmy':
        return 'battle', T('Its cloak changes to match the terrain it last battled in (Mega Showdown). The cloak passes to eggs when breeding.',
                           '마지막으로 배틀한 장소의 지형에 맞춰 도롱이가 바뀝니다 (Mega Showdown). 교배하면 알에게 유전됩니다.')
    F = {
        'unown': ('Letter is random when it spawns.', '출현 시 글자가 무작위로 정해집니다.', None),
        'basculin': ('Stripe colour is set when it spawns.', '출현 시 줄무늬 색이 정해집니다.', 'fish_stripes'),
        'tatsugiri': ('Shape is set when it spawns.', '출현 시 모양이 정해집니다.', 'tatsugiri_texture'),
    }
    feat = (p.get('feat') or [{}])[0].get('k')
    if sp in F:
        return fixed(F[sp][0], F[sp][1], F[sp][2])
    return fixed('Fixed variant — set when it spawns or hatches and can\'t be changed afterwards.',
                 '고정 변형 — 출현/부화할 때 정해지며 이후 바꿀 수 없습니다.', feat)


d = json.load(open(DEX, encoding='utf8'))
cnt = {}
for p in d['pokemon']:
    for f in p.get('forms', []) or []:
        k, h = rule(p, f)
        f['fc'] = {'k': k, 'h': h}
        cnt[k] = cnt.get(k, 0) + 1
d['meta']['fcKinds'] = {
    'mega': ['Mega Evolution', '메가진화'], 'gmax': ['Gigantamax', '거다이맥스'], 'battle': ['In battle', '배틀 중 변화'],
    'held': ['Held item', '지닌 도구'], 'use': ['Use an item', '도구 사용'], 'fusion': ['Fusion', '합체'], 'move': ['Move', '기술'],
    'evo': ['At evolution', '진화 시 결정'], 'fixed': ['Fixed', '고정'], 'regional': ['Regional form', '리전폼'],
    'gender': ['Gender', '성별'], 'cosmetic': ['Cosmetic item', '장식 아이템'], 'none': ['Not obtainable', '획득 불가'],
}
json.dump(d, open(DEX, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('form changes:', cnt)
