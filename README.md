# Schrodinger1DSolver

An interactive quantum mechanics simulation engine designed to solve, visualize, and analyze both **Time-Independent** and **Time-Dependent** 1D Schrödinger equations under customizable and composite potential landscapes.

> **Main Goal:** To provide an intuitive platform for exploring quantum state behavior—from bound energy eigenstates in custom potential wells to dynamic wave packet scattering and tunneling across arbitrary barriers.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [User Interface & Navigation](#user-interface--navigation)
- [Preset Examples & Configurations](#preset-examples--configurations)
  - [1. Single Dirac Delta Potential at x = 0](#1-single-dirac-delta-potential-at-x--0)
  - [2. Dirac Delta Train (4 Spikes) + Harmonic Oscillator](#2-dirac-delta-train-4-spikes--harmonic-oscillator)
  - [3. Time-Dependent Wave Packet in a Harmonic Well](#3-time-dependent-wave-packet-in-a-harmonic-well)
- [Physics Background](#physics-background)
- [Exporting Data](#exporting-data)
- [Getting Started](#getting-started)
- [License](#license)

---

## Overview

`Schrodinger1DSolver` bridges the gap between theoretical quantum mechanics and visual intuition. By allowing users to freely combine potentials or input custom mathematical prompts, the solver computes exact/numerical eigenstates or propagates time-dependent wave packets in real time.

---

## Key Features

* **Dual Solving Modes:** Switch easily between stationary state (Time-Independent) and dynamic evolution (Time-Dependent) solvers.
* **Rich Simulation Controls:** Fine-tune physical constants including mass ($m$), spatial bounds ($[x_{\min}, x_{\max}]$), and grid resolution/number of visible eigenstates.
* **Composite Potential Builder:**
  * Choose from standard built-in potentials (Harmonic Oscillator, Finite Well, Dirac Delta, etc.).
  * Enter **custom mathematical expressions/prompts** for arbitrary functions $V(x)$.
  * **Stack and combine** multiple potential layers simultaneously.
* **Time-Dependent Controls:**
  * Configure wave packet parameters: initial momentum ($p_0$) and spatial variance ($\sigma^2$).
  * Real-time **Run / Stop** simulation controls to observe dynamic evolution.
* **Comprehensive Analytics & Exporting:** Measure discrete eigenenergies directly from the right-hand inspection panel and export spatial/momentum probability distributions.

---

## User Interface & Navigation

The software features a dual-mode interface accessible from the main navigation panel:

| Mode | Menu Icon | Description |
| :--- | :---: | :--- |
| **Time-Independent (TISE)** | ![TISE Icon](docs/icons/tise_icon.png) | Solves for stationary eigenstates $\psi_n(x)$ and energy levels $E_n$. |
| **Time-Dependent (TDSE)** | ![TDSE Icon](docs/icons/tdse_icon.png) | Simulates real-time wave packet evolution $\Psi(x,t)$ through potential barriers. |

---

## Preset Examples & Configurations

### 1. Single Dirac Delta Potential at $x = 0$

Explore attractive or repulsive bound states created by an infinitely narrow potential well located at the origin.

![Single Dirac Delta at x=0](docs/examples/dirac_single.png)

* **Potential Configuration:** $V(x) = -\alpha \cdot \delta(x)$
* **Domain Limits:** $x \in [-5, 5]$
* **Key Observations:** Demonstrates localized bound states and decay characteristics as $|x| \to \infty$.

---

### 2. Dirac Delta Train (4 Spikes) + Harmonic Oscillator

Combine continuous parabolic confinement with a discrete lattice-like potential to inspect symmetry breaking and band-like state splitting.

![4 Diracs + Harmonic Oscillator](docs/examples/dirac_train_oscillator.png)

* **Potential Configuration:** 
  $$V(x) = \frac{1}{2} m \omega^2 x^2 + \sum_{i=1}^{4} v_i \cdot \delta(x - x_i)$$
* **Layering Steps:**
  1. Add built-in **Harmonic Oscillator** ($k = 1.0$).
  2. Add **4x Dirac Delta** prompts at $x = \{-3, -1, 1, 3\}$.
* **Key Observations:** The uniform spacing creates localized perturbational drops in the parabolic eigenstate profiles, showing how periodic perturbations alter global harmonic states.

---

### 3. Time-Dependent Wave Packet in a Harmonic Well

Simulate dynamic oscillations of a Gaussian wave packet placed off-center inside a harmonic potential well.

![Wave Packet Dynamic Simulation](docs/examples/wave_packet_tdse.png)

* **Potential Configuration:** $V(x) = \frac{1}{2} k x^2$
* **Packet Parameters:**
  * **Initial Position ($x_0$):** $-2.0$
  * **Initial Momentum ($p_0$):** $+1.5$
  * **Spatial Variance ($\sigma^2$):** $0.5$
* **Control:** Click **Run** to observe coherent state oscillation and dispersion/refocusing over time.

---

## Physics Background

### Time-Independent Schrödinger Equation (TISE)

$$-\frac{\hbar^2}{2m} \frac{d^2 \psi_n(x)}{dx^2} + V(x)\psi_n(x) = E_n \psi_n(x)$$

The app discretizes the space on the chosen domain $[x_{\min}, x_{\max}]$ to solve the Hamiltonian matrix eigenvalue problem, outputting the individual eigenstates $\psi_n(x)$ along with their corresponding eigenenergies $E_n$ displayed on the right-side control panel.

### Time-Dependent Schrödinger Equation (TDSE)

$$i\hbar \frac{\partial \Psi(x,t)}{\partial t} = \left( -\frac{\hbar^2}{2m}\frac{\partial^2}{\partial x^2} + V(x) \right) \Psi(x,t)$$

Initial Gaussian wave packets are constructed as:

$$\Psi(x, 0) = \left( \frac{1}{2\pi \sigma^2} \right)^{1/4} \exp\left( -\frac{(x - x_0)^2}{4\sigma^2} \right) \exp\left( \frac{i p_0 x}{\hbar} \right)$$

---

## Exporting Data

Throughout both TISE and TDSE modes, you can export high-resolution data and plots directly from the toolbar:

* **Position Probability Density ($|\Psi(x)|^2$):** Export spatial distributions to inspect position probabilities.
* **Momentum Probability Density ($|\Phi(p)|^2$):** Export Fourier-transformed momentum representations to evaluate state momentum dispersion.
* **Raw Numerical Data:** Export `.csv` files containing spatial grid coordinates, potential values, wavefunctions, and eigenenergy tables.

---
## Getting Started (Installation & Running)

You can run `Schrodinger1DSolver` either by launching the standalone executable (no installation required) or by running it directly from the Python source code.

### Option 1: Run via Standalone Executable (.exe)

This is the easiest method if you are on Windows and don't want to install Python.

1. Go to the starting page of this repository.
2. Download the latest `Schrodinger1DSolver.exe` file.
3. Double-click the downloaded `.exe` file to launch the application. *(Note: Windows Defender might show a "SmartScreen" warning since the executable isn't digitally signed by a major publisher. Click "More info" and then "Run anyway").*

### Option 2: Run via Python (From Source)

If you prefer to run the code yourself, modify it, or are on macOS/Linux:

1. **Prerequisites:** Ensure you have Python 3.9 or higher installed.
2. **Clone the repository:**
   ```bash
   git clone https://github.com/XydiasPanos/Schrodinger-1D-Equation-Solver.git Schrodinger1DSolver
   cd Schrodinger1DSolver
   python main.py
   ```
---

## License

Distributed under the MIT License. See `LICENSE` for more information.
