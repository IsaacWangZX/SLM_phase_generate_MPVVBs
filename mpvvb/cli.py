"""Command line interface:  python -m mpvvb {phase,simulate,paper} ...

Examples
  python -m mpvvb phase --M 30 --layer 0.3 0.5 --layer 0.5 2 -o phase.png
  python -m mpvvb phase --M 20 --layer 0.4 1.5 --shape 1080 1920 --R0 540 --gray2pi 213 -o slm.bmp
  python -m mpvvb simulate --M 30 --layer 0.3 1 -o out/d0.3m1
  python -m mpvvb paper -o paper_outputs
"""
import argparse
import os
import sys

import numpy as np

from .core import Layer, SimOptions, simulate, slm_phase
from .fileio import save_phase, save_simulation


def _layers(raw):
    out = []
    for vals in raw:
        if not 2 <= len(vals) <= 4:
            raise SystemExit('--layer expects: d m [l [betaDeg]]')
        d, m = vals[0], vals[1]
        l = vals[2] if len(vals) > 2 else None
        beta = vals[3] if len(vals) > 3 else 0.0
        out.append(Layer(d, m, l, beta))
    return out


def _weights(raw):
    if raw is None:
        return None
    return [complex(s.replace('i', 'j')) for s in raw]


def _add_beam_args(p):
    p.add_argument('--M', type=float, default=30, help='order of the vector vortex polarizer (default 30)')
    p.add_argument('--layer', type=float, nargs='+', action='append', required=True,
                   metavar='V', help='one ring: d m [l [betaDeg]]; repeat for multiple rings')
    p.add_argument('--weights', nargs='+', default=None,
                   help='layer weights outer->inner (default 1 -0.8 0.6); complex like 0.5+0.2i allowed')


def _cmd_phase(a):
    layers = _layers(a.layer)
    center = tuple(a.center) if a.center else None
    P = slm_phase(layers, M=a.M, shape=(a.shape[0], a.shape[1]), R0=a.R0,
                  weights=_weights(a.weights), center=center)
    save_phase(P, a.output, gray2pi=a.gray2pi, bits=a.bits)
    print('saved', a.output, '(%d x %d)' % P.shape)
    if a.preview:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from .plotting import plot_phase
        ax = plot_phase(P)
        ax.set_title('M=%g  ' % a.M + '  '.join('(d=%g, m=%g)' % (L.d, L.m) for L in layers))
        root = os.path.splitext(a.output)[0]
        ax.figure.savefig(root + '_preview.png', dpi=120, bbox_inches='tight')
        print('saved', root + '_preview.png')


def _cmd_simulate(a):
    import matplotlib
    matplotlib.use('Agg')
    from .plotting import plot_rows
    layers = _layers(a.layer)
    o = SimOptions(M=a.M, weights=_weights(a.weights), fieldMode=a.mode, analyzerDeg=a.analyzer,
                   hwpDeg=a.hwp)
    S = simulate(layers, o)
    root = a.output
    save_phase(S['phaseSLM'], root + '_SLM_phase.png')
    save_simulation(S, root + '.npz')
    label = 'M=%g  ' % a.M + ' / '.join('d=%g m=%g' % (L.d, L.m) for L in S['layers'])
    fig = plot_rows([S], [label])
    fig.savefig(root + '_panel.png', dpi=110)
    print('saved', root + '_SLM_phase.png,', root + '.npz,', root + '_panel.png')


def _cmd_paper(a):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from .paper import PAPER_CASES
    from .plotting import plot_rows
    for G in PAPER_CASES:
        gdir = os.path.join(a.output, G['name'])
        res, labs = [], []
        for C in G['cases']:
            S = simulate(C['layers'], SimOptions(M=a.M, fieldMode=a.mode))
            save_phase(S['phaseSLM'], os.path.join(gdir, C['stem'] + '_SLM_phase.png'))
            save_simulation(S, os.path.join(gdir, C['stem'] + '.npz'))
            res.append(S); labs.append(C['label'])
            print(G['name'], C['stem'])
        fig = plot_rows(res, labs, G['title'])
        fig.savefig(os.path.join(a.output, G['name'] + '_sim.png'), dpi=110)
        plt.close(fig)
    print('done ->', a.output)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='python -m mpvvb', description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('phase', help='write an SLM phase map')
    _add_beam_args(p)
    p.add_argument('--shape', type=int, nargs=2, default=[1000, 1000], metavar=('H', 'W'),
                   help='SLM size in pixels, height width (default 1000 1000)')
    p.add_argument('--R0', type=float, default=500,
                   help='SLM pixels per unit rho; axicon period = d*R0 pixels (default 500)')
    p.add_argument('--center', type=float, nargs=2, default=None, metavar=('ROW', 'COL'),
                   help='beam axis position in pixels (default array center)')
    p.add_argument('--gray2pi', type=int, default=255, help='gray level that equals 2*pi (default 255)')
    p.add_argument('--bits', type=int, default=8, choices=[8, 16], help='image bit depth (default 8)')
    p.add_argument('--preview', action='store_true', help='also save a color preview')
    p.add_argument('-o', '--output', required=True, help='.png/.bmp/.tif (gray), .npy/.csv/.mat (radians)')
    p.set_defaults(func=_cmd_phase)

    p = sub.add_parser('simulate', help='SLM phase + focal-plane intensities')
    _add_beam_args(p)
    p.add_argument('--mode', default='ideal', choices=['ideal', 'slm'])
    p.add_argument('--analyzer', type=float, nargs='+', default=[0, 45, 90], help='analyzer angles in deg')
    p.add_argument('--hwp', type=float, default=None, help='HWP fast-axis angle in deg (optional)')
    p.add_argument('-o', '--output', required=True, help='output path prefix, e.g. out/beam1')
    p.set_defaults(func=_cmd_simulate)

    p = sub.add_parser('paper', help='reproduce Figs. 2-5 of the manuscript')
    p.add_argument('--M', type=float, default=30)
    p.add_argument('--mode', default='ideal', choices=['ideal', 'slm'])
    p.add_argument('-o', '--output', default='paper_outputs')
    p.set_defaults(func=_cmd_paper)

    a = ap.parse_args(argv)
    a.func(a)


if __name__ == '__main__':
    main(sys.argv[1:])
