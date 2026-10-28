"""Beams of Figs. 2-5 of the manuscript and the matching reference file names."""
from .core import Layer

PAPER_CASES = [
    dict(name='Fig2_integer', title='Fig. 2  Integer-order PVVBs', folder='figure1', cases=[
        dict(label='(a) m=3, d=0.2', stem='d0.2m3', phaseStem='phased0.2m3', layers=[Layer(0.2, 3)]),
        dict(label='(b) m=1, d=0.3', stem='d0.3m1', phaseStem='phased0.3m1', layers=[Layer(0.3, 1)]),
        dict(label='(c) m=2, d=0.5', stem='d0.5m2', phaseStem='phased0.5m2', layers=[Layer(0.5, 2)]),
    ]),
    dict(name='Fig3_fractional', title='Fig. 3  Fractional-order PVVBs (l = 0.5)', folder='figure2', cases=[
        dict(label='(a) m=0.5, d=0.2', stem='d0.2m0.5l0.5', phaseStem='phased0.2m0.5l0.5total', layers=[Layer(0.2, 0.5)]),
        dict(label='(b) m=1.5, d=0.3', stem='d0.3m1.5l0.5', phaseStem='phased0.3m1.5l0.5total', layers=[Layer(0.3, 1.5)]),
        dict(label='(c) m=2.5, d=0.5', stem='d0.5m2.5l0.5', phaseStem='phased0.5m2.5l0.5total', layers=[Layer(0.5, 2.5)]),
    ]),
    dict(name='Fig4_bilayer', title='Fig. 4  Bi-layer hybrid MPVVBs', folder='figure3 double', cases=[
        dict(label='(a) outer 0.5 / inner 2', stem='d10.3d20.5m1_0.5m2_2_', phaseStem='phased10.3d20.5m1_0.5m2_2_total',
             layers=[Layer(0.3, 0.5), Layer(0.5, 2)]),
        dict(label='(b) outer 1.5 / inner 3', stem='d10.3d20.5m1_1.5m2_3_', phaseStem='phased10.3d20.5m1_1.5m2_3_total',
             layers=[Layer(0.3, 1.5), Layer(0.5, 3)]),
        dict(label='(c) outer 1 / inner 0.5', stem='d10.5d20.3m1_0.5m2_1_', phaseStem='phased10.5d20.3m1_0.5m2_1_total',
             layers=[Layer(0.5, 0.5), Layer(0.3, 1)]),
        dict(label='(d) outer 3 / inner 1.5', stem='d10.5d20.3m1_1.5m2_3_', phaseStem='phased10.5d20.3m1_1.5m2_3_total',
             layers=[Layer(0.5, 1.5), Layer(0.3, 3)]),
    ]),
    dict(name='Fig5_trilayer', title='Fig. 5  Tri-layer hybrid MPVVBs', folder='figure4 3pov', cases=[
        dict(label='(a) outer 0.5 / middle 1 / inner 1.5', stem='d1_0.3d2_0.45d3_1_', phaseStem='phased1_0.3d2_0.45d3_1_total',
             layers=[Layer(0.3, 0.5), Layer(0.45, 1), Layer(1, 1.5)]),
        dict(label='(b) outer 2.5 / middle 2 / inner 1.5', stem='newd1_0.3d2_0.45d3_1_', phaseStem='phasenewd1_0.3d2_0.45d3_1_total',
             layers=[Layer(0.3, 2.5), Layer(0.45, 2), Layer(1, 1.5)]),
    ]),
]
