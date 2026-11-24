"""Precios de carburantes del Ministerio (geoportal de gasolineras) -> carb/pXX.json por provincia + carb/index.json."""
import json, sys, urllib.request, os, collections
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
req = urllib.request.Request("https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/",
                             headers={'User-Agent': 'Mozilla/5.0 (CocheCuentas)', 'Accept': 'application/json'})
d = json.loads(urllib.request.urlopen(req, timeout=180).read().decode('utf-8-sig'))
F = {'g95': 'Precio Gasolina 95 E5', 'gA': 'Precio Gasoleo A', 'g98': 'Precio Gasolina 98 E5', 'glp': 'Precio Gases licuados del petróleo'}
num = lambda s: float(s.replace(',', '.')) if s and s.strip() else None
prov = collections.defaultdict(list); names = {}; sums = collections.defaultdict(list); cent = collections.defaultdict(list)
for e in d['ListaEESSPrecio']:
    try:
        lat, lon = num(e['Latitud']), num(e['Longitud (WGS84)'])
    except Exception:
        continue
    if lat is None or lon is None:
        continue
    pr = {k: num(e.get(v, '')) for k, v in F.items()}
    if not any(pr.values()):
        continue
    p = e['IDProvincia']; names[p] = e['Provincia'].title()
    prov[p].append([e['Rótulo'].strip().title(), e['Dirección'].strip().title(), e['Municipio'].strip(), round(lat, 5), round(lon, 5),
                    pr['g95'], pr['gA'], pr['g98'], pr['glp'], e.get('Horario', '').strip()])
    cent[p].append((lat, lon))
    for k, v in pr.items():
        if v: sums[k].append(v)
for p, lst in prov.items():
    json.dump(lst, open(f"{out}/p{p}.json", 'w'), ensure_ascii=False, separators=(',', ':'))
idx = {"fecha": d.get('Fecha'), "medias": {k: round(sum(v) / len(v), 3) for k, v in sums.items() if v},
       "provincias": sorted([[p, names[p], round(sum(a for a, _ in c) / len(c), 4), round(sum(b for _, b in c) / len(c), 4)] for p, c in cent.items()], key=lambda x: x[1])}
json.dump(idx, open(f"{out}/index.json", 'w'), ensure_ascii=False, separators=(',', ':'))
print('gasolineras', sum(len(v) for v in prov.values()), 'provincias', len(prov), idx['medias'])
