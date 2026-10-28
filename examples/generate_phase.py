"""Template: edit the variables below and run  python examples/generate_phase.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import matplotlib
matplotlib.use('Agg')
from mpvvb import Layer, save_phase, slm_phase
from mpvvb.plotting import plot_phase

M = 30                      # order of the vector vortex polarizer
LAYERS = [                  # Layer(d, m, l=None, betaDeg=0); l defaults to 0.5 for half-integer m
    Layer(d=0.3, m=0.5),
    Layer(d=0.5, m=2),
]
WEIGHTS = None              # outer -> inner; None = (1, -0.8, 0.6)
SHAPE = (1080, 1920)        # SLM height, width in pixels
R0 = 500                    # SLM pixels per unit rho (axicon period = d*R0 pixels)
GRAY_2PI = 255              # gray level equal to 2*pi on the SLM
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

phase = slm_phase(LAYERS, M=M, shape=SHAPE, R0=R0, weights=WEIGHTS)
name = 'M%g_' % M + '_'.join('d%g_m%g' % (L.d, L.m) for L in LAYERS)
save_phase(phase, os.path.join(OUT_DIR, name + '.png'), gray2pi=GRAY_2PI)
save_phase(phase, os.path.join(OUT_DIR, name + '.npy'))
ax = plot_phase(phase)
ax.figure.savefig(os.path.join(OUT_DIR, name + '_preview.png'), dpi=120, bbox_inches='tight')
print('saved to', OUT_DIR, name)
