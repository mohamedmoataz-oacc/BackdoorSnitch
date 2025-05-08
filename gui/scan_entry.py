from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt

class ScanEntryWidget(QWidget):
    def __init__(self, date, model_path, result_summary, report_path=None):
        super().__init__()
        self.contents_layout = QVBoxLayout(self)
        layout_frame = QFrame()
        
        layout_frame.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 12px;
            font-size:20px;
        """)
        layout = QVBoxLayout(layout_frame)

        layout.addWidget(QLabel(f"<b>Date:</b> {date}"))
        layout.addWidget(QLabel(f"<b>Model Path:</b> {model_path}"))
        layout.addWidget(QLabel(f"<b>Detection Results:</b> {result_summary}"))

        if report_path:
            download_btn = QPushButton("Download Report")
            download_btn.setCursor(Qt.PointingHandCursor)
            download_btn.clicked.connect(lambda: self.open_report(report_path))
            download_btn.setFixedWidth(210)
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #20a31c;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #1a7817;
                }
            """)
            layout.addWidget(download_btn, alignment=Qt.AlignCenter)

        self.contents_layout.addWidget(layout_frame)

    def open_report(self, path):
        # Placeholder: open PDF, HTML, etc.
        print(f"Opening report: {path}")
