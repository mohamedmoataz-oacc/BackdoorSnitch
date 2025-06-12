from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, 
    QFrame, QScrollArea, QSpacerItem, QSizePolicy, QMessageBox, QHBoxLayout, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from gui.parameter_controls import ParameterControls


class SettingsPage(QFrame):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setup_ui()
        self.parameters = None  # Placeholder for the widget
        
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
        self.set_parms = QPushButton("Set Parameters")

        self.netcop_check.findChild(QCheckBox).setChecked(
            "netcop" in self.config.settings.get("detection_methods")
        )

        self.netcop_check.findChild(QCheckBox).stateChanged.connect(self.toggle_parameters)

        
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
                image: url(./gui/assets/check.png);
                border: 2px solid #00BA00;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                image: none;
                border: 2px solid #cccccc;
                border-radius: 4px;
            }
        """)
    
    def _create_method_checkbox(self, title, description):
        """Create a method selection widget with proper spacing"""
        self.container = QFrame()
        self.container.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 15)  # Bottom margin for spacing
        self.layout.setSpacing(8)  # Space between checkbox and description
        
        # Checkbox
        self.checkbox = QCheckBox(title)
        self.checkbox.setStyleSheet("font-weight: bold;")
        self.checkbox.setCursor(Qt.PointingHandCursor)


        
        # Description
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("""
            color: #666666; 
            font-size: 14px;
            margin-left: 34px;  # Align with checkbox text
            margin-top: -5px;
        """)
        self.desc_label.setWordWrap(True)
        
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.desc_label)
        if title == "NetCop":
            self.parameter_controls = ParameterControls()
            self.layout.addWidget(self.parameter_controls)
            self.parameter_controls.hide()

        
        return self.container
    

    def toggle_parameters(self):
        if self.netcop_check.findChild(QCheckBox).isChecked():
            self.parameter_controls.show()
        else:
            self.parameter_controls.hide()

    def create_input(self, title):
        input_container_frame = QFrame()
        input_container = QHBoxLayout(input_container_frame)
        label = QLabel(title)
        input_field = QLineEdit()
        input_container.addWidget(label)
        input_container.addWidget(input_field)

        return input_container_frame

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