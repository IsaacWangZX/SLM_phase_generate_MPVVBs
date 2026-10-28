"""Paper-style figures: Phase | Without analyser | analyzer angles | Polarization."""
import numpy as np


def plot_phase(phase, ax=None, colorbar=True):
    import matplotlib.pyplot as plt
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(phase, cmap='jet', vmin=0, vmax=2 * np.pi)
    ax.set_xticks([]); ax.set_yticks([])
    if colorbar:
        cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, ticks=[0, np.pi, 2 * np.pi])
        cb.ax.set_yticklabels(['0', 'π', '2π'])
    return ax


def plot_rows(results, labels=None, title=''):
    """One row per simulate() result."""
    import matplotlib.pyplot as plt
    nR = len(results)
    labels = labels or [''] * nR
    angs = results[0]['analyzerDeg']
    heads = ['Phase', 'Without analyser'] + ['Analyzer %g°' % a for a in angs] + ['Polarization']
    nC = len(heads)
    fig, ax = plt.subplots(nR, nC, figsize=(3 * nC, 3 * nR + 0.6), squeeze=False)
    for r, (S, lab) in enumerate(zip(results, labels)):
        ax[r, 0].imshow(S['phaseSLM'], cmap='jet', vmin=0, vmax=2 * np.pi)
        if lab:
            ax[r, 0].text(0.03, 0.95, lab, transform=ax[r, 0].transAxes, va='top', fontsize=8,
                          bbox=dict(fc='w', ec='none'))
        panels = [S['Itotal']] + [S['Ia'][:, :, a] for a in range(len(angs))]
        for c, I in enumerate(panels):
            ax[r, c + 1].imshow(I, cmap='hot', vmin=0, vmax=1)
        Q = S['quiver']
        ax[r, -1].quiver(Q['X'], Q['Y'], Q['U'], Q['V'], color='r', pivot='mid', scale=30,
                         headwidth=0, headlength=0, headaxislength=0)
        ax[r, -1].set_xlim(-11, 11); ax[r, -1].set_ylim(-11, 11); ax[r, -1].set_aspect('equal')
        for s in ax[r, -1].spines.values():
            s.set_color('r')
    for c in range(nC):
        ax[0, c].set_title(heads[c], fontsize=10)
    for a in ax.ravel():
        a.set_xticks([]); a.set_yticks([])
    if title:
        fig.suptitle(title, fontweight='bold')
    fig.tight_layout()
    return fig
