import os
import sys

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.login_dialog import RegisterWindow
from auth.auth_manager import load_auth_data
from config.config_manager import load_settings
from logger import logger

def main():

    app = QApplication(sys.argv)

    token = load_auth_data()
    if not token:
        logger.info("Not registered yet, opening window to register.")
        register_window = RegisterWindow()
        register_window.show()

        # Start event loop, wait until user closes register window
        app.exec()

        # After register window closes, check for token
        if not register_window.token:
            logger.info("user cancelled the registration, or registration failed")
            sys.exit(0)  # User cancelled or registration failed

    logger.info("auth token available after earlier registration, loading settings")
    settings = load_settings()
    if not settings.get("enabled", True):
        logger.info("Syncing is currently disabled. UI started for status/config.")
    logger.info("auth token and settings available, opening UI window")
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        logger.error(f"Unhandled exception in main: {e}")
        traceback.print_exc()
