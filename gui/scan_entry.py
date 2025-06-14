from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QFileDialog, QMessageBox
from PySide6.QtGui import QGuiApplication
from backend.settings import config
from PySide6.QtCore import Qt
from backend import bds
import netron


class ScanEntryWidget(QWidget):
    def __init__(self, backend, path, last_modified, detection_methods_used):
        super().__init__()
        self.backend = backend
        self.model_path = path
        self.strip = False
        self.strip_params = []
        
        self.contents_layout = QVBoxLayout(self)
        layout_frame = QFrame()
        layout_frame.setMaximumHeight(500)
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()

        layout_frame.setMaximumWidth(screen_geometry.width()-250)
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
            if method == 'strip':
                self.strip = True
                self.strip_params = params
                layout_frame.setMaximumHeight(700)

                
            label += f"<br>\t{method}:"
            for k, v in params.items():
                label += f"<br>\t\t{k}: {v}"
        label += "</pre>"

        label_w = QLabel(label)


        layout.addWidget(label_w)

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

        # Visualize button (initially hidden)
        scan_button = QPushButton("Scan Model")
        scan_button.setCursor(Qt.PointingHandCursor)
        scan_button.setFixedWidth(210)
        scan_button.setStyleSheet("""
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
        scan_button.clicked.connect(self.scan_model)

        layout.addWidget(download_btn, alignment=Qt.AlignCenter)
        layout.addWidget(visualize_button, alignment=Qt.AlignCenter)
        print()
        if self.strip:
            layout.addWidget(scan_button, alignment=Qt.AlignCenter)

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

    def scan_model(self):
        self.scan = self.window()
        self.scan.switch_page(index= 0)
        self.scan.mark_button(self.scan.scan_button)
        self.scan.show()
        print(self.strip_params["mean_entropy"], self.strip_params["std_entropy"], self.strip_params["threshold"])
        self.scan.scan_page.model_path = self.model_path
        self.scan.scan_page.strip_params = {"mean_entropy": self.strip_params["mean_entropy"],
                                            "std_entropy": self.strip_params["std_entropy"], 
                                            "threshold": self.strip_params["threshold"]}
        self.scan.scan_page.step2_strip()



