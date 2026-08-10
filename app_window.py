import numpy as np
from scipy.integrate import trapezoid 

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, 
    QSpinBox, QDoubleSpinBox, QRadioButton, QPushButton, QSplitter, 
    QLabel, QTextBrowser, QGroupBox, QButtonGroup, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from solvers import solve_tise, split_operator_step
from widgets import PotentialItemWidget, ExtraGraphsDialog


class SchrodingerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("1D Quantum Schrödinger Equation Solver & Real-Time Simulator")
        self.setWindowIcon(QIcon("app_icon.ico"))
        self.resize(1420, 840)
        
        self.x = None
        self.V = None
        self.energies = None
        self.wavefunctions = None
        self.potential_widgets = []

        self.t_curr = 0.0
        self.psi_t = None
        self.is_running = False

        self.timer = QTimer(self)
        self.timer.setInterval(25)
        self.timer.timeout.connect(self.advance_time_simulation)
        
        self.init_ui()
        self.add_potential_component()
        self.calculate_and_update()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        top_vlayout = QVBoxLayout(main_widget)

        top_bar = QGroupBox("Solver Operating Mode & Extra Actions")
        top_bar_layout = QHBoxLayout(top_bar)

        self.mode_group = QButtonGroup(self)
        self.radio_tid = QRadioButton("Time Independent Solution")
        self.radio_td = QRadioButton("Time Dependent Solution")
        self.radio_tid.setChecked(True)
        
        self.mode_group.addButton(self.radio_tid)
        self.mode_group.addButton(self.radio_td)

        top_bar_layout.addWidget(self.radio_tid)
        top_bar_layout.addWidget(self.radio_td)
        top_bar_layout.addStretch()

        self.btn_solve = QPushButton("Solve TISE/TDSE/Re-Init")
        self.btn_solve.setStyleSheet("font-weight: bold; background-color: #007ACC; color: white; padding: 5px 15px;")
        self.btn_solve.clicked.connect(self.calculate_and_update)
        top_bar_layout.addWidget(self.btn_solve)

        self.btn_extra = QPushButton("Export Density Graphs (|ψ|² & ψ(p))")
        self.btn_extra.setStyleSheet("padding: 5px 12px; background-color: #2A2A3D; color: white;")
        self.btn_extra.clicked.connect(self.open_extra_window)
        top_bar_layout.addWidget(self.btn_extra)

        top_vlayout.addWidget(top_bar)
        
        self.radio_tid.toggled.connect(self.on_mode_switched)
        self.radio_td.toggled.connect(self.on_mode_switched)

        self.splitter = QSplitter(Qt.Horizontal)

        # SPACE 1: Left Control Panel
        left_panel = QGroupBox("Simulation Setup & Potentials")
        left_layout = QVBoxLayout(left_panel)

        sys_box = QGroupBox("System Parameters & Axis Limits")
        sys_layout = QFormLayout(sys_box)

        self.spin_mass = QDoubleSpinBox()
        self.spin_mass.setRange(-1e9, 1e9)
        self.spin_mass.setValue(1.0)
        self.spin_mass.setSingleStep(0.1)
        self.spin_mass.valueChanged.connect(self.calculate_and_update)
        sys_layout.addRow("Particle Mass (m):", self.spin_mass)

        self.spin_xmin = QDoubleSpinBox()
        self.spin_xmin.setRange(-1e9, 1e9)
        self.spin_xmin.setValue(-10.0)
        self.spin_xmin.setSingleStep(0.5)
        self.spin_xmin.valueChanged.connect(self.calculate_and_update)
        sys_layout.addRow("xmin:", self.spin_xmin)

        self.spin_xmax = QDoubleSpinBox()
        self.spin_xmax.setRange(-1e9, 1e9)
        self.spin_xmax.setValue(10.0)
        self.spin_xmax.setSingleStep(0.5)
        self.spin_xmax.valueChanged.connect(self.calculate_and_update)
        sys_layout.addRow("xmax:", self.spin_xmax)

        self.lbl_n = QLabel("Max States (n):")
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 20)
        self.spin_n.setValue(3)
        self.spin_n.valueChanged.connect(self.calculate_and_update)
        sys_layout.addRow(self.lbl_n, self.spin_n)

        left_layout.addWidget(sys_box)

        self.td_box = QGroupBox("Time Dependent Wave Packet Parameters")
        td_layout = QFormLayout(self.td_box)

        self.spin_packet_x0 = QDoubleSpinBox()
        self.spin_packet_x0.setRange(-1e9, 1e9)
        self.spin_packet_x0.setValue(-4.0)
        self.spin_packet_x0.setSingleStep(0.5)
        self.spin_packet_x0.valueChanged.connect(self.calculate_and_update)
        td_layout.addRow("Packet Center (x₀):", self.spin_packet_x0)

        self.spin_packet_k0 = QDoubleSpinBox()
        self.spin_packet_k0.setRange(-1e9, 1e9)
        self.spin_packet_k0.setValue(4.0)
        self.spin_packet_k0.setSingleStep(0.5)
        self.spin_packet_k0.valueChanged.connect(self.calculate_and_update)
        td_layout.addRow("Initial Momentum (k₀):", self.spin_packet_k0)

        self.spin_packet_sigma = QDoubleSpinBox()
        self.spin_packet_sigma.setRange(-1e9, 1e9)
        self.spin_packet_sigma.setValue(0.8)
        self.spin_packet_sigma.setSingleStep(0.1)
        self.spin_packet_sigma.valueChanged.connect(self.calculate_and_update)
        td_layout.addRow("Packet Spread (σ):", self.spin_packet_sigma)

        self.spin_dt = QDoubleSpinBox()
        self.spin_dt.setRange(0.0001, 10.0)
        self.spin_dt.setValue(0.01)
        self.spin_dt.setSingleStep(0.005)
        self.spin_dt.setDecimals(4)
        self.spin_dt.valueChanged.connect(self.calculate_and_update)
        td_layout.addRow("Time Step (dt):", self.spin_dt)

        self.td_box.setVisible(False)
        left_layout.addWidget(self.td_box)

        pot_header = QHBoxLayout()
        pot_header.addWidget(QLabel("<b>Stackable V(x) Components:</b>"))
        self.btn_add_pot = QPushButton("➕ Add Potential")
        self.btn_add_pot.setStyleSheet("background-color: #5C2D91; color: white; font-weight: bold;")
        self.btn_add_pot.clicked.connect(self.add_potential_component)
        pot_header.addWidget(self.btn_add_pot)
        left_layout.addLayout(pot_header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        
        left_layout.addWidget(self.scroll_area)

        # SPACE 2: Middle Visualizer Panel
        middle_panel = QWidget()
        mid_layout = QVBoxLayout(middle_panel)

        self.sim_control_bar = QWidget()
        sim_bar_layout = QHBoxLayout(self.sim_control_bar)
        sim_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_run_pause = QPushButton("▶ Run Simulation")
        self.btn_run_pause.setStyleSheet("font-weight: bold; background-color: #28A745; color: white; padding: 6px 15px;")
        self.btn_run_pause.clicked.connect(self.toggle_run_pause)
        sim_bar_layout.addWidget(self.btn_run_pause)

        self.btn_reset_t = QPushButton("🔄 Reset t=0")
        self.btn_reset_t.setStyleSheet("padding: 6px 15px;")
        self.btn_reset_t.clicked.connect(self.reset_simulation_time)
        sim_bar_layout.addWidget(self.btn_reset_t)

        self.lbl_time_display = QLabel("<b>Time t = 0.000 a.u.</b>")
        self.lbl_time_display.setStyleSheet("font-size: 11pt; color: #00AAFF; margin-left: 15px;")
        sim_bar_layout.addWidget(self.lbl_time_display)
        sim_bar_layout.addStretch()

        self.sim_control_bar.setVisible(False)
        mid_layout.addWidget(self.sim_control_bar)

        self.fig = Figure(figsize=(6, 5), facecolor='#121212')
        self.canvas = FigureCanvas(self.fig)
        self.nav_bar = NavigationToolbar(self.canvas, self)
        self.nav_bar.setStyleSheet("background-color: #181824; color: white;")

        mid_layout.addWidget(self.nav_bar)
        mid_layout.addWidget(self.canvas)

        # SPACE 3: Right Panel
        right_panel = QGroupBox("Solved Values & Observables")
        right_layout = QVBoxLayout(right_panel)

        self.math_browser = QTextBrowser()
        self.math_browser.setOpenExternalLinks(True)
        right_layout.addWidget(self.math_browser)

        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(middle_panel)
        self.splitter.addWidget(right_panel)

        self.splitter.setSizes([340, 580, 320])
        top_vlayout.addWidget(self.splitter)

    def add_potential_component(self):
        idx = len(self.potential_widgets) + 1
        widget = PotentialItemWidget(self, idx)
        self.potential_widgets.append(widget)
        self.scroll_layout.addWidget(widget)
        self.calculate_and_update()

    def remove_potential_component(self, widget):
        if len(self.potential_widgets) <= 1:
            QMessageBox.information(self, "Minimum Components", "You must keep at least one potential component.")
            return
        
        self.potential_widgets.remove(widget)
        widget.deleteLater()
        
        for i, w in enumerate(self.potential_widgets):
            w.lbl_title.setText(f"<b>Potential Component #{i+1}</b>")
            
        self.calculate_and_update()

    def on_mode_switched(self):
        is_td = self.radio_td.isChecked()
        
        self.td_box.setVisible(is_td)
        self.spin_n.setVisible(not is_td)
        self.lbl_n.setVisible(not is_td)
        
        self.sim_control_bar.setVisible(is_td)

        if not is_td and self.is_running:
            self.toggle_run_pause()

        self.calculate_and_update()

    def toggle_run_pause(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_run_pause.setText("⏸ Pause Simulation")
            self.btn_run_pause.setStyleSheet("font-weight: bold; background-color: #D9534F; color: white; padding: 6px 15px;")
            self.timer.start()
        else:
            self.btn_run_pause.setText("▶ Run Simulation")
            self.btn_run_pause.setStyleSheet("font-weight: bold; background-color: #28A745; color: white; padding: 6px 15px;")
            self.timer.stop()

    def reset_simulation_time(self):
        if self.is_running:
            self.toggle_run_pause()
        self.t_curr = 0.0
        self.lbl_time_display.setText(f"<b>Time t = {self.t_curr:.3f} a.u.</b>")
        self.calculate_and_update()

    def advance_time_simulation(self):
        if not self.radio_td.isChecked() or self.psi_t is None:
            return

        dt = self.spin_dt.value()
        m = self.spin_mass.value()

        for _ in range(2):
            self.psi_t = split_operator_step(self.psi_t, self.V, self.x, dt, hbar=1.0, m=m)
            self.t_curr += dt

        self.lbl_time_display.setText(f"<b>Time t = {self.t_curr:.3f} a.u.</b>")
        self.update_plot()
        self.update_math_panel()

    def calculate_and_update(self):
        m = self.spin_mass.value()
        xmin = self.spin_xmin.value()
        xmax = self.spin_xmax.value()

        if m <= 0:
            QMessageBox.warning(self, "Invalid Parameter", f"Particle Mass (m = {m}) must be strictly positive!")
            return

        if xmin >= xmax:
            QMessageBox.warning(self, "Invalid Parameter", f"xmin ({xmin}) must be strictly smaller than xmax ({xmax})!")
            return

        self.x = np.linspace(xmin, xmax, 1000)
        self.V = np.zeros_like(self.x)
        descriptions = []

        try:
            for widget in self.potential_widgets:
                v_part, desc = widget.evaluate(self.x)
                self.V += v_part
                descriptions.append(desc)
        except Exception as err:
            QMessageBox.warning(self, "Potential Error", f"Error building V(x): {err}")
            return

        self.v_descriptions = descriptions

        if self.radio_td.isChecked():
            x0 = self.spin_packet_x0.value()
            k0 = self.spin_packet_k0.value()
            sigma = self.spin_packet_sigma.value()

            if sigma <= 0:
                QMessageBox.warning(self, "Invalid Parameter", "Packet Spread (σ) must be strictly positive!")
                return

            norm_factor = (1.0 / (np.pi * (sigma ** 2))) ** 0.25
            gaussian_envelope = np.exp(- ((self.x - x0) ** 2) / (2.0 * (sigma ** 2)))
            phase_factor = np.exp(1j * k0 * self.x)
            
            self.psi_t = (norm_factor * gaussian_envelope * phase_factor).astype(complex)
            
            dx = self.x[1] - self.x[0]
            norm = np.sqrt(trapezoid(np.abs(self.psi_t)**2, self.x))
            if norm > 0:
                self.psi_t /= norm

            self.t_curr = 0.0
            self.lbl_time_display.setText(f"<b>Time t = {self.t_curr:.3f} a.u.</b>")

        else:
            n_states = self.spin_n.value()
            try:
                self.energies, self.wavefunctions = solve_tise(self.x, self.V, n_states=n_states, m=m)
            except Exception as e:
                QMessageBox.warning(self, "Solver Error", f"Failed to solve TISE:\n{e}")
                return

        self.update_plot()
        self.update_math_panel()

    def update_plot(self):
        self.fig.clear()
        ax = self.fig.add_subplot(1, 1, 1, facecolor='#181824')

        ax.tick_params(colors='#E0E0E0')
        ax.xaxis.label.set_color('#E0E0E0')
        ax.yaxis.label.set_color('#E0E0E0')
        ax.title.set_color('#00AAFF')
        ax.grid(True, linestyle='--', alpha=0.3, color='#45475A')
        for spine in ax.spines.values():
            spine.set_color('#2C2C3E')

        ax.plot(self.x, self.V, color='#F1C40F', linewidth=2.5, label='Potential V(x)')

        v_range = np.max(self.V) - np.min(self.V)
        if v_range == 0:
            v_range = 1.0
        scale = 0.20 * v_range

        if self.radio_td.isChecked() and self.psi_t is not None:
            prob_density = np.abs(self.psi_t) ** 2
            real_part = np.real(self.psi_t)
            
            ax.fill_between(self.x, 0, scale * prob_density, color='#00AAFF', alpha=0.35, label='Density |Ψ(x,t)|²')
            ax.plot(self.x, scale * prob_density, color='#00AAFF', linewidth=2.0)
            ax.plot(self.x, scale * real_part, color='#FF5555', linestyle='--', alpha=0.7, label='Re[Ψ(x,t)]')

            ax.set_title(f"Time-Dependent Wave Packet Propagation (t = {self.t_curr:.3f} a.u.)", fontsize=11, fontweight='bold')
            ax.set_ylabel("Potential / Wave Packet (Scaled)", fontsize=10)

        else:
            colors = ['#00AAFF', '#FFB86C', '#50FA7B', '#FF5555', '#BD93F9', '#FF79C6', '#8BE9FD']
            for n in range(len(self.energies)):
                E = self.energies[n]
                psi = self.wavefunctions[:, n]
                c = colors[n % len(colors)]
                
                ax.plot(self.x, E + scale * psi, color=c, linewidth=1.8, label=f'ψ_{n}(x) [E_{n}={E:.2f}]')
                ax.axhline(E, color=c, linestyle=':', alpha=0.5)

            ax.set_title("1D Time-Independent Schrödinger Solutions", fontsize=11, fontweight='bold')
            ax.set_ylabel("Energy / Wavefunction (Shifted)", fontsize=10)

        ax.set_xlabel("x (Position)", fontsize=10)
        ax.set_xlim([self.spin_xmin.value(), self.spin_xmax.value()])
        
        min_y = np.min(self.V) - 0.1 * abs(v_range)
        max_y = np.max(self.V) + 0.3 * abs(v_range)
        ax.set_ylim([min_y, max_y])

        ax.legend(loc='upper right', facecolor='#1F1F2E', edgecolor='#2C2C3E', labelcolor='#E0E0E0')

        self.fig.tight_layout()
        self.canvas.draw()

    def update_math_panel(self):
        dx = self.x[1] - self.x[0]
        m = self.spin_mass.value()

        html = f"""
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #E0E0E0; background-color: #14141F; }}
            h3 {{ color: #00AAFF; margin-bottom: 4px; margin-top: 10px; }}
            h4 {{ color: #FFFFFF; margin-top: 12px; margin-bottom: 4px; }}
            .value-table {{ width: 100%; border-collapse: collapse; margin-top: 5px; }}
            .value-table th, .value-table td {{ border: 1px solid #2A2A3D; padding: 6px; text-align: left; }}
            .value-table th {{ background-color: #1F1F2E; color: #00AAFF; }}
            ul {{ margin-left: -20px; }}
            hr {{ border: 0; height: 1px; background: #2A2A3D; margin: 12px 0; }}
        </style>
        """

        if self.radio_td.isChecked() and self.psi_t is not None:
            prob_density = np.abs(self.psi_t) ** 2
            norm = trapezoid(prob_density, self.x)
            
            x_exp = trapezoid(self.x * prob_density, self.x) / (norm if norm > 0 else 1.0)
            
            dpsi_dx = np.gradient(self.psi_t, dx)
            p_exp = np.real(trapezoid(np.conj(self.psi_t) * (-1j * dpsi_dx), self.x))

            html += f"""
            <h3><u>Real-Time TDSE Observables</u></h3>
            <table class="value-table">
                <tr><th>Observable</th><th>Value (a.u.)</th></tr>
                <tr><td><b>Current Time (t)</b></td><td><span style='color:#00AAFF;'><b>{self.t_curr:.4f}</b></span></td></tr>
                <tr><td><b>Probability Norm (&int;|&Psi;|<sup>2</sup>dx)</b></td><td>{norm:.5f}</td></tr>
                <tr><td><b>Position Expectation &langle;x&rangle;</b></td><td><b>{x_exp:.4f}</b></td></tr>
                <tr><td><b>Momentum Expectation &langle;p&rangle;</b></td><td><b>{p_exp:.4f}</b></td></tr>
            </table>

            <hr/>
            <h3><u>Initial Packet Config</u></h3>
            <ul>
                <li><b>Start Center (x<sub>0</sub>)</b> = {self.spin_packet_x0.value():.2f}</li>
                <li><b>Start Momentum (k<sub>0</sub>)</b> = {self.spin_packet_k0.value():.2f}</li>
                <li><b>Packet Spread (&sigma;)</b> = {self.spin_packet_sigma.value():.2f}</li>
                <li><b>Time Step (dt)</b> = {self.spin_dt.value():.4f}</li>
            </ul>
            """
        else:
            html += f"""
            <h3><u>Calculated Energy Eigenvalues</u></h3>
            <p>Values found for <b>n = {len(self.energies)}</b> requested state(s):</p>
            
            <table class="value-table">
                <tr><th>State (n)</th><th>Energy E<sub>n</sub></th><th>Spacings &Delta;E</th></tr>
            """
            for n, E in enumerate(self.energies):
                spacing_str = "-" if n == 0 else f"{E - self.energies[n-1]:.4f}"
                html += f"""
                <tr>
                    <td><b>n = {n}</b></td>
                    <td><span style='color:#FF5555;'><b>{E:.5f}</b></span></td>
                    <td>{spacing_str}</td>
                </tr>
                """
            html += "</table>"

        html += f"""
        <hr/>
        <h3><u>Active System Parameters</u></h3>
        <ul>
            <li><b>Particle Mass (m)</b> = {m:.4f} a.u.</li>
            <li><b>Planck Constant (&hbar;)</b> = 1.0000 a.u.</li>
            <li><b>Domain Limits [xmin, xmax]</b> = [{self.spin_xmin.value():.2f}, {self.spin_xmax.value():.2f}]</li>
            <li><b>Grid Resolution (&Delta;x)</b> = {dx:.5f}</li>
            <li><b>Total Grid Points (N)</b> = {len(self.x)}</li>
        </ul>

        <hr/>
        <h3><u>Active Potential Stack Components</u></h3>
        <ul>
        """
        for i, desc in enumerate(self.v_descriptions):
            html += f"<li><b>Component #{i+1}:</b> {desc}</li>"

        html += "</ul>"
        self.math_browser.setHtml(html)

    def open_extra_window(self):
        if self.x is None:
            return
        
        if self.radio_td.isChecked():
            if self.psi_t is None:
                return
            dialog = ExtraGraphsDialog(self.x, self.psi_t, parent=self)
        else:
            if self.wavefunctions is None:
                return
            dialog = ExtraGraphsDialog(self.x, self.wavefunctions, self.energies, parent=self)
            
        dialog.exec_()
