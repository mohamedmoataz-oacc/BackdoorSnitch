from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QFileDialog, QMessageBox, QTextEdit
)
from PySide6.QtGui import QPixmap, QTextCursor
from PySide6.QtCore import Qt, QTimer

import sys
import onnx
import netron
from backend.bds import BDS
from backend.settings import config
from multiprocessing import Process


class ScanPage(QWidget):
    def __init__(self, backend: BDS, history_page):
        super().__init__()
        self.backend = backend
        self.history_page = history_page

        self.model_path = None
        self.data_dir = None

        self.contents_layout = QVBoxLayout(self)
        self.content = QFrame()
        self.content.setStyleSheet("font-size:25px;")
        
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(20)
        self.upload_width = self.width() * 0.4

        content_margin = (900 - 206 - self.upload_width) // 2
        self.content_layout.setContentsMargins(content_margin, 0,content_margin , 0)
        
        self.upload_box = QFrame()
        self.progress_bar = QLabel()

        self.step1()
        self.contents_layout.addWidget(self.content)

    def step1(self):
        self.step = QLabel("Step1: Upload Network")
        self.step.setStyleSheet("font-size:25px; padding-top:90px;")

        self.content_layout.addWidget(self.step, alignment=Qt.AlignCenter)

        prog = QPixmap("./gui/assets/progress.png")
        self.progress_bar.setPixmap(prog)
        self.progress_bar.setScaledContents(True)
        self.progress_bar.setFixedSize(320, 22)

        self.content_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # upload box 
        self.create_input("ONNX file")

        # Visualize button (initially hidden)
        self.visualize_button = QPushButton("Visualize Model")
        self.visualize_button.setFixedHeight(50)
        self.visualize_button.setStyleSheet("""
            QPushButton {
                background-color: #2E2E2E;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)
        self.visualize_button.setVisible(False)
        self.visualize_button.clicked.connect(self.visualize_model)
        self.content_layout.addWidget(self.visualize_button, alignment=Qt.AlignCenter)
    
    def visualize_model(self):
        netron.start(self.model_path)

    def step2(self):
        self.step.setParent(None)
        self.progress_bar.setParent(None)
        self.continue_button.setParent(None)
        self.upload_box.setParent(None)

        self.step = QLabel("Step2: Upload data sample\nfor each output class")
        self.step.setStyleSheet("font-size:25px; padding-top:90px;")

        self.content_layout.addWidget(self.step, alignment=Qt.AlignCenter)

        self.progress_bar = QLabel()
        prog = QPixmap("./gui/assets/comp1.png")
        self.progress_bar.setPixmap(prog)
        self.progress_bar.setScaledContents(True)
        self.progress_bar.setFixedSize(330, 26)

        self.content_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # upload box 
        self.create_input('data directory')

    def step3(self):
        # Clear previous widgets
        self.step.setParent(None)
        self.progress_bar.setParent(None)
        self.continue_button.setParent(None)
        self.upload_box.setParent(None)

        self.analyze_model()

        # Step label
        self.step = QLabel("Step3: Network Analysis")
        self.step.setStyleSheet("font-size:25px; padding-top:90px;")
        self.content_layout.addWidget(self.step, alignment=Qt.AlignCenter)

        self.progress_bar = QLabel()
        prog = QPixmap("./gui/assets/comp2.png")
        self.progress_bar.setPixmap(prog)
        self.progress_bar.setScaledContents(True)
        self.progress_bar.setFixedSize(330, 26)

        self.content_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # Circular progress bar
        self.logging_box = QTextEdit()
        self.logging_box.setFixedSize(1000, 500)
        # self.logging_box.setLineWrapMode(QTextEdit.NoWrap)
        # Create a layout to add margins
        progress_layout = QVBoxLayout()
        progress_layout.addStretch(0.3)  # Top margin
        progress_layout.addWidget(self.logging_box, alignment=Qt.AlignLeft)
        progress_layout.addStretch(0.3)  # Bottom margin
        self.content_layout.addLayout(progress_layout)

        # Report button (initially hidden)
        self.download_button = QPushButton("Download Report")
        self.download_button.setFixedHeight(50)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #2E2E2E;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)
        self.download_button.setVisible(False)
        self.download_button.clicked.connect(self.download_report)
        self.content_layout.addWidget(self.download_button, alignment=Qt.AlignCenter)

        # Progress logic
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)
    
    def analyze_model(self):
        # Send model and data_dir to backend
        self.backend.add_model(self.model_path)
        self.backend_process = Process(
            target=self.backend.analyze,
            kwargs={
                "model_path": self.model_path,
                "free_eagle_params": {"optimizer_epochs": 10},
                "strip_params": {"clean_images_dir": self.data_dir}
            }
        )
        self.backend_process.start()
    
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

    def update_progress(self):
        if not self.backend_process.is_alive():
            config.load()
            self.download_button.setVisible(True)
            self.history_page.show_history(config.get_model(self.model_path))
            self.timer.stop()
        else:
            while True:
                try:
                    # Retrieve any available log record (non-blocking)
                    record = self.backend.log_queue.get_nowait()
                except Exception:
                    # If no more messages are available, break out of the loop
                    break

                # Append the log message to the text widget
                print(record.getMessage())
                self.logging_box.append(record.getMessage())
                self.logging_box.moveCursor(QTextCursor.End)

    def resizeEvent(self, event):
        self.upload_width = self.width() * 0.55
        if self.upload_width < 650:
            self.upload_box.setFixedSize(self.upload_width, 440)
            content_margin = (self.width() - 206 - self.upload_width) // 2
            self.progress_bar.setFixedSize(320, 22)
        else:
            self.upload_box.setFixedSize(650, 440)
            content_margin = (self.width() - 206 - 650) // 2
            self.progress_bar.setFixedSize(380, 28)

        self.content_layout.setContentsMargins(content_margin, 0, 0 , 0)

        super().resizeEvent(event)

    def create_button(self, button_name):
        button = QPushButton(button_name)
        button.setStyleSheet("font-size:15px; font-family: sans; border-radius:10px;")
        button.setFixedSize(200, 40)
        button.setCursor(Qt.PointingHandCursor)

        return button
    
    def upload_onnx_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select ONNX Model", "", "ONNX Files (*.onnx)")

        if not file_path:
            return  # No file selected
        try:
            onnx_model = onnx.load(file_path)
            onnx.checker.check_model(onnx_model)  # Validate model

            self.contents_layout.addWidget(self.continue_button, alignment=Qt.AlignRight)
            self.model_path = file_path
            self.visualize_button.setVisible(True)
        except Exception as e:
            self.continue_button.setParent(None)
            QMessageBox.critical(self, "Error", f"Invalid ONNX file!\n{str(e)}")

    def choose_data_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select directory containing sample data", "")
        
        if not dir_path:
            return  # No file selected
        
        self.contents_layout.addWidget(self.continue_button, alignment=Qt.AlignRight)
        self.data_dir = dir_path

    def create_input(self, type: str):
        # Clear existing widgets from the upload box before reusing it
        if self.upload_box.layout() is not None:
            while self.upload_box.layout().count():
                item = self.upload_box.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Reset upload_box style
        self.upload_box.setStyleSheet(
            "background-color: #333333; border-radius:15px; color: #FBFBFB; margin-top:30px;"
        )

        # Reuse existing layout instead of creating a new one
        upload_layout = self.upload_box.layout()
        if upload_layout is None:
            upload_layout = QVBoxLayout(self.upload_box)
            upload_layout.setAlignment(Qt.AlignTop)
            upload_layout.setContentsMargins(0, 0, 0, 0)
            upload_layout.setSpacing(20)
            self.upload_box.setLayout(upload_layout)

        self.box_label = QLabel(f"Drag {type} here or Click to upload")
        upload_layout.addWidget(self.box_label)
        self.box_label.setStyleSheet(
            "font-size:22px; border-bottom: 1px solid white;  padding-bottom:15px;"
            "border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;"
        )
        self.box_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.upload_box)

        self.upload_icon = QLabel()
        upload = QPixmap("./gui/assets/upload.png")
        self.upload_icon.setPixmap(upload)
        self.upload_icon.setScaledContents(True)
        self.upload_icon.setFixedSize(125, 170)
        self.upload_icon.setStyleSheet("margin-top:50px;")
        upload_layout.addWidget(self.upload_icon, alignment=Qt.AlignCenter)

        # Create a new upload button every time `create_input()` is called
        self.upload_button = self.create_button("Upload file")
        self.upload_button.setStyleSheet(
            "background-color: #2ADD24; color:#121212; border-radius:15px;"
            "margin-top:20px;font-size:22px;"
        )
        self.upload_button.setFixedSize(170, 70)

        # Ensure there are no duplicate signal connections
        try:
            self.upload_button.clicked.disconnect()
        except TypeError:
            pass  # No previous connection, safe to proceed

        # Assign the correct upload function based on file type
        if type.lower() == "data directory":
            self.upload_button.clicked.connect(self.choose_data_dir)
        else:
            self.upload_button.clicked.connect(self.upload_onnx_file)

        upload_layout.addWidget(self.upload_button, alignment=Qt.AlignCenter)

        # Create a new continue button
        self.continue_button = self.create_button("Continue >")
        self.continue_button.setStyleSheet(
            "background-color: #2ADD24; color:#121212; border-radius:10px;"
            "font-size:22px;margin-bottom:45px; margin-right:30px;"
        )
        self.continue_button.setFixedSize(190, 100)

        # Ensure `continue_button` is properly reconnected
        try:
            self.continue_button.clicked.disconnect()
        except TypeError:
            pass  # No previous connection, safe to proceed

        if type.lower() == "data directory" or "strip" not in config.get_detectors_used():
            self.continue_button.clicked.connect(self.step3)
        else:
            self.continue_button.clicked.connect(self.step2)
    
    def progress(self, value):
        self.progress = value
        self.update()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScanPage()
    window.show()
    sys.exit(app.exec())