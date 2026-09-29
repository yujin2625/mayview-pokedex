# Resolves render jobs (model/texture/layers/pose) for every species/form, normal and shiny.
import json, os, re, glob, collections

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = os.path.join(S, 'layers')
INST = r'C:/Users/Dumaru/curseforge/minecraft/Instances/Mayview (with Cobblemon)'
DEX = json.load(open(os.path.join(INST, 'guides', 'pokedex', 'data', 'pokedex.json'), encoding='utf8'))

# asset roots, low -> high priority (follows options.txt resource pack order)
# third-party model addons for species this pack has no model for (lowest priority, gap-fill only)
EXTRA = []  # addon gap-fill disabled at user's request (models differed from in-game)
EXTRA_SPECIES = {'celesteela', 'ironjugulis', 'ironhands', 'ironboulder', 'tinglu', 'virizion', 'pheromosa', 'tympole', 'palpitoad', 'seismitoad'}
ROOTS = EXTRA + [
    '00_cobblemon', '01_integrations', '02_msd', '03_mal', '04_paleo', '05_cobblenav',
    '10_whimscape', '11_e19',
    '00_cobblemon/resourcepacks/regionbiasforms', '02_msd/resourcepacks/regionbiasmsd',
    '12_mayviewres', '13_atm_rp',
]
ASSET = {}
for r in ROOTS:
    base = os.path.join(L, r, 'assets')
    for f in glob.glob(os.path.join(base, '*', '**', '*'), recursive=True):
        if os.path.isfile(f):
            rel = os.path.relpath(f, base).replace('\\', '/')
            ASSET[rel] = os.path.relpath(f, L).replace('\\', '/')
print('assets', len(ASSET))


def loc(rid):
    """'cobblemon:textures/x.png' -> assets rel path"""
    ns, _, p = rid.partition(':')
    if not p:
        ns, p = 'cobblemon', ns
    return ns + '/' + p

MODELS, POSERS, RESOLVERS = {}, {}, collections.defaultdict(list)
for rel, full in ASSET.items():
    m = re.match(r'^([^/]+)/bedrock/pokemon/models/(?:.+/)?([^/]+)\.json$', rel)
    if m:
        MODELS[m.group(1) + ':' + m.group(2)] = full
        continue
    m = re.match(r'^([^/]+)/bedrock/pokemon/posers/(?:.+/)?([^/]+)\.json$', rel)
    if m:
        POSERS[m.group(1) + ':' + m.group(2)] = full
        continue
    if re.match(r'^[^/]+/bedrock/pokemon/resolvers/.+\.json$', rel):
        try:
            j = json.load(open(os.path.join(L, full), encoding='utf-8-sig'))
        except Exception as e:
            print('bad resolver', full, e); continue
        sp = j.get('species', '').split(':')[-1]
        if full.split('/')[0] in EXTRA and sp not in EXTRA_SPECIES:
            continue
        RESOLVERS[sp].append(j)

ANIMS = {}
for rel, full in ASSET.items():
    if re.match(r'^[^/]+/bedrock/pokemon/animations/.+\.json$', rel):
        try:
            j = json.load(open(os.path.join(L, full), encoding='utf-8-sig'))
        except Exception:
            continue
        for k in (j.get('animations') or {}):
            ANIMS[k] = full
print('models', len(MODELS), 'posers', len(POSERS), 'resolver species', len(RESOLVERS), 'anims', len(ANIMS))


def tex_first(t):
    if isinstance(t, dict):
        fr = t.get('frames') or []
        return fr[0] if fr else None
    return t


def resolve(sp, aspects):
    A = set(aspects)
    res = {'poser': None, 'model': None, 'texture': None, 'layers': []}
    for r in sorted(RESOLVERS.get(sp, []), key=lambda r: r.get('order', 0)):
        for v in r.get('variations', []):
            if set(v.get('aspects', [])) <= A:
                for k in ('poser', 'model', 'texture'):
                    if v.get(k):
                        res[k] = v[k]
                if 'layers' in v:
                    res['layers'] = v['layers']
    return res


def pose_for(poser_id):
    f = POSERS.get(poser_id if ':' in poser_id else 'cobblemon:' + poser_id)
    if not f:
        return None, []
    try:
        j = json.load(open(os.path.join(L, f), encoding='utf-8-sig'))
    except Exception:
        t = open(os.path.join(L, f), encoding='utf-8-sig').read()
        t = re.sub(r'(?<![:"])//.*$', '', t, flags=re.M)
        t = re.sub(r',(\s*[}\]])', r'\1', t)
        try:
            j = json.loads(t)
        except Exception as e:
            print('bad poser', f, e)
            return None, []
    poses = j.get('poses') or {}
    pick = None
    for want in ('PROFILE', 'PORTRAIT', 'STAND', 'NONE'):
        for name, p in poses.items():
            if want in (p.get('poseTypes') or []) and not p.get('isBattle') and not p.get('isTouchingWater'):
                pick = p; break
        if pick:
            break
    if not pick and poses:
        pick = list(poses.values())[0]
    anims = []
    al = (pick or {}).get('animations', []) or []
    if isinstance(al, dict):
        al = list(al.values())
    for a in al:
        a = a if isinstance(a, str) else json.dumps(a)
        m = re.search(r"bedrock\(\s*'?\"?([\w\-]+)'?\"?\s*,\s*'?\"?([\w\-\.]+)'?\"?", a)
        if m:
            aid = 'animation.%s.%s' % (m.group(1), m.group(2))
            if aid in ANIMS:
                anims.append({'id': aid, 'f': ANIMS[aid]})
    return anims, (pick or {}).get('transformedParts', [])


def asset_url(rid):
    if not rid:
        return None
    p = ASSET.get(loc(rid))
    return p


def job(sp, name, aspects):
    r = resolve(sp, aspects)
    if not r['model']:
        return None
    mid = r['model'] if ':' in r['model'] else 'cobblemon:' + r['model']
    mfile = MODELS.get(mid) or MODELS.get(mid.replace('.geo', '') + '.geo')
    if sp in EXTRA_SPECIES:
        for root in EXTRA:
            hit = [f for f in glob.glob(os.path.join(L, root, 'assets', '*', 'bedrock', 'pokemon', 'models', '**', mid.split(':')[-1] + '.json'), recursive=True)]
            if hit:
                mfile = os.path.relpath(hit[0], L).replace(os.sep, '/'); break
    tex = asset_url(tex_first(r['texture']))
    if not mfile or not tex:
        return None
    layers = []
    for ly in r['layers'] or []:
        t = asset_url(tex_first(ly.get('texture')))
        if t:
            layers.append({'t': t, 'e': 1 if ly.get('emissive') else 0, 'tr': 1 if ly.get('translucent') else 0})
    anims, tparts = pose_for(r['poser'] or sp)
    return {'id': name, 'model': mfile, 'tex': tex, 'layers': layers, 'anims': anims or [], 'tparts': tparts or [], 'key': (mfile, tex, tuple(l['t'] for l in layers))}

jobs, missing = [], []
for p in DEX['pokemon']:
    sp = p['id']
    g = [] if p.get('mr') == -1 else (['female'] if p.get('mr') == 0 else ['male'])
    variants = [('', [])]
    for fo in p.get('forms', []):
        variants.append(('__' + fo['slug'], [a for a in fo['asp']]))
    base_key = None
    for suffix, asp in variants:
        for shiny in (False, True):
            name = sp + suffix + ('__shiny' if shiny else '')
            j = job(sp, name, g + asp + (['shiny'] if shiny else []))
            if not j:
                missing.append(name); continue
            if suffix and not shiny and base_key and j['key'] == base_key:
                break  # form looks identical to base
            if not suffix and not shiny:
                base_key = j['key']
            jobs.append(j)
for j in jobs:
    del j['key']
json.dump(jobs, open(os.path.join(S, 'render', 'jobs.json'), 'w'), separators=(',', ':'))
print('jobs', len(jobs), 'missing', len(missing), missing[:40])
