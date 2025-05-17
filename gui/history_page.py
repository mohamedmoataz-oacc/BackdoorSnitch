from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt

from gui.scan_entry import ScanEntryWidget


class HistoryPage(QWidget):
    def __init__(self, scan_data, backend):
        super().__init__()
        self.backend = backend

        layout = QVBoxLayout(self)
        title = QLabel("📊 Scan History")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        layout.addWidget(title, alignment=Qt.AlignTop | Qt.AlignHCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(15)

        container.setLayout(self.container_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.show_history(scan_data)
    
    def show_history(self, scan_data):
        for entry in scan_data:
            entry_widget = ScanEntryWidget(self.backend, **entry)
            self.container_layout.addWidget(entry_widget)

