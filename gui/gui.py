from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect,
    QHBoxLayout, QFrame, QStackedWidget
)
from PySide6.QtGui import QPixmap, QIcon, QGuiApplication, QColor
from PySide6.QtCore import Qt, QTimer

import sys
from gui.scan_page import ScanPage
from gui.settings_page import SettingsPage
from gui.history_page import HistoryPage
from backend.settings import config
from backend.bds import BDS


class MainWindow(QWidget):
    def __init__(self, backend: BDS):
        super().__init__()
        self.backend = backend

        self.parameters = []

        self.setWindowTitle("Backdoor Snitch")
        pixmap = QPixmap('./gui/assets/logo_light.png')
        self.setWindowIcon(QIcon(pixmap))

        # Get the screen geometry
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = 800
        window_height = screen_geometry.height() - 55

        # To center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.setGeometry(x, y, window_width, window_height + 25)
        self.setStyleSheet("background-color: white; padding:0")

        # Set some variables
        self.font_size = 20
        self.upload_width = self.width() * 0.55
        self.min_width = 400

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignTop)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(206)
        self.sidebar.setFixedHeight(self.height())
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 30, 0, 0)
        sidebar_layout.setSpacing(40)
        sidebar_layout.setAlignment(Qt.AlignTop)

        self.sidebar.setStyleSheet("""
            QWidget {
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background-color: #E1E1E1;
                margin-right: 2px; padding: 0px;
                font-size:18px;
            }
        """)

        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setScaledContents(True)
        logo.setFixedSize(150, 170)
        logo.setStyleSheet("""
        padding-top:20px;
        padding-bottom:20px;
        """)
        sidebar_layout.addWidget(logo, alignment=Qt.AlignCenter)

        buttons_container = QFrame()
        buttons_container.setFixedSize(206, 148)
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(3, 0, 0, 0)
        buttons_layout.setSpacing(10)

        # Create pages
        self.stacked_widget = QStackedWidget()
        
        # Scan page
        scan_data = config.settings["models"]
        self.history_page = HistoryPage(scan_data, self.backend)
        self.scan_page = ScanPage(self.backend, self.history_page)
        self.stacked_widget.addWidget(self.scan_page)
        self.stacked_widget.addWidget(self.history_page)
        
        # Settings page
        self.settings_page = SettingsPage(config)
        self.stacked_widget.addWidget(self.settings_page)

        # Create navigation buttons
        self.scan_button = self.create_button("Scan")     
        self.scan_button.clicked.connect(lambda: self.switch_page(0))
        self.mark_button(self.scan_button)
        buttons_layout.addWidget(self.scan_button)

        self.history_button = self.create_button("History")     
        self.history_button.clicked.connect(lambda: self.switch_page(1))
        buttons_layout.addWidget(self.history_button)

        self.settings_button = self.create_button("Settings")     
        self.settings_button.clicked.connect(lambda: self.switch_page(2))
        buttons_layout.addWidget(self.settings_button)

        sidebar_layout.addWidget(buttons_container)
        self.sidebar.setLayout(sidebar_layout)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)

        # Sidebar visibility state
        self.sidebar_visible = True

        # Apply shadow effect AFTER UI is loaded
        QTimer.singleShot(100, self.apply_shadow_fix)

    def switch_page(self, index):
        """Switch between different pages in the stacked widget"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Update button styles
        buttons = [self.scan_button, self.history_button, self.settings_button]
        for i, button in enumerate(buttons):
            if i == index:
                self.mark_button(button)
            else:
                button.setStyleSheet("""
                    background-color: transparent;
                    border-radius: 10px;
                    padding: 5px;
                """)


    def set_params(self, IR, epochs):
        self.parameters = [IR, epochs]

    def create_button(self, button_name):
        button = QPushButton(button_name)
        button.setStyleSheet("""
            font-size:15px; 
            font-family: sans; 
            border-radius:10px; 
            background-color: transparent;
            padding: 5px;
        """)
        button.setFixedSize(200, 40)
        button.setCursor(Qt.PointingHandCursor)
        return button
    
    def mark_button(self, button):
        button.setStyleSheet("""
            background-color: #47CA42;
            border-radius: 10px;
            padding: 5px;
        """)

    def apply_shadow_fix(self):
       # Shadow for the scan button
        button_effect = QGraphicsDropShadowEffect()
        button_effect.setOffset(0, 0)
        button_effect.setBlurRadius(10)
        button_effect.setColor(QColor(0, 0, 0, 160))
        self.scan_button.setGraphicsEffect(button_effect)

        # Shadow for the sidebar
        sidebar_effect = QGraphicsDropShadowEffect()
        sidebar_effect.setOffset(0, 1)  # Moves the shadow slightly to the right
        sidebar_effect.setBlurRadius(10)  # Softer, more diffused shadow
        sidebar_effect.setColor(QColor(0, 0, 0, 200))  # Light black shadow
        self.sidebar.setGraphicsEffect(sidebar_effect)

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())