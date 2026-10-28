"""mpvvb: SLM phase maps and simulation of multipolar perfect vector vortex beams."""
from .core import (DEFAULT_WEIGHTS, Layer, SimOptions, as_layers, polarization_quiver,
                   ring_radius_px, simulate, slm_phase)
from .fileio import load_fig_image, load_fig_quiver, phase_to_gray, save_phase, save_simulation

__version__ = '1.0.0'

__all__ = ['DEFAULT_WEIGHTS', 'Layer', 'SimOptions', 'as_layers', 'polarization_quiver',
           'ring_radius_px', 'simulate', 'slm_phase', 'load_fig_image', 'load_fig_quiver',
           'phase_to_gray', 'save_phase', 'save_simulation']
