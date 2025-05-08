from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from scan_entry import ScanEntryWidget
from PySide6.QtCore import Qt, QTimer

class HistoryPage(QWidget):
    def __init__(self, scan_data):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("📊 Scan History")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        layout.addWidget(title, alignment=Qt.AlignTop | Qt.AlignHCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(15)

        for entry in scan_data:
            entry_widget = ScanEntryWidget(**entry)
            container_layout.addWidget(entry_widget)

        container.setLayout(container_layout)
        scroll.setWidget(container)

        layout.addWidget(scroll)
