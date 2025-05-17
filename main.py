from PySide6.QtWidgets import QApplication
from gui.gui import MainWindow
from backend import bds
import sys


if __name__ == "__main__":
    app = QApplication()

    backend = bds.BDS(log=True)
    window = MainWindow(backend)
    window.show()

    sys.exit(app.exec())
