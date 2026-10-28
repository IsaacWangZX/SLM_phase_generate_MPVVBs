"""Saving SLM phase maps / simulation results and reading MATLAB .fig files."""
import os

import numpy as np


def phase_to_gray(phase: np.ndarray, gray2pi: int = 255, bits: int = 8) -> np.ndarray:
    """Map phase [0, 2*pi) linearly to gray levels [0, gray2pi].

    gray2pi : gray level that corresponds to 2*pi on your SLM (from its LUT calibration)
    bits    : 8 -> uint8 image, 16 -> uint16 image
    """
    g = np.round(np.mod(phase, 2 * np.pi) / (2 * np.pi) * gray2pi)
    dtype = np.uint8 if bits == 8 else np.uint16
    if gray2pi > np.iinfo(dtype).max:
        raise ValueError('gray2pi=%d exceeds %d-bit range' % (gray2pi, bits))
    return g.astype(dtype)


def save_phase(phase: np.ndarray, path: str, gray2pi: int = 255, bits: int = 8) -> str:
    """Save an SLM phase map. The format follows the file extension:
    .png/.bmp/.tif -> gray image, .npy -> radians, .csv -> radians, .mat -> radians (variable 'phase')."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.png', '.bmp', '.tif', '.tiff'):
        from PIL import Image
        Image.fromarray(phase_to_gray(phase, gray2pi, bits)).save(path)
    elif ext == '.npy':
        np.save(path, phase)
    elif ext == '.csv':
        np.savetxt(path, phase, delimiter=',', fmt='%.6f')
    elif ext == '.mat':
        import scipy.io as sio
        sio.savemat(path, {'phase': phase})
    else:
        raise ValueError('unsupported extension %r' % ext)
    return path


def save_simulation(S: dict, path: str) -> str:
    """Save a simulate() result as compressed .npz."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    np.savez_compressed(path, phaseSLM=S['phaseSLM'], Ex=S['Ex'], Ey=S['Ey'], Itotal=S['Itotal'],
                        Ia=S['Ia'], analyzerDeg=np.asarray(S['analyzerDeg']))
    return path


def _fig_root(path):
    import scipy.io as sio
    m = sio.loadmat(path)
    return m[[k for k in m if not k.startswith('__')][0]]


def load_fig_image(path: str) -> np.ndarray:
    """CData of the first image object in a MATLAB .fig file (NaN -> 0)."""
    res = []

    def walk(o):
        if isinstance(o, np.ndarray) and o.dtype.names:
            for e in o.flat:
                if e['type'][0] == 'image' and not res:
                    c = e['properties'][0, 0]['CData']
                    res.append(np.asarray(c[0, 0] if c.dtype == object else c, dtype=float))
                walk(e['children'])
    walk(_fig_root(path))
    if not res:
        raise ValueError('no image object in %s' % path)
    return np.nan_to_num(res[0])


def load_fig_quiver(path: str) -> dict:
    """XData, YData, UData, VData of the first quiver object in a MATLAB .fig file."""
    q = {}

    def walk(o):
        if isinstance(o, np.ndarray) and o.dtype.names:
            for e in o.flat:
                if str(e['type'][0]) == 'specgraph.quivergroup' and not q:
                    p = e['properties'][0, 0]
                    for k in ('XData', 'YData', 'UData', 'VData'):
                        v = p[k]
                        q[k] = np.asarray(v[0, 0] if v.dtype == object else v, dtype=float)
                walk(e['children'])
    walk(_fig_root(path))
    return q
