import sys
from PyQt5.QtWidgets import QApplication

from styles import DARK_STYLE_SHEET
from app_window import SchrodingerGUI


def main():
    app = QApplication(sys.argv)
    
    # Configure global aesthetic defaults
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE_SHEET)
    
    # Initialize and display application window
    window = SchrodingerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
