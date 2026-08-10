import numpy as np
from scipy.fft import fft, fftshift, fftfreq

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QComboBox, 
    QDoubleSpinBox, QPushButton, QLabel, QLineEdit, QFrame, QDialog
)
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class PotentialItemWidget(QFrame):
    """Dynamic Row Widget representing a single potential component V_i(x)."""
    def __init__(self, parent_gui, index):
        super().__init__()
        self.parent_gui = parent_gui
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        top_row = QHBoxLayout()
        self.lbl_title = QLabel(f"<b>Potential Component #{index}</b>")
        self.lbl_title.setStyleSheet("color: #00AAFF;")
        
        self.combo_type = QComboBox()
        self.combo_type.addItems([
            "Harmonic Oscillator",
            "Finite Square Well",
            "Potential Step",
            "Linear Ramp",
            "Gaussian Barrier",
            "Dirac Delta Barrier",
            "Double Well",
            "Custom Math Expression"
        ])
        self.combo_type.currentIndexChanged.connect(self.on_type_changed)

        self.btn_delete = QPushButton("✖ Remove")
        self.btn_delete.setStyleSheet("background-color: #D9534F; color: white; font-weight: bold;")
        self.btn_delete.clicked.connect(self.remove_self)

        top_row.addWidget(self.lbl_title)
        top_row.addWidget(self.combo_type, 1)
        top_row.addWidget(self.btn_delete)
        layout.addLayout(top_row)

        form_layout = QFormLayout()

        self.spin_v0 = QDoubleSpinBox()
        self.spin_v0.setRange(-1e9, 1e9)
        self.spin_v0.setValue(1.0)
        self.spin_v0.setSingleStep(0.5)
        self.spin_v0.valueChanged.connect(self.parent_gui.calculate_and_update)
        self.lbl_v0 = QLabel("Strength/Height (V₀ or k):")
        form_layout.addRow(self.lbl_v0, self.spin_v0)

        self.spin_x0 = QDoubleSpinBox()
        self.spin_x0.setRange(-1e9, 1e9)
        self.spin_x0.setValue(0.0)
        self.spin_x0.setSingleStep(0.5)
        self.spin_x0.valueChanged.connect(self.parent_gui.calculate_and_update)
        self.lbl_x0 = QLabel("Center Offset (x₀):")
        form_layout.addRow(self.lbl_x0, self.spin_x0)

        self.spin_a = QDoubleSpinBox()
        self.spin_a.setRange(-1e9, 1e9)
        self.spin_a.setValue(2.0)
        self.spin_a.setSingleStep(0.2)
        self.spin_a.valueChanged.connect(self.parent_gui.calculate_and_update)
        self.lbl_a = QLabel("Width/Scale (a):")
        form_layout.addRow(self.lbl_a, self.spin_a)

        self.txt_custom = QLineEdit("0.5*(x-0)**2 + 2*np.exp(-x**2)")
        self.txt_custom.setPlaceholderText("e.g. 0.5*x**2 + 2*sin(x)")
        self.txt_custom.setVisible(False)
        self.txt_custom.returnPressed.connect(self.parent_gui.calculate_and_update)
        self.lbl_custom = QLabel("Custom V(x):")
        self.lbl_custom.setVisible(False)
        form_layout.addRow(self.lbl_custom, self.txt_custom)

        layout.addLayout(form_layout)

    def on_type_changed(self):
        is_custom = (self.combo_type.currentText() == "Custom Math Expression")
        self.spin_v0.setVisible(not is_custom)
        self.lbl_v0.setVisible(not is_custom)
        self.spin_x0.setVisible(not is_custom)
        self.lbl_x0.setVisible(not is_custom)
        self.spin_a.setVisible(not is_custom)
        self.lbl_a.setVisible(not is_custom)
        
        self.txt_custom.setVisible(is_custom)
        self.lbl_custom.setVisible(is_custom)

        self.parent_gui.calculate_and_update()

    def remove_self(self):
        self.parent_gui.remove_potential_component(self)

    def evaluate(self, x):
        ptype = self.combo_type.currentText()
        V0 = self.spin_v0.value()
        x0 = self.spin_x0.value()
        a = self.spin_a.value()

        if ptype == "Custom Math Expression":
            expr_str = self.txt_custom.text()
            safe_dict = {
                'x': x, 'np': np, 'pi': np.pi, 'e': np.e,
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'exp': np.exp, 'sqrt': np.sqrt, 'abs': np.abs,
                'where': np.where, 'sinh': np.sinh, 'cosh': np.cosh
            }
            try:
                V = eval(expr_str, {"__builtins__": {}}, safe_dict)
                if np.isscalar(V):
                    V = np.full_like(x, V, dtype=float)
                return V, f"Custom({expr_str})"
            except Exception as e:
                raise ValueError(f"Syntax error in Custom Expression '{expr_str}': {e}.")

        shift_x = x - x0

        if ptype == "Harmonic Oscillator":
            V = 0.5 * V0 * (shift_x ** 2)
            desc = f"Harmonic(k={V0:.2f}, x₀={x0:.2f})"

        elif ptype == "Finite Square Well":
            V = np.where(np.abs(shift_x) <= a / 2.0, -V0, 0.0)
            desc = f"SquareWell(V₀={V0:.2f}, x₀={x0:.2f}, a={a:.2f})"

        elif ptype == "Potential Step":
            V = np.where(x >= x0, V0, 0.0)
            desc = f"Step(V₀={V0:.2f}, x₀={x0:.2f})"

        elif ptype == "Linear Ramp":
            V = V0 * shift_x
            desc = f"Ramp(slope={V0:.2f}, x₀={x0:.2f})"

        elif ptype == "Gaussian Barrier":
            if a == 0:
                raise ValueError("Gaussian Barrier width parameter 'a' cannot be 0.")
            V = V0 * np.exp(- (shift_x ** 2) / (2.0 * (a ** 2)))
            desc = f"Gaussian(V₀={V0:.2f}, x₀={x0:.2f}, σ={a:.2f})"

        elif ptype == "Dirac Delta Barrier":
            sigma = 0.05
            V = (V0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * (shift_x / sigma)**2)
            desc = f"DiracDelta(strength={V0:.2f}, x₀={x0:.2f})"

        elif ptype == "Double Well":
            V = V0 * (shift_x ** 4) - a * (shift_x ** 2)
            desc = f"DoubleWell(V₀={V0:.2f}, x₀={x0:.2f}, a={a:.2f})"

        else:
            V = np.zeros_like(x)
            desc = "Zero"

        return V, desc


class ExtraGraphsDialog(QDialog):
    """Secondary pop-up window for position density and momentum-space Fourier spectra."""
    def __init__(self, x, psi, energies=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Extra Analysis: Density |ψ(x)|² & Momentum Space ψ(p)")
        self.resize(900, 650)
        
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(8, 6), facecolor='#121212')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: #181824; color: white;")
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        self.plot_graphs(x, psi, energies)

    def plot_graphs(self, x, psi, energies):
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(2, 1, 1, facecolor='#181824')
        ax2 = self.figure.add_subplot(2, 1, 2, facecolor='#181824')
        
        for ax in (ax1, ax2):
            ax.tick_params(colors='#E0E0E0')
            ax.xaxis.label.set_color('#E0E0E0')
            ax.yaxis.label.set_color('#E0E0E0')
            ax.title.set_color('#00AAFF')
            ax.grid(True, linestyle='--', alpha=0.3, color='#45475A')
            for spine in ax.spines.values():
                spine.set_color('#2C2C3E')

        N = len(x)
        dx = x[1] - x[0]
        hbar = 1.0
        
        k = 2.0 * np.pi * fftfreq(N, d=dx)
        p = fftshift(hbar * k)

        if psi.ndim == 1:
            prob_density = np.abs(psi)**2
            ax1.plot(x, prob_density, color='#00AAFF', linewidth=2, label='Current Wave Packet |Ψ(x,t)|²')
            
            psi_p = fftshift(fft(psi)) * (dx / np.sqrt(2 * np.pi * hbar))
            prob_p = np.abs(psi_p)**2
            ax2.plot(p, prob_p, color='#FF5555', linewidth=2, label='Momentum Density |Φ(p,t)|²')
        else:
            colors = ['#00AAFF', '#FFB86C', '#50FA7B', '#FF5555', '#BD93F9', '#FF79C6', '#8BE9FD']
            for i in range(psi.shape[1]):
                psi_x = psi[:, i]
                prob_density = np.abs(psi_x)**2
                lbl = f'State n={i}' + (f' (E={energies[i]:.2f})' if energies is not None else '')
                c = colors[i % len(colors)]
                ax1.plot(x, prob_density, color=c, label=lbl)
                
                psi_p = fftshift(fft(psi_x)) * (dx / np.sqrt(2 * np.pi * hbar))
                prob_p = np.abs(psi_p)**2
                ax2.plot(p, prob_p, color=c, label=f'State n={i}')

        ax1.set_title("Position Probability Density $|\\psi(x)|^2$")
        ax1.set_xlabel("x (Position)")
        ax1.set_ylabel("$|\\psi(x)|^2$")
        ax1.legend(loc='upper right', facecolor='#1F1F2E', edgecolor='#2C2C3E', labelcolor='#E0E0E0')

        ax2.set_title("Momentum Probability Density $|\\phi(p)|^2$ (Fourier Transform)")
        ax2.set_xlabel("p (Momentum)")
        ax2.set_ylabel("$|\\phi(p)|^2$")
        ax2.set_xlim([-15, 15])
        ax2.legend(loc='upper right', facecolor='#1F1F2E', edgecolor='#2C2C3E', labelcolor='#E0E0E0')

        self.figure.tight_layout()
        self.canvas.draw()
