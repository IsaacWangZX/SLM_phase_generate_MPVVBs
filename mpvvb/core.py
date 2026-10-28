"""Core model of multipolar perfect vector vortex beams (MPVVBs).

Layer k contributes the SLM term
    f_k = cos((M - m_k)*phi - beta_k) * exp(i*l_k*phi) * exp(-i*2*pi*rho/d_k)
and the SLM phase is
    Phi = arg( sum_k w_k * exp(i*arg f_k) ).
After an M-order vector vortex polarizer the x-polarized beam becomes
E*[cos(M*phi), sin(M*phi)]; the beat with cos((M-m)*phi) yields an m-order
vector vortex beam. A lens Fourier transform turns each axicon term into a
ring whose radius scales as 1/d.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np

DEFAULT_WEIGHTS = (1.0, -0.8, 0.6)


@dataclass
class Layer:
    """One ring of the beam.

    d       : normalized axicon period (ring radius ~ 1/d; larger d -> smaller ring)
    m       : polarization order (2m petals behind an analyzer)
    l       : scalar vortex charge; None -> 0.5 for half-integer m, else 0
    betaDeg : polarization offset beta in degrees
    """
    d: float
    m: float
    l: Optional[float] = None
    betaDeg: float = 0.0

    def __post_init__(self):
        if self.d <= 0:
            raise ValueError('d must be positive, got %r' % self.d)
        if self.l is None:
            self.l = 0.5 if self.m % 1 != 0 else 0.0


LayerLike = Union[Layer, Tuple[float, float], Sequence[float], dict]


def as_layers(layers: Sequence[LayerLike]) -> List[Layer]:
    """Accept Layer objects, (d, m[, l[, betaDeg]]) tuples or dicts."""
    out = []
    for L in layers:
        if isinstance(L, Layer):
            out.append(L)
        elif isinstance(L, dict):
            out.append(Layer(**L))
        else:
            out.append(Layer(*L))
    if not out:
        raise ValueError('at least one layer is required')
    return out


def resolve_weights(n: int, weights=None) -> np.ndarray:
    """Layer weights ordered from the outer ring (smallest d) to the inner ring."""
    if weights is None:
        if n > len(DEFAULT_WEIGHTS):
            raise ValueError('default weights cover %d layers; pass weights for %d layers'
                             % (len(DEFAULT_WEIGHTS), n))
        weights = DEFAULT_WEIGHTS[:n]
    w = np.asarray(weights, dtype=complex)
    if w.size < n:
        raise ValueError('need %d weights, got %d' % (n, w.size))
    return w[:n]


def sort_layers(layers: Sequence[LayerLike]) -> List[Layer]:
    return sorted(as_layers(layers), key=lambda L: L.d)


def layer_terms(layers: List[Layer], M: float, rho: np.ndarray, phi: np.ndarray):
    """Yield the complex SLM term f_k of every (already sorted) layer."""
    for L in layers:
        yield (np.cos((M - L.m) * phi - np.deg2rad(L.betaDeg))
               * np.exp(1j * (L.l * phi - 2 * np.pi * rho / L.d)))


def pupil_grid(height: int, width: int, R0: float, center=None):
    """rho/phi grid. Image row 0 is the top (+y); center defaults to the array center."""
    if center is None:
        cy, cx = (height - 1) / 2, (width - 1) / 2
    else:
        cy, cx = center
    x = np.arange(width) - cx
    y = -(np.arange(height) - cy)
    X, Y = np.meshgrid(x, y)
    return np.hypot(X, Y) / R0, np.arctan2(Y, X), x, y


def slm_phase(layers: Sequence[LayerLike], M: float = 30, shape: Tuple[int, int] = (1000, 1000),
              R0: float = 500, weights=None, center=None) -> np.ndarray:
    """SLM phase map in radians [0, 2*pi).

    layers  : list of Layer or (d, m[, l[, betaDeg]])
    M       : order of the vector vortex polarizer
    shape   : (height, width) in SLM pixels, e.g. (1080, 1920)
    R0      : SLM pixels per unit normalized radius rho (axicon period = d*R0 pixels)
    weights : layer weights, outer -> inner; default (1, -0.8, 0.6)
    center  : (row, col) of the beam axis; default array center
    """
    Ls = sort_layers(layers)
    w = resolve_weights(len(Ls), weights)
    rho, phi, _, _ = pupil_grid(shape[0], shape[1], R0, center)
    U = np.zeros(rho.shape, complex)
    for wk, f in zip(w, layer_terms(Ls, M, rho, phi)):
        U += wk * np.exp(1j * np.angle(f))
    return np.mod(np.angle(U), 2 * np.pi)


@dataclass
class SimOptions:
    """Parameters of the focal-plane simulation (calibrated against the original results)."""
    M: float = 30
    R0: float = 500
    rhoMax: float = 2.5
    w0: float = 1.7
    weights: Optional[Sequence[complex]] = None
    fieldMode: str = 'ideal'            # 'ideal' complex field or 'slm' phase-only field
    nOut: int = 500
    df: float = 1 / 19800               # ring radius ~ 1/(df*R0*d) output pixels
    circularOutput: bool = True
    analyzerDeg: Sequence[float] = field(default_factory=lambda: [0, 45, 90])
    hwpDeg: Optional[float] = None
    phaseCrop: int = 1000
    quiverN: int = 20


def simulate(layers: Sequence[LayerLike], opts: Optional[SimOptions] = None, **kw) -> dict:
    """Simulate SLM -> M-order VVP -> lens -> (HWP) -> analyzer.

    Keyword arguments override fields of SimOptions, e.g. simulate(layers, M=20, fieldMode='slm').
    Returns a dict with phaseSLM, Ex, Ey, Itotal, Ia (nOut x nOut x nAngles), analyzerDeg, quiver.
    """
    o = opts or SimOptions()
    if kw:
        o = SimOptions(**{**o.__dict__, **kw})
    Ls = sort_layers(layers)
    w = resolve_weights(len(Ls), o.weights)

    N = 2 * int(np.ceil(o.rhoMax * o.R0)) + 2
    rho, phi, j, _ = pupil_grid(N, N, o.R0)
    Uphase = np.zeros((N, N), complex)
    Uideal = np.zeros((N, N), complex)
    for wk, f in zip(w, layer_terms(Ls, o.M, rho, phi)):
        Uphase += wk * np.exp(1j * np.angle(f))
        Uideal += wk * f
    phaseFull = np.mod(np.angle(Uphase), 2 * np.pi)
    del Uphase

    if o.fieldMode == 'ideal':
        E = Uideal
    elif o.fieldMode == 'slm':
        E = np.exp(1j * phaseFull)
    else:
        raise ValueError("fieldMode must be 'ideal' or 'slm'")
    E = (rho <= o.rhoMax) * np.exp(-(rho / o.w0) ** 2) * E

    u = (np.arange(o.nOut) - o.nOut / 2) * o.df
    W = np.exp(-2j * np.pi * np.outer(u, j))
    Ex = W @ (E * np.cos(o.M * phi)) @ W.T
    Ey = W @ (E * np.sin(o.M * phi)) @ W.T
    del E, W

    if o.hwpDeg is not None:
        t = np.deg2rad(2 * o.hwpDeg)
        Ex, Ey = np.cos(t) * Ex + np.sin(t) * Ey, np.sin(t) * Ex - np.cos(t) * Ey

    c = np.arange(o.nOut) - o.nOut / 2
    cx, cy = np.meshgrid(c, c)
    mask = np.hypot(cx, cy) <= o.nOut / 2 if o.circularOutput else np.ones(cx.shape, bool)

    It = (abs(Ex) ** 2 + abs(Ey) ** 2) * mask
    It /= It.max()
    Ia = []
    for a in o.analyzerDeg:
        a = np.deg2rad(a)
        I = abs(np.cos(a) * Ex + np.sin(a) * Ey) ** 2 * mask
        Ia.append(I / I.max())

    c0 = (N - o.phaseCrop) // 2
    idx = c0 + np.arange(o.phaseCrop)
    return dict(layers=Ls, options=o, phaseSLM=phaseFull[np.ix_(idx, idx)], Ex=Ex, Ey=Ey,
                Itotal=It, Ia=np.stack(Ia, axis=2), analyzerDeg=list(o.analyzerDeg),
                quiver=polarization_quiver(Ls, w, o.quiverN))


def polarization_quiver(layers: List[Layer], w, n: int = 20) -> dict:
    """Local linear-polarization orientation of the target field on an n x n grid
    (for a single layer this is m*phi + beta)."""
    g = np.linspace(-10, 10, n)
    QX, QY = np.meshgrid(g, g)
    qphi = np.arctan2(QY, QX)
    qrho = np.hypot(QX, QY) / 10
    ex = np.zeros(QX.shape, complex)
    ey = np.zeros(QX.shape, complex)
    for wk, L in zip(w, layers):
        s = wk * np.exp(1j * (L.l * qphi - 2 * np.pi * qrho / L.d))
        a = L.m * qphi + np.deg2rad(L.betaDeg)
        ex += s * np.cos(a)
        ey += s * np.sin(a)
    psi = 0.5 * np.arctan2(2 * np.real(ex * np.conj(ey)), abs(ex) ** 2 - abs(ey) ** 2)
    return dict(X=QX, Y=QY, U=np.cos(psi), V=np.sin(psi))


def ring_radius_px(d: float, R0: float = 500, df: float = 1 / 19800) -> float:
    """Approximate focal-plane ring radius in simulation output pixels."""
    return 1 / (df * R0 * d)
