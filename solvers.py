import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
from scipy.fft import fft, ifft, fftfreq
from scipy.integrate import trapezoid


def solve_tise(x, V, n_states=3, hbar=1.0, m=1.0):
    """
    Solves 1D Time-Independent Schrödinger Equation using Finite Differences.
    """
    N = len(x)
    dx = x[1] - x[0]
    
    coeff = - (hbar ** 2) / (2.0 * m * (dx ** 2))
    main_diag = -2.0 * coeff * np.ones(N) + V
    off_diag = coeff * np.ones(N - 1)
    
    H = diags([off_diag, main_diag, off_diag], [-1, 0, 1], format='csr')
    
    v0 = np.ones(N)
    energies, wavefunctions = eigsh(H, k=n_states, which='SA', v0=v0)
    
    idx = np.argsort(energies)
    energies = energies[idx]
    wavefunctions = wavefunctions[:, idx]
    
    for i in range(n_states):
        psi = wavefunctions[:, i]
        norm = np.sqrt(trapezoid(np.abs(psi)**2, x))
        if norm > 0:
            psi /= norm
            
        max_val = np.max(np.abs(psi))
        if max_val > 0:
            first_lobe_idx = np.where(np.abs(psi) > 0.5 * max_val)[0][0]
            if psi[first_lobe_idx] < 0:
                psi *= -1.0

        wavefunctions[:, i] = psi

    return energies, wavefunctions


def split_operator_step(psi, V, x, dt, hbar=1.0, m=1.0):
    """
    Advances wavepacket by dt using Split-Operator Spectral TDSE method.
    """
    N = len(x)
    dx = x[1] - x[0]
    k = 2.0 * np.pi * fftfreq(N, d=dx)
    
    psi = psi * np.exp(-1j * (V / hbar) * (dt / 2.0))
    
    psi_k = fft(psi)
    psi_k = psi_k * np.exp(-1j * (hbar * (k ** 2) / (2.0 * m)) * dt)
    psi = ifft(psi_k)
    
    psi = psi * np.exp(-1j * (V / hbar) * (dt / 2.0))
    
    x_center = 0.5 * (x[-1] + x[0])
    L = x[-1] - x[0]
    sponge = np.exp(- ((x - x_center) / (0.47 * L)) ** 20)
    psi *= sponge

    return psi
