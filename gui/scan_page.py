from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QFileDialog, QMessageBox, QTextEdit, QHBoxLayout, QSpacerItem, QSizePolicy
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
        self.strip_params = None

        self.contents_layout = QVBoxLayout(self)
        self.content = QFrame()
        self.content.setStyleSheet("font-size:25px;")
        
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(20)
        self.upload_width = self.width() * 0.4

        content_margin = (900 - 206 - self.upload_width) // 2
        self.content_layout.setContentsMargins(content_margin , 0,content_margin , 0)
        
        self.upload_box = QFrame()
        self.progress_bar = QLabel()
        self.logging_box = QTextEdit()
        self.download_button = QPushButton("Download Report")
        self.back_button = QPushButton("< Back")

        self.step1()
        self.contents_layout.addWidget(self.content)

    def step1(self):
        self.strip_params = None
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
        self.visualize_button.setFixedHeight(100)
        self.visualize_button.setStyleSheet("""
            QPushButton {
                background-color: #2E2E2E;
                color: white;
                font-size: 22px;
                border-radius: 12px;
                padding: 0 20px;
                margin-bottom:45px;
            
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)
        self.visualize_button.setVisible(False)
        self.visualize_button.clicked.connect(self.visualize_model)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)


        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        
        self.container_layout.addWidget(self.visualize_button)
        self.container_layout.addItem(spacer)
        self.container_layout.addWidget(self.continue_button)


    
    def visualize_model(self):
        netron.start(self.model_path)

    def step2(self):
        self.step.setParent(None)
        self.progress_bar.setParent(None)
        self.continue_button.setParent(None)
        self.upload_box.setParent(None)
        self.visualize_button.setParent(None)

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

    def step2_strip(self):
        self.step.setParent(None)
        self.progress_bar.setParent(None)
        self.logging_box.setParent(None)
        self.download_button.setParent(None)
        self.back_button.setParent(None)
        self.step.setParent(None)
        self.progress_bar.setParent(None)
        self.continue_button.setParent(None)
        self.upload_box.setParent(None)
        self.visualize_button.setParent(None)

        self.step = QLabel("Step2: Upload test data")
        self.step.setStyleSheet("font-size:25px; padding-top:90px;")

        self.content_layout.addWidget(self.step, alignment=Qt.AlignCenter)

        self.progress_bar = QLabel()
        prog = QPixmap("./gui/assets/comp1.png")
        self.progress_bar.setPixmap(prog)
        self.progress_bar.setScaledContents(True)
        self.progress_bar.setFixedSize(330, 26)

        self.content_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # upload box 
        self.create_input('image or \ndirectory')

    def step3(self):
        content_margin = (self.width() - 206 - self.width()*0.7) // 2
        self.content_layout.setContentsMargins(content_margin, 0, content_margin , 0)
        # Clear previous widgets
        self.step.setParent(None)
        self.progress_bar.setParent(None)
        self.continue_button.setParent(None)
        self.upload_box.setParent(None)
        self.visualize_button.setParent(None)


        self.analyze_model()

        # Step label
        self.step = QLabel("Step3: Network Analysis")
        self.step.setStyleSheet("font-size:25px; padding-top:90px;")
        self.content_layout.addWidget(self.step, alignment=Qt.AlignCenter)

        self.progress_bar = QLabel()
        prog = QPixmap("./gui/assets/comp2.png")
        self.progress_bar.setPixmap(prog)
        self.progress_bar.setScaledContents(True)
        self.progress_bar.setFixedSize(320, 22)

        self.content_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # Circular progress bar
        self.logging_box.setFixedSize(self.width()* 0.8, 420)

        self.logging_box.setReadOnly(False)
        self.logging_box.clear()
        self.logging_box.setReadOnly(True)
        # Create a layout to add margins

        self.content_layout.addWidget(self.logging_box, alignment=Qt.AlignCenter)

        # Report button (initially hidden)
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

        #back button
        self.back_button.setFixedHeight(50)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #575757;
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
        self.back_button.setVisible(False)
        self.back_button.clicked.connect(self.back_scan)
        self.content_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        # Progress logic
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

        
    def back_scan(self):
        self.step.setParent(None)
        self.progress_bar.setParent(None)
        self.logging_box.setParent(None)
        self.download_button.setParent(None)
        self.back_button.setParent(None)
        content_margin = (self.width() - 206 - self.upload_width) // 2
        self.content_layout.setContentsMargins(content_margin+80, 0, content_margin , 0)
        self.step1()

    def analyze_model(self):
        self.set_params = self.window()

        # Send model and data_dir to backend
        self.backend.add_model(self.model_path)

        if self.strip_params:
            kwargs = {
                "model_path": self.model_path,
                "strip_params": self.strip_params,
                "detectors": ["strip"],
                "strip_args": self.data_dir
            }
        else:
            kwargs = {
                "model_path": self.model_path,
                "strip_params": {"clean_images_dir": self.data_dir}
            }
            if self.set_params.parameters:
                kwargs["netcop_params"] = {"optimizer_epochs": self.set_params.parameters[1], "num_IRcs": self.set_params.parameters[0]}
                print(self.set_params.parameters[1], self.set_params.parameters[0])

        self.backend_process = Process(
            target=self.backend.analyze,
            kwargs=kwargs
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
            self.back_button.setVisible(True)
            prog = QPixmap("./gui/assets/comp3.png")
            self.progress_bar.setPixmap(prog)

            self.history_page.show_history(config.settings["models"])
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

        self.logging_box.setFixedWidth(self.width()*0.7)

        if "step3:" in self.step.text().lower() :
            content_margin = (self.width() - 206 - self.width()*0.7) // 2
            self.content_layout.setContentsMargins(content_margin, 0, content_margin , 0)
        else:
            self.content_layout.setContentsMargins(content_margin+80, 0, content_margin , 0)

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

            self.contents_layout.addStretch()
            self.contents_layout.addWidget(self.container)
            self.model_path = file_path
            self.visualize_button.setVisible(True)
        except Exception as e:
            self.container.setParent(None)
            QMessageBox.critical(self, "Error", f"Invalid ONNX file!\n{str(e)}")

    def choose_data_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select directory containing sample data", "")
        
        if not dir_path:
            return  # No file selected
        
        self.contents_layout.addWidget(self.continue_button, alignment=Qt.AlignRight)
        self.data_dir = dir_path

    def choose_image_dir(self):
        images_path, _ = QFileDialog.getOpenFileNames(
            None, "Select Images", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if not images_path:
            return  # Nothing selected

        self.data_dir = images_path
        self.contents_layout.addWidget(self.continue_button, alignment=Qt.AlignRight)

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
        elif type.lower() == "onnx file":
            self.upload_button.clicked.connect(self.upload_onnx_file)
        else:
            self.upload_button.clicked.connect(self.choose_image_dir)


        upload_layout.addWidget(self.upload_button, alignment=Qt.AlignCenter)

        # Create a new continue button
        self.continue_button = self.create_button("Continue >")
        self.continue_button.setStyleSheet(
            "background-color: #2ADD24; color:#121212; border-radius:10px;"
            "font-size:22px;margin-bottom:45px;"
        )
        self.continue_button.setFixedSize(150, 100)

        # Ensure `continue_button` is properly reconnected
        try:
            self.continue_button.clicked.disconnect()
        except TypeError:
            pass  # No previous connection, safe to proceed

        if type.lower() == "data directory" or type.lower() == "image or \ndirectory" or"strip" not in config.get_detectors_used():
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