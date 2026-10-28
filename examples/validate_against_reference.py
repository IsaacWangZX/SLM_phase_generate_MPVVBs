"""Check the package against the original MATLAB .fig results (M = 30).

Usage:  python examples/validate_against_reference.py [path/to/figure]
Default reference folder: ../../figure relative to this file.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import numpy as np
from mpvvb import Layer, load_fig_image, load_fig_quiver, simulate, slm_phase
from mpvvb.paper import PAPER_CASES

ref = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, '..', '..', 'figure'))
if not os.path.isdir(ref):
    raise SystemExit('reference folder not found: %s' % ref)

n = 500
c = np.arange(n) - n / 2
cx, cy = np.meshgrid(c, c)
mask = np.hypot(cx, cy) <= n / 2 - 5
allc = []
for G in PAPER_CASES:
    for C in G['cases']:
        Pref = load_fig_image(os.path.join(ref, G['folder'], C['phaseStem'] + '.fig')) * 2 * np.pi
        P = slm_phase(C['layers'], M=30, shape=Pref.shape, R0=500)
        pm = abs(np.exp(1j * (Pref - P)).mean())
        S = simulate(C['layers'])
        rs = []
        for tag, I in zip(('total', '00', '45', '90'), [S['Itotal']] + [S['Ia'][:, :, k] for k in range(3)]):
            R = load_fig_image(os.path.join(ref, G['folder'], C['stem'] + tag + '.fig'))[750:1250, 750:1250]
            rs.append(np.corrcoef(R[mask], I[mask])[0, 1])
        allc += rs
        print('%-16s %-24s phase %.4f | %s' % (G['name'], C['stem'], pm, '  '.join('%.3f' % r for r in rs)))
print('intensity correlation: mean %.3f, min %.3f' % (np.mean(allc), np.min(allc)))

pol = os.path.join(ref, '偏振分布')
for name in ('0.5', '1', '1.5', '2', '2.5', '3'):
    f = os.path.join(pol, name + '.fig')
    if os.path.exists(f):
        q = load_fig_quiver(f)
        Q = simulate([Layer(0.3, float(name))], rhoMax=0.02, nOut=4, phaseCrop=4)['quiver']
        ok = abs(np.exp(2j * (np.arctan2(q['VData'], q['UData']) - np.arctan2(Q['V'], Q['U']))).mean())
        print('polarization order %-4s match %.4f' % (name, ok))
