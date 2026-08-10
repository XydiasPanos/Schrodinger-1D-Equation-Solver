DARK_STYLE_SHEET = """
QMainWindow, QDialog {
    background-color: #121212;
    color: #E0E0E0;
}
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-size: 10pt;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #2C2C3E;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: #181824;
    color: #00AAFF;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    color: #00AAFF;
}
QFrame {
    background-color: #1F1F2E;
    border: 1px solid #2A2A3D;
    border-radius: 6px;
}
QDoubleSpinBox, QSpinBox, QComboBox, QLineEdit {
    background-color: #252538;
    color: #FFFFFF;
    border: 1px solid #3B3B54;
    border-radius: 4px;
    padding: 4px;
    selection-background-color: #007ACC;
}
QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
    border: 1px solid #00AAFF;
}
QComboBox QAbstractItemView {
    background-color: #1F1F2E;
    color: #FFFFFF;
    selection-background-color: #007ACC;
}
QPushButton {
    background-color: #2A2A3D;
    color: #FFFFFF;
    border: 1px solid #3B3B54;
    border-radius: 5px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3A3A52;
    border: 1px solid #00AAFF;
}
QPushButton:pressed {
    background-color: #007ACC;
}
QRadioButton, QCheckBox {
    color: #E0E0E0;
    background-color: transparent;
}
QRadioButton::indicator, QCheckBox::indicator {
    width: 13px;
    height: 13px;
}
QTextBrowser {
    background-color: #14141F;
    color: #E0E0E0;
    border: 1px solid #2A2A3D;
    border-radius: 6px;
}
QScrollArea {
    background-color: #121212;
    border: none;
}
QScrollBar:vertical {
    background: #181824;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #3A3A52;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #00AAFF;
}
"""
