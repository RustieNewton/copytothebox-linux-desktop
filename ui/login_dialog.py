from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from auth.auth_manager import login

class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register with Brainbox Home Server")
        self.setFixedSize(500, 360)  # Increased height for better layout

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Instructions (QLabel instead of QTextEdit)
        instructions = QLabel()
        instructions.setTextFormat(Qt.TextFormat.RichText)
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignTop)
        instructions.setText("""
            <b style="color:#F87171; font-size:16px;">DO THIS AT HOME ONLY.</b><br><br>
            You <b>cannot register outside the home</b>.<br><br>
            To register your app, enter your <b>Brainbox username</b> and <b>password</b> below.<br>
            These credentials link your device to your Brainbox home server.
        """)
        layout.addWidget(instructions)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Brainbox username")
        layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Brainbox password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.attempt_register)
        layout.addWidget(self.register_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #070934;
                color: white;
            }
            QLabel {
                color: #D4F7EC;
                font-size: 16px;
            }
            QLineEdit {
                background-color: #D4F7EC;
                color: #070934;
                border: 1px solid #448D76;
                padding: 8px;
                font-size: 18px;
                min-height: 40px;
                min-width: 250px;
                max-width: 300px;
            }
            QPushButton {
                background-color: #2E2FE3;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 20px;
                max-width: 300px;
                min-width: 200px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #448D76;
            }
        """)

        self.token = None

    def attempt_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        token = login(username, password)  
        if token:
            self.token = token
            QMessageBox.information(self, "Success", "Registration successful.")
            self.close()
        else:
            QMessageBox.warning(self, "Registration Failed", "Invalid credentials or server error.")
