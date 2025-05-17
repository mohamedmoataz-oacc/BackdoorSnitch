from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QFileDialog, QMessageBox
from backend.settings import config
from PySide6.QtCore import Qt
import netron


class ScanEntryWidget(QWidget):
    def __init__(self, backend, path, last_modified, detection_methods_used):
        super().__init__()
        self.backend = backend
        self.model_path = path

        self.contents_layout = QVBoxLayout(self)
        layout_frame = QFrame()
        layout_frame.setMaximumHeight(500)
        layout_frame.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 12px;
            font-size:20px;
        """)
        layout = QVBoxLayout(layout_frame)
    
        layout.addWidget(QLabel(f"<pre><b>Date:</b> {last_modified}</pre>"))
        layout.addWidget(QLabel(f"<pre><b>Model Path:</b> {path}</pre>"))

        label = "<pre><b>Detection Methods used:</b>"
        for method, params in detection_methods_used["params"].items():
            label += f"<br>\t{method}:"
            for k, v in params.items():
                label += f"<br>\t\t{k}: {v}"
        label += "</pre>"

        layout.addWidget(QLabel(label))

        download_btn = QPushButton("Download Report")
        download_btn.setCursor(Qt.PointingHandCursor)
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
        download_btn.clicked.connect(self.download_report)

        # Visualize button (initially hidden)
        visualize_button = QPushButton("Visualize Model")
        visualize_button.setCursor(Qt.PointingHandCursor)
        visualize_button.setFixedWidth(210)
        visualize_button.setStyleSheet("""
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
        visualize_button.clicked.connect(self.visualize_model)

        layout.addWidget(download_btn, alignment=Qt.AlignCenter)
        layout.addWidget(visualize_button, alignment=Qt.AlignCenter)
        self.contents_layout.addWidget(layout_frame)
    
    def visualize_model(self):
        netron.start(self.model_path)

    def download_report(self):
        output_dir = QFileDialog.getExistingDirectory(self, "Select directory to save report", "")
        generated = self.backend.generate_report(config.get_model(self.model_path), output_dir)
        if generated:
            QMessageBox.information(
                self, "Saved",
                f"The report was generated and saved successfully!"
            )
        else:
            QMessageBox.critical(
                self, "Error",
                f"Failed to generate the report!"
            )
