"""Convierte el fichero abierto de distintivos de la DGT en ficheros pequeños consultables desde la web.
m/XXX.bin : matrículas 9999XXX, 4 bits por número (5000 bytes). 0=no existe 1=B 2=C 3=ECO 4=0 (turismos y resto) 5=sin distintivo 6=B 7=C 8=ECO 9=0 (motos)
o/PPDD.txt: resto de formatos, una línea "resto:código" por matrícula, agrupadas por letras iniciales + 2 primeras cifras."""
import sys, os, re, collections, datetime
src, out = sys.argv[1], sys.argv[2]
CODE = {'16TB': 1, '16TC': 2, '16TE': 3, '16T0': 4, 'SIN DISTINTIVO': 5, '16MB': 6, '16MC': 7, '16ME': 8, '16M0': 9}
modern = collections.defaultdict(lambda: bytearray(5000))
old = collections.defaultdict(list)
rm = re.compile(r'^(\d{4})([A-Z]{3})$'); ro = re.compile(r'^([A-Z]{1,2})(\d{3,})([A-Z]*)$')
n_ok = n_skip = 0
with open(src, encoding='latin-1') as f:
    next(f)
    for line in f:
        p, _, c = line.rstrip('\r\n').partition('|')
        v = CODE.get(c.strip()); p = p.strip().upper()
        if not v:
            n_skip += 1; continue
        m = rm.match(p)
        if m:
            n = int(m.group(1)); b = modern[m.group(2)]; i = n >> 1
            b[i] = ((b[i] & 0x0F) | (v << 4)) if n & 1 else ((b[i] & 0xF0) | v)
            n_ok += 1; continue
        m = ro.match(p)
        if m:
            pre, dig, suf = m.groups()
            old[pre + dig[:2]].append(f"{dig[2:]}{suf}:{v}"); n_ok += 1
        else:
            n_skip += 1
os.makedirs(out + '/m', exist_ok=True); os.makedirs(out + '/o', exist_ok=True)
for k, b in modern.items():
    open(f"{out}/m/{k}.bin", 'wb').write(bytes(b))
for k, lst in old.items():
    lst.sort(); open(f"{out}/o/{k}.txt", 'w').write('\n'.join(lst) + '\n')
open(f"{out}/fecha.txt", 'w').write(datetime.date.today().strftime('%d/%m/%Y'))
print('matriculas', n_ok, 'descartadas', n_skip, 'series', len(modern), 'grupos', len(old))

# Última serie de matrícula registrada (la serie de letras más alta con vehículos en el fichero)
L = 'BCDFGHJKLMNPRSTVWXYZ'
ix = lambda k: L.index(k[0]) * 400 + L.index(k[1]) * 20 + L.index(k[2])
ok = [k for k in modern if all(c in L for c in k)]
if ok:
    top = max(ok, key=ix); b = modern[top]
    nums = [n for n in range(10000) if ((b[n >> 1] >> 4) if n & 1 else (b[n >> 1] & 15))]
    import json as _j
    _j.dump({"serie": top, "numero": max(nums) if nums else None, "fecha": datetime.date.today().strftime('%d/%m/%Y')}, open(f"{out}/ultima.json", 'w'))
    print('ultima serie', top, max(nums) if nums else None)
