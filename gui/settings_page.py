from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, 
    QFrame, QScrollArea, QSpacerItem, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SettingsPage(QFrame):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Title
        title = QLabel("Detection Methods Configuration")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333333; margin-bottom: 15px;")
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("Select the methods to apply to your model:")
        desc.setStyleSheet("color: #555555; font-size: 15px;")
        desc.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc)
        
        # Add vertical spacer for better top spacing
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Scroll area for methods
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        
        # Methods container
        methods_container = QWidget()
        methods_layout = QVBoxLayout(methods_container)
        methods_layout.setContentsMargins(20, 10, 20, 10)
        methods_layout.setSpacing(25)  # Increased spacing between methods
        
        # Method checkboxes
        self.netcop_check = self._create_method_checkbox(
            "NetCop", 
            "Neural trojan detection during validation"
        )
        self.netcop_check.findChild(QCheckBox).setChecked(
            "netcop" in self.config.settings.get("detection_methods")
        )
        
        self.strip_check = self._create_method_checkbox(
            "STRIP", 
            "Neural trojan detection after deployment"
        )
        self.strip_check.findChild(QCheckBox).setChecked(
            "strip" in self.config.settings.get("detection_methods")
        )
        
        methods_layout.addWidget(self.netcop_check)
        methods_layout.addWidget(self.strip_check)
        
        # Add spacer at bottom to push content up
        methods_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        scroll.setWidget(methods_container)
        main_layout.addWidget(scroll)
        
        # Save button container (for better centering)
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        # Save button
        save_btn = QPushButton("Save Configuration")
        save_btn.setFixedSize(200, 45)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #20a31c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1a7817;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn, alignment=Qt.AlignCenter)
        
        main_layout.addWidget(button_container)
        
        # Set overall styles
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QCheckBox {
                color: #333333;
                spacing: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
            }
            QCheckBox::indicator:checked {
                background-color: #4a6fa5;
                border: 2px solid #3a5a8f;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #cccccc;
                border-radius: 4px;
            }
        """)
    
    def _create_method_checkbox(self, title, description):
        """Create a method selection widget with proper spacing"""
        container = QFrame()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 15)  # Bottom margin for spacing
        layout.setSpacing(8)  # Space between checkbox and description
        
        # Checkbox
        checkbox = QCheckBox(title)
        checkbox.setStyleSheet("font-weight: bold;")
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            color: #666666; 
            font-size: 14px;
            margin-left: 34px;  # Align with checkbox text
            margin-top: -5px;
        """)
        desc_label.setWordWrap(True)
        
        layout.addWidget(checkbox)
        layout.addWidget(desc_label)
        
        return container
    
    def save_settings(self):
        """Collect and save the selected methods"""
        selected_methods = []
        if self.netcop_check.findChild(QCheckBox).isChecked():
            selected_methods.append("netcop")
        if self.strip_check.findChild(QCheckBox).isChecked():
            selected_methods.append("strip")
        
        # Here you would typically save to config file or database
        self.config.settings["detection_methods"] = selected_methods
        self.config.save()
        QMessageBox.information(self, "Saved", f"Configuration saved successfully!")