from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QDoubleSpinBox, QSpinBox
)
from PySide6.QtCore import Qt


class ParameterControls(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            *{
                font-size: 19px;
            }
            QSpinBox {
                    padding-right: 20px;
                    font-size: 16px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }

                QSpinBox::up-button{
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 20px;
                    height: 15px;
                    background-color: #e0e0e0;
                    border: none;
                    border-top-right-radius: 4px;
                }

                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 20px;
                    height: 15px;
                    background-color: #e0e0e0;
                    border: none;
                    border-bottom-right-radius: 4px;
                }

                QSpinBox::up-button:hover,
                QSpinBox::down-button:hover{
                    background-color: #c0c0c0;
                }

                QSpinBox::up-arrow,
                QSpinBox::down-arrow {
                    width: 10px;
                    height: 10px;
                }
        """)
        self.layout = QVBoxLayout(self)

        
        

        # Set Parameters button
        self.set_btn = QPushButton("Set Parameters")
        self.set_btn.setCursor(Qt.PointingHandCursor)
        self.set_btn.setFixedSize(180,50)
        self.set_btn.setStyleSheet("""
                QPushButton {
                    background-color: #000000;
                    color: white;
                    font-size: 19px;
                    border-radius: 12px;
                    padding: 0 15px;   
                                                
                }
                QPushButton:hover {
                    background-color: #2E2E2E;
                }
            """)
        self.set_btn.clicked.connect(self.show_inputs)
        self.layout.addWidget(self.set_btn, alignment=Qt.AlignCenter)

        # Inputs + save
        self.inputs_widget = QWidget()
        self.inputs_layout = QVBoxLayout(self.inputs_widget, alignment=Qt.AlignCenter)

        # Learning Rate input
        ir_layout = QHBoxLayout()
        ir_label = QLabel("Intermediate Representation:")
        self.ir_input = QSpinBox()
        
        self.ir_input.setRange(2, 100)
        ir_layout.addWidget(ir_label, alignment=Qt.AlignCenter)
        ir_layout.addWidget(self.ir_input, alignment=Qt.AlignCenter)

        # Epochs input
        ep_layout = QHBoxLayout()
        ep_label = QLabel("Epochs:")
        self.epochs_input = QSpinBox()
        self.epochs_input.setRange(200, 2000)
        ep_layout.addWidget(ep_label, alignment=Qt.AlignCenter)
        ep_layout.addWidget(self.epochs_input, alignment=Qt.AlignCenter)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setFixedSize(80,55)
        self.save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #000000;
                    color: white;
                    font-size: 19px;
                    border-radius: 12px;
                    padding: 0 20px;  
                    margin-top:10px;   
                }
                QPushButton:hover {
                    background-color: #2E2E2E;
                }
            """)
        self.save_btn.clicked.connect(self.save_params)

        self.inputs_layout.addLayout(ir_layout)
        self.inputs_layout.addLayout(ep_layout)
        self.inputs_layout.addWidget(self.save_btn, alignment= Qt.AlignCenter)

        self.inputs_widget.hide()
        self.layout.addWidget(self.inputs_widget, alignment=Qt.AlignCenter)

    def show_inputs(self):
        self.set_btn.hide()
        self.inputs_widget.show()

    def save_params(self):
        Intermediate_Representation = self.ir_input.value()
        epochs = self.epochs_input.value()
        self.set_params = self.window()
        self.set_params.set_params(Intermediate_Representation, epochs)
        self.inputs_widget.hide()
        self.set_btn.show()