from PySide6.QtWidgets import QApplication
from gui.gui import MainWindow
import sys

from backend import bds, settings


if __name__ == "__main__":
    app = QApplication()

    backend = bds.BDS()

    window = MainWindow(backend)
    window.show()

    sys.exit(app.exec())