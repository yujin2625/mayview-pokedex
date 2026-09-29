# Builds pokedex.json for the Mayview modpack from layered game data.
import json, os, re, glob, collections, sys

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = os.path.join(S, 'layers')
INST = r'C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)'
OUT = os.path.join(INST, 'guides', 'pokedex', 'data')
os.makedirs(OUT, exist_ok=True)

# data layers, low -> high priority
DATA_LAYERS = [os.path.join(L, x) for x in ['00_cobblemon', '01_integrations', '02_msd', '03_mal', '04_paleo', '05_cobblenav', '20_atm_dp']] + [os.path.join(INST, 'kubejs')]
MODIDS = set(open(os.path.join(S, 'modids.txt')).read().split())
MODIDS |= {'minecraft', 'c', 'neoforge', 'forge'}


def jload(p):
    try:
        with open(p, encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        if '/lang/' in p.replace(os.sep, '/'):
            t = open(p, encoding='utf-8-sig', errors='ignore').read()
            return {m.group(1): json.loads('"%s"' % m.group(2)) for m in re.finditer(r'"((?:[^"\\]|\\.)+)"\s*:\s*"((?:[^"\\]|\\.)*)"', t) if _okstr(m.group(2))}
        print('WARN bad json', p, e)
        return None


def _okstr(v):
    try:
        json.loads('"%s"' % v); return True
    except Exception:
        return False


def layered_files(sub):
    """{relpath: fullpath} for data/<ns>/<sub>/**.json, higher layers override."""
    res = {}
    for layer in DATA_LAYERS:
        for f in glob.glob(os.path.join(layer, 'data', '*', sub, '**', '*.json'), recursive=True):
            rel = os.path.relpath(f, os.path.join(layer, 'data')).replace('\\', '/')
            res[rel] = f
    return res

# ---------------------------------------------------------------- lang
def load_lang(code):
    d = {}
    srcs = []
    for layer in ['30_modtags', '00_cobblemon', '02_msd', '13_atm_rp', '12_mayviewres']:
        srcs += glob.glob(os.path.join(L, layer, '**', 'assets', '*', 'lang', code + '.json'), recursive=True)
        srcs += glob.glob(os.path.join(L, layer, 'assets', '*', 'lang', code + '.json'))
    if code == 'ko_kr':
        srcs += glob.glob(os.path.join(L, '32_vanilla_ko', 'assets', '*', 'lang', 'ko_kr.json'))
        srcs += glob.glob(os.path.join(L, '31_mvkorean', 'assets', '*', 'lang', 'ko_kr.json'))
    seen = set()
    for s in srcs:
        if s in seen:
            continue
        seen.add(s)
        j = jload(s)
        if isinstance(j, dict):
            d.update(j)
    return d

EN = load_lang('en_us')
KO = load_lang('ko_kr')
print('lang', len(EN), len(KO))


def tr(key, fallback=None):
    en = EN.get(key)
    ko = KO.get(key) or en
    if en is None and fallback is not None:
        en = fallback
        ko = ko or fallback
    return [en, ko] if en is not None else None

# ---------------------------------------------------------------- tags
def load_tags(kind):
    tags = collections.defaultdict(list)  # id -> entries
    files = []
    for f in glob.glob(os.path.join(L, '30_modtags', '*', 'data', '*', 'tags', 'worldgen', kind, '**', '*.json'), recursive=True):
        files.append(f)
    for layer in DATA_LAYERS:
        files += glob.glob(os.path.join(layer, 'data', '*', 'tags', 'worldgen', kind, '**', '*.json'), recursive=True)
    for f in files:
        m = re.search(r'[\\/]data[\\/]([^\\/]+)[\\/]tags[\\/]worldgen[\\/]' + kind + r'[\\/](.+)\.json$', f)
        tid = m.group(1) + ':' + m.group(2).replace('\\', '/')
        j = jload(f)
        if not j:
            continue
        vals = j.get('values', [])
        if j.get('replace'):
            tags[tid] = list(vals)
        else:
            tags[tid] += vals
    return tags

BIOME_TAGS = load_tags('biome')
BIOMES = set()
for f in glob.glob(os.path.join(L, '30_modtags', '*', 'data', '*', 'worldgen', 'biome', '**', '*.json'), recursive=True):
    pass
# biome registry was not extracted; rebuild from jars quickly
import zipfile
for s in glob.glob(os.path.join(INST, 'mods', '*.jar')) + [r'C:/Users/Dumaru/curseforge/minecraft/Install/versions/1.21.1/1.21.1.jar']:
    try:
        z = zipfile.ZipFile(s)
    except Exception:
        continue
    for n in z.namelist():
        m = re.match(r'^data/([^/]+)/worldgen/biome/(.+)\.json$', n)
        if m and m.group(1) not in ('ae2', 'cobblemonraiddens', 'terrablender'):
            BIOMES.add(m.group(1) + ':' + m.group(2))
print('biomes', len(BIOMES))


def resolve_tag(tid, stack=()):
    out = set()
    if tid in stack:
        return out
    for v in BIOME_TAGS.get(tid, []):
        if isinstance(v, dict):
            v = v.get('id')
        if not isinstance(v, str):
            continue
        if v.startswith('#'):
            out |= resolve_tag(v[1:], stack + (tid,))
        elif v in BIOMES:
            out.add(v)
    return out

TAG_CACHE = {}


def biome_ref(ref):
    """Returns set of real biomes for a ref ('#tag' or id)."""
    if ref in TAG_CACHE:
        return TAG_CACHE[ref]
    r = resolve_tag(ref[1:]) if ref.startswith('#') else ({ref} if ref in BIOMES else set())
    TAG_CACHE[ref] = r
    return r

# ---------------------------------------------------------------- species
species_files = layered_files('species')
species = {}
for rel, f in species_files.items():
    j = jload(f)
    if not j or 'name' not in j:
        continue
    key = os.path.splitext(os.path.basename(f))[0].lower()
    j['_gen'] = rel.split('/')[2] if rel.count('/') >= 3 else ''
    species[key] = j


def merge_forms(base, add):
    byname = {x.get('name', '').lower(): x for x in base}
    for fo in add:
        k = fo.get('name', '').lower()
        if k in byname:
            byname[k].update(fo)
        else:
            base.append(fo)
            byname[k] = fo


addition_files = []
for layer in DATA_LAYERS:
    addition_files += sorted(glob.glob(os.path.join(layer, 'data', '*', 'species_additions', '**', '*.json'), recursive=True))
for f in addition_files:
    j = jload(f)
    if not j or 'target' not in j:
        continue
    key = j['target'].split(':')[-1].lower()
    sp = species.get(key)
    if not sp:
        continue
    for k, v in j.items():
        if k == 'target':
            continue
        if k == 'forms' and isinstance(v, list):
            merge_forms(sp.setdefault('forms', []), v)
        elif k == 'evolutions' and isinstance(v, list):
            ids = {e.get('id'): e for e in sp.get('evolutions', [])}
            for e in v:
                if e.get('id') in ids:
                    ids[e['id']].update(e)
                else:
                    sp.setdefault('evolutions', []).append(e)
        else:
            sp[k] = v

impl = {k: v for k, v in species.items() if v.get('implemented')}
print('species total', len(species), 'implemented', len(impl))
SLUG = {}  # showdown-ish slug of name -> key
for k, v in species.items():
    SLUG[re.sub(r'[^a-z0-9]', '', v['name'].lower())] = k
    SLUG[k] = k

# ---------------------------------------------------------------- properties parsing
def parse_props(s):
    """'raichu region_bias=alola' -> ('raichu', ['region_bias=alola'])"""
    parts = s.strip().split()
    if not parts:
        return None, []
    head = parts[0].split(':')[-1].lower()
    sp = SLUG.get(re.sub(r'[^a-z0-9]', '', head), head)
    return sp, parts[1:]

# ---------------------------------------------------------------- names helpers
def item_name(iid):
    if not iid:
        return None
    if isinstance(iid, dict):
        iid = iid.get('item') or iid.get('tag') or json.dumps(iid)
    tag = iid.startswith('#')
    ns, _, path = iid.lstrip('#').partition(':')
    if not path:
        ns, path = 'minecraft', ns
    for k in ('item.%s.%s' % (ns, path), 'block.%s.%s' % (ns, path)):
        t = tr(k)
        if t:
            return t
    nice = path.replace('_', ' ').replace('/', ' ').title()
    return [('#' if tag else '') + nice, ('#' if tag else '') + nice]


def move_name(m):
    return tr('cobblemon.move.' + m.lower(), m.title()) or [m, m]


def ability_name(a):
    return tr('cobblemon.ability.' + a.lower(), a.title()) or [a, a]


def type_name(t):
    return tr('cobblemon.type.' + t.lower(), t.title()) or [t.title(), t.title()]


def species_name(key):
    return tr('cobblemon.species.%s.name' % key, species.get(key, {}).get('name', key)) or [key, key]


def biome_name(b):
    ns, _, p = b.partition(':')
    return tr('biome.%s.%s' % (ns, p.replace('/', '.')), p.replace('_', ' ').title())

BIOME_OUT = {}
for b in sorted(BIOMES):
    BIOME_OUT[b] = biome_name(b)

# ---------------------------------------------------------------- abilities list
def abilities(lst):
    out = []
    for a in lst or []:
        hidden = a.startswith('h:')
        a2 = a[2:] if hidden else a
        out.append({'id': a2, 'n': ability_name(a2), 'h': 1 if hidden else 0})
    return out

STAT_KEYS = ['hp', 'attack', 'defence', 'special_attack', 'special_defence', 'speed']


def stats(d):
    return [d.get(k, 0) for k in STAT_KEYS] if d else None

# ---------------------------------------------------------------- evolutions
def conv_req(q):
    v = q.get('variant')
    o = {'t': v}
    if v == 'level':
        o['v'] = q.get('minLevel')
    elif v == 'friendship':
        o['v'] = q.get('amount')
    elif v == 'time_range':
        o['v'] = q.get('range')
    elif v == 'held_item':
        o['v'] = item_name(q.get('itemCondition'))
    elif v == 'biome':
        if q.get('biomeCondition'):
            o['v'] = q['biomeCondition']
        if q.get('biomeAnticondition'):
            o['not'] = q['biomeAnticondition']
    elif v == 'properties':
        o['v'] = q.get('target')
    elif v == 'has_move':
        o['v'] = move_name(q.get('move', ''))
    elif v == 'has_move_type':
        o['v'] = type_name(q.get('type', ''))
    elif v == 'structure':
        if q.get('structureCondition'):
            o['v'] = q['structureCondition']
        if q.get('structureAnticondition'):
            o['not'] = q['structureAnticondition']
    elif v == 'property_range':
        o['v'] = q.get('range'); o['f'] = q.get('feature')
    elif v == 'party_member':
        sp, _ = parse_props(q.get('target', ''))
        o['v'] = sp; o['in'] = q.get('contains', True)
    elif v == 'defeat':
        sp, props = parse_props(q.get('target', ''))
        o['v'] = sp; o['n'] = q.get('amount'); o['p'] = ' '.join(props)
    elif v in ('blocks_traveled', 'battle_critical_hits', 'recoil', 'damage_taken'):
        o['v'] = q.get('amount')
    elif v == 'use_move':
        o['v'] = move_name(q.get('move', '')); o['n'] = q.get('amount')
    elif v == 'stat_compare':
        o['v'] = [q.get('highStat'), q.get('lowStat')]
    elif v == 'stat_equal':
        o['v'] = [q.get('statOne'), q.get('statTwo')]
    elif v == 'weather':
        o['v'] = 'thunder' if q.get('isThundering') else ('rain' if q.get('isRaining') else ('clear' if q.get('isRaining') is False else '?'))
    elif v == 'moon_phase':
        o['v'] = q.get('moonPhase')
    elif v == 'advancement':
        o['v'] = q.get('requiredAdvancement')
    else:
        o['raw'] = q
    return o


def conv_evos(lst):
    out = []
    for e in lst or []:
        sp, props = parse_props(e.get('result', ''))
        if not sp:
            continue
        o = {'to': sp, 'm': e.get('variant')}
        if props:
            o['p'] = props
        ctx = e.get('requiredContext')
        if ctx:
            if e.get('variant') == 'trade':
                o['with'] = parse_props(ctx)[0]
            else:
                o['item'] = item_name(ctx)
                o['itemId'] = ctx
        need = {'lunar_event': 'enhancedcelestials', 'sereneseasons': 'sereneseasons'}
        if any(need.get(q.get('variant')) and need[q.get('variant')] not in MODIDS for q in e.get('requirements', [])):
            continue
        reqs = [conv_req(q) for q in e.get('requirements', [])]
        if reqs:
            o['r'] = reqs
        out.append(o)
    return out

# ---------------------------------------------------------------- spawns
preset_files = layered_files('spawn_detail_presets')
PRESETS = {}
for rel, f in preset_files.items():
    j = jload(f)
    if j:
        PRESETS[os.path.splitext(os.path.basename(f))[0]] = j

spawn_files = layered_files('spawn_pool_world')
SP = collections.defaultdict(list)
drop_stats = collections.Counter()


def mods_ok(d):
    for m in d.get('neededInstalledMods', []) or []:
        if m not in MODIDS:
            return False
    for m in d.get('neededUninstalledMods', []) or []:
        if m in MODIDS:
            return False
    return True


def merge_cond(dst, src):
    for k, v in (src or {}).items():
        if isinstance(v, list) and isinstance(dst.get(k), list):
            dst[k] = dst[k] + v
        else:
            dst.setdefault(k, v)


def conv_biomes(refs):
    kept = []
    for r in refs or []:
        real = biome_ref(r)
        if real:
            kept.append(r)
    return kept

TIME_NAMES = {'day', 'night', 'dawn', 'dusk', 'morning', 'noon', 'afternoon', 'midnight', 'twilight', 'predawn', 'evening'}
USED_TAGS = set()
for rel, f in spawn_files.items():
    d = jload(f)
    if not d:
        continue
    if d.get('enabled') is False or not mods_ok(d):
        drop_stats['file_disabled'] += 1
        continue
    for s in d.get('spawns', []):
        if not mods_ok(s):
            drop_stats['mods'] += 1
            continue
        cond = dict(s.get('condition') or {})
        anti = dict(s.get('anticondition') or {})
        ctx = s.get('spawnablePositionType') or s.get('context')
        for p in s.get('presets', []) or []:
            pr = PRESETS.get(p, {})
            merge_cond(cond, pr.get('condition'))
            merge_cond(anti, pr.get('anticondition'))
            ctx = ctx or pr.get('spawnablePositionType') or pr.get('context')
        if 'biomes' in cond:
            kb = conv_biomes(cond['biomes'])
            if not kb:
                drop_stats['no_biome'] += 1
                continue
        else:
            kb = []
        kanti = conv_biomes(anti.get('biomes'))
        USED_TAGS.update(kb); USED_TAGS.update(kanti)
        targets = []
        if s.get('pokemon'):
            targets.append(s['pokemon'])
        for h in s.get('herdablePokemon', []) or []:
            if isinstance(h, dict) and h.get('pokemon'):
                targets.append(h['pokemon'])
        o = {'b': kb, 'k': s.get('bucket'), 'l': s.get('level') or s.get('levelRange'), 'w': s.get('weight'), 'c': ctx}
        if kanti:
            o['nb'] = kanti
        extra = {}
        for key in ('timeRange', 'isRaining', 'isThundering', 'canSeeSky', 'minY', 'maxY', 'minSkyLight', 'maxSkyLight', 'minLight', 'maxLight', 'moonPhase', 'isSlimeChunk', 'minLureLevel', 'maxLureLevel', 'rodType', 'bait', 'key_item', 'lunarEvent', 'dimensions'):
            if key in cond:
                extra[key] = cond[key]
        if cond.get('structures'):
            extra['structures'] = cond['structures']
        if anti.get('structures'):
            extra['notStructures'] = anti['structures']
        if anti.get('timeRange'):
            extra['notTime'] = anti['timeRange']
        if anti.get('canSeeSky') is not None:
            extra['notSky'] = anti['canSeeSky']
        if 'key_item' in extra:
            ki = extra['key_item']
            extra['key_item'] = item_name(ki if isinstance(ki, str) else (ki.get('item') if isinstance(ki, dict) else str(ki)))
        if cond.get('neededNearbyBlocks'):
            extra['nearby'] = cond['neededNearbyBlocks']
        if cond.get('neededBaseBlocks') and s.get('presets') and 'natural' not in s.get('presets'):
            extra['base'] = cond['neededBaseBlocks']
        if s.get('presets'):
            extra['presets'] = [p for p in s['presets'] if p not in ('natural', 'wild')]
            if not extra['presets']:
                del extra['presets']
        if s.get('weightMultipliers') or s.get('weightMultiplier'):
            wm = s.get('weightMultipliers') or [s.get('weightMultiplier')]
            extra['wm'] = [{'x': m.get('multiplier'), 'c': {k: v for k, v in (m.get('condition') or {}).items() if k in ('timeRange', 'isRaining', 'isThundering', 'moonPhase', 'canSeeSky')}} for m in wm if isinstance(m, dict)]
        if extra:
            o['x'] = extra
        o['src'] = rel.split('/')[0]
        for t in targets:
            sp, props = parse_props(t)
            if not sp:
                continue
            oo = dict(o)
            if props:
                oo['p'] = props
            SP[sp].append(oo)
print('spawns', sum(len(v) for v in SP.values()), dict(drop_stats))

# ---------------------------------------------------------------- raids
def json5(p):
    t = open(p, encoding='utf-8-sig').read()
    t = re.sub(r'(?<![:"])//.*$', '', t, flags=re.M)
    t = re.sub(r',(\s*[}\]])', r'\1', t)
    return json.loads(t)

RAID_LAYERS = [os.path.join(L, '40_raid_jar'), os.path.join(L, '41_raid_dp'), os.path.join(INST, 'kubejs')]
TIER_KEYS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven']
TIERS = {}
for i, tk in enumerate(TIER_KEYS):
    try:
        j = json5(os.path.join(INST, 'config', 'cobblemonraiddens', 'tier_%s.json5' % tk))
        TIERS[i + 1] = {'lv': j.get('boss_level'), 'shiny': j.get('shiny_rate'), 'ha': j.get('ha_rate'), 'iv': j.get('ivs'), 'players': j.get('max_players')}
    except Exception as e:
        print('tier cfg', tk, e)
try:
    TIER_W = json5(os.path.join(INST, 'config', 'cobblemonraiddens', 'common.json5'))['dimension_tier_weights']['minecraft:overworld']
except Exception:
    TIER_W = None

boss_files = {}
for layer in RAID_LAYERS:
    for f in glob.glob(os.path.join(layer, 'data', 'cobblemonraiddens', 'raid', 'boss', '*.json')):
        boss_files[os.path.basename(f)[:-5]] = f
raid_tags = collections.defaultdict(list)
for layer in RAID_LAYERS:
    for f in glob.glob(os.path.join(layer, 'data', 'cobblemonraiddens', 'tags', 'raid', 'boss', '**', '*.json'), recursive=True):
        j = jload(f)
        if j:
            tid = os.path.splitext(os.path.relpath(f, os.path.join(layer, 'data', 'cobblemonraiddens', 'tags', 'raid', 'boss')))[0].replace('\\', '/')
            raid_tags[tid] = (j.get('values', []) if j.get('replace') else raid_tags[tid] + j.get('values', []))


def raid_tag_ids(t, st=()):
    out = set()
    for v in raid_tags.get(t, []):
        v = v.get('id') if isinstance(v, dict) else v
        if v.startswith('#'):
            if v[1:].split(':')[-1] not in st:
                out |= raid_tag_ids(v[1:].split(':')[-1], st + (t,))
        else:
            out.add(v.split(':')[-1])
    return out

ARENA = collections.defaultdict(set)
for layer in RAID_LAYERS:
    for f in glob.glob(os.path.join(layer, 'data', 'cobblemonraiddens', 'raid', 'boss_additions', '*.json')):
        try:
            j = json5(f)
        except Exception as e:
            print('arena', f, e); continue
        dens = (j.get('additions') or {}).get('den', [])
        for inc in j.get('include', []):
            ids = raid_tag_ids(inc[1:].split(':')[-1]) if inc.startswith('#') else {inc.split(':')[-1]}
            if inc.startswith('#') and not ids:
                ids = {inc[1:].split(':')[-1]}
            for b in ids:
                for d in dens:
                    ARENA[b].add(d.split('/')[-1])
RAIDS = collections.defaultdict(list)
for bid, f in boss_files.items():
    j = jload(f)
    if not j or not j.get('pokemon'):
        continue
    pk = j['pokemon']
    sp, props = parse_props(pk.get('species', ''))
    for cp in pk.get('custom_properties', []) or []:
        props.append('%s=%s' % (cp.get('name'), cp.get('value')))
    tier = TIER_KEYS.index(j.get('raid_tier', 'TIER_ONE').split('_')[-1].lower()) + 1 if j.get('raid_tier') else None
    o = {'id': bid, 'tier': tier, 'type': (j.get('raid_type') or '').lower(), 'f': (j.get('raid_feature') or 'DEFAULT').lower(), 'w': j.get('weight')}
    if props:
        o['p'] = props
    if ARENA.get(bid):
        o['den'] = sorted(ARENA[bid])
    if j.get('den'):
        o['den'] = sorted(set(o.get('den', [])) | {str(d).split('/')[-1] for d in (j['den'] if isinstance(j['den'], list) else [j['den']])})
    RAIDS[sp].append(o)
print('raid bosses', sum(len(v) for v in RAIDS.values()), 'arenas', len(ARENA))

# ---------------------------------------------------------------- tag labels
TAG_KO = json.load(open(os.path.join(S, 'build', 'tag_ko.json'), encoding='utf8')) if os.path.exists(os.path.join(S, 'build', 'tag_ko.json')) else {}
TAGS_OUT = {}


def tag_label(ref):
    t = ref[1:] if ref.startswith('#') else ref
    ns, _, p = t.partition(':')
    last = p.split('/')[-1]
    en = last.replace('is_', '').replace('has_block', 'has').replace('_', ' ').title()
    if p.startswith('nether/'):
        en = 'Nether ' + en
    if p.startswith('has_block/'):
        en = 'Has ' + last.replace('_', ' ').title()
    ko = TAG_KO.get(t, en)
    return [en, ko]

for ref in sorted(USED_TAGS):
    if ref.startswith('#'):
        TAGS_OUT[ref] = {'n': tag_label(ref), 'b': sorted(biome_ref(ref))}

# ---------------------------------------------------------------- forms / features
HIDE_FORM = re.compile(r'-bias$|^normal$', re.I)


def form_slug(name):
    n = name.lower().replace('!', ' exclamation ').replace('?', ' question ')
    return re.sub(r'[^a-z0-9]+', '-', n).strip('-')


def form_label(sp_key, fname):
    slug = form_slug(fname)
    for k in ('cobblemon.ui.pokedex.info.form.%s-%s' % (sp_key, slug), 'cobblemon.ui.pokedex.info.form.' + slug):
        t = tr(k)
        if t:
            return t
    return [fname, fname]

FEATURES = {}
for rel, f in layered_files('species_features').items():
    j = jload(f)
    if j:
        FEATURES[os.path.splitext(os.path.basename(f))[0]] = j
FEAT_ASSIGN = collections.defaultdict(set)
for rel, f in layered_files('species_feature_assignments').items():
    j = jload(f)
    if j:
        for p in j.get('pokemon', []):
            FEAT_ASSIGN[p.lower()].update(j.get('features', []))

# ---------------------------------------------------------------- assemble
def base_info(src, fallback=None):
    fb = fallback or {}
    g = lambda k: src.get(k, fb.get(k))
    o = {
        't': [x for x in [src.get('primaryType'), src.get('secondaryType')] if x],
        's': stats(g('baseStats')),
        'a': abilities(g('abilities')),
        'h': g('height'), 'wt': g('weight'),
    }
    return o

out = []
for key, sp in species.items():
    if not sp.get('implemented') and not RAIDS.get(key) and not SP.get(key):
        continue
    num = sp.get('nationalPokedexNumber')
    o = {'id': key, 'no': num, 'n': species_name(key), 'gen': sp.get('_gen', '').replace('generation', '')}
    o.update(base_info(sp))
    desc = (sp.get('pokedex') or [None])[0]
    if desc:
        o['d'] = tr(desc)
    if not sp.get('implemented'):
        o['ni'] = 1
    o['eg'] = sp.get('eggGroups', [])
    o['mr'] = sp.get('maleRatio')
    o['ec'] = sp.get('eggCycles')
    o['cr'] = sp.get('catchRate')
    o['bf'] = sp.get('baseFriendship')
    o['xg'] = sp.get('experienceGroup')
    o['bx'] = sp.get('baseExperienceYield')
    ev = sp.get('evYield') or {}
    o['ev'] = [ev.get(k, 0) for k in STAT_KEYS]
    o['lab'] = [x for x in sp.get('labels', []) if not x.startswith('gen')]
    if sp.get('preEvolution'):
        o['pre'] = parse_props(sp['preEvolution'])[0]
    evs = conv_evos(sp.get('evolutions'))
    if evs:
        o['evo'] = evs
    if sp.get('riding'):
        o['ride'] = sorted((sp['riding'].get('behaviours') or {}).keys()) or ['yes']
    if sp.get('shoulderMountable'):
        o['sh'] = 1
    drops = (sp.get('drops') or {}).get('entries', [])
    if drops:
        o['dr'] = [{'i': d.get('item'), 'n': item_name(d.get('item')), 'q': d.get('quantityRange'), 'pc': d.get('percentage')} for d in drops if d.get('item')]
    forms = []
    for fo in sp.get('forms', []) or []:
        nm = fo.get('name', '')
        if HIDE_FORM.search(nm):
            continue
        fi = {'name': nm, 'slug': form_slug(nm), 'n': form_label(key, nm), 'asp': fo.get('aspects', [])}
        fb = base_info(fo, sp)
        if 'primaryType' in fo:
            fb['t'] = [x for x in [fo.get('primaryType'), fo.get('secondaryType')] if x]
        else:
            fb['t'] = o['t']
        fi.update(fb)
        if fo.get('battleOnly'):
            fi['bo'] = 1
        fe = conv_evos(fo.get('evolutions'))
        if fe:
            fi['evo'] = fe
        if fo.get('preEvolution'):
            fi['pre'] = parse_props(fo['preEvolution'])[0]
        if fo.get('pokedex'):
            fi['d'] = tr(fo['pokedex'][0])
        if 'eggGroups' in fo:
            fi['eg'] = fo['eggGroups']
        forms.append(fi)
    if forms:
        o['forms'] = forms
    feats = []
    for fk in sorted(FEAT_ASSIGN.get(key, [])):
        fd = FEATURES.get(fk)
        if fd and fd.get('type') == 'choice' and fd.get('choices'):
            feats.append({'k': fk, 'c': fd['choices'], 'asp': fd.get('aspect', True)})
    if feats:
        o['feat'] = feats
    if SP.get(key):
        o['sp'] = SP[key]
    if RAIDS.get(key):
        o['raid'] = sorted(RAIDS[key], key=lambda r: (r['tier'] or 0, r['id']))
    # map spawn/raid properties to a form slug via aspects
    asp2form = {}
    for fi in forms:
        for a in fi['asp']:
            asp2form[a.lower()] = fi['slug']
        asp2form[fi['slug']] = fi['slug']
        asp2form[fi['name'].lower()] = fi['slug']
    for coll in (o.get('sp', []), o.get('raid', [])):
        for e in coll:
            for pr in e.get('p', []):
                k, _, v = pr.lower().partition('=')
                cand = [k, v, v.replace('alola', 'alolan').replace('galar', 'galarian').replace('hisui', 'hisuian').replace('paldea', 'paldean')]
                if k in ('region_bias',):
                    cand = [v + 'n' if v.endswith('a') else v, v, {'hisui': 'hisuian', 'galar': 'galarian', 'paldea': 'paldean', 'alola': 'alolan'}.get(v, v)]
                for c in cand:
                    if c and c in asp2form:
                        e['fm'] = asp2form[c]
                        break
            if 'fm' not in e and 'tier' in e:
                bid = e['id']
                for cand in (('mega-x', 'mega_x'), ('mega-y', 'mega_y'), ('gmax', 'gmax'), ('mega', 'mega')):
                    if cand[1] in bid and cand[0] in asp2form:
                        e['fm'] = cand[0]; break
    out.append(o)

out.sort(key=lambda x: (x['no'] or 99999, x['id']))
meta = {
    'buckets': {'common': 94.0, 'uncommon': 5.0, 'rare': 0.7, 'ultra-rare': 0.3},
    'shinyRate': 8192,
    'raidTiers': TIERS,
    'raidTierWeights': TIER_W,
    'biomes': BIOME_OUT,
    'tags': TAGS_OUT,
    'types': {t: type_name(t) for t in ['normal', 'fire', 'water', 'grass', 'electric', 'ice', 'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy']},
    'eggGroups': {g: tr('cobblemon.egg_group.' + g, g) for g in ['monster', 'water_1', 'bug', 'flying', 'field', 'fairy', 'grass', 'human_like', 'water_3', 'mineral', 'amorphous', 'water_2', 'ditto', 'dragon', 'undiscovered']},
    'names': {k: species_name(k) for k in species},
    'abil': {a['id']: tr('cobblemon.ability.%s.desc' % a['id']) for p in out for a in (p.get('a') or []) + [x for f in p.get('forms', []) for x in (f.get('a') or [])] if tr('cobblemon.ability.%s.desc' % a['id'])},
}
json.dump({'meta': meta, 'pokemon': out}, open(os.path.join(OUT, 'pokedex.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
json.dump(sorted(USED_TAGS), open(os.path.join(S, 'build', 'used_tags.json'), 'w'), indent=0)
print('wrote', len(out), os.path.getsize(os.path.join(OUT, 'pokedex.json')) // 1024, 'KB')
