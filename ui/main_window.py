import threading
import humanize
import subprocess, os
from PyQt6.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QTextEdit, QMessageBox
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QSpinBox

from PyQt6.QtCore import Qt

from datetime import datetime
# own modules
from config.config_manager import load_settings, save_settings
from rsync.runner import run_all_syncs
from config.constants import LOG_FILE # to display recent entries
from config.constants import UNINSTALL_FILE, TEMP_UNINSTALL_PATH

#nb there is 1 hardcoded path to uninstall.sh in the last 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CopyToTheBox")
        self.setGeometry(200, 200, 400, 400)
        self.settings = load_settings()

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Sync Now
        self.sync_now_button = QPushButton("Sync Now")
        self.sync_now_button.clicked.connect(self.sync_now)
        layout.addWidget(self.sync_now_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # toggle enable / disable  new code vv4
        self.toggle_button = QPushButton()
        self.toggle_button.clicked.connect(self.toggle_sync)
        layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Last Sync Time
        self.last_sync_label = QLabel("Last Sync: Not recorded")
        layout.addWidget(self.last_sync_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Sync Interval, new code in vv4
        sync_interval = self.settings.get("syncInterval", 1800)
        minutes = sync_interval // 60

        self.interval_label = QLabel(f"Sync Interval: {minutes} min")
        layout.addWidget(self.interval_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.interval_input = QSpinBox()
        self.interval_input.setRange(10, 120)  # 10 min to 2 hrs
        self.interval_input.setSingleStep(10)
        self.interval_input.setValue(minutes)
        self.interval_input.valueChanged.connect(self.update_sync_interval)
        layout.addWidget(self.interval_input, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Help / About  NEW BUTTON in vv4
        self.help_button = QPushButton("Help / About")
        self.help_button.clicked.connect(self.show_help_dialog)
        layout.addWidget(self.help_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # View Log
        self.view_log_button = QPushButton("View Log (last 10 lines)")
        self.view_log_button.clicked.connect(self.show_recent_logs)
        layout.addWidget(self.view_log_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Uninstall button
        self.uninstall_button = QPushButton("Uninstall App")
        self.uninstall_button.clicked.connect(self.uninstall_app)
        layout.addWidget(self.uninstall_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Apply layout 
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # create some Brainbox style  new code vv4
        self.setStyleSheet("""
            QMainWindow {
                background-color: #070934;
                color: white;
            }
            QPushButton {
                background-color: #2E2FE3;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;         /* More padding for size */
                font-size: 20px;            /* Slightly larger text */
                max-width: 300px;           /* Limit button width */
                min-width: 200px;
                min-height: 40px;           /* Make button taller */
            }
            QPushButton:hover {
                background-color: #448D76;
            }
            QLabel {
                color: #D4F7EC;
            }
            QSpinBox {
                background-color: #D4F7EC;
                color: #070934;
                border: 1px solid #448D76;
                padding: 4px 6px;
                min-height: 40px;
                max-width: 300px;           /* Limit button width */
                min-width: 200px;
                font-size: 20px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 30px;
                height: 20px;
            }
            QTextEdit {
                background-color: #D4F7EC;
                color: #070934;
                border: 1px solid #448D76;
                padding: 4px;
            }
        """)

        # Initial state
        self.load_state()

    def load_state(self):
        enabled = self.settings.get("enabled", True) #default to true if property or file missing
        self.toggle_button.setText(
            "Disable Sync" if enabled else "Enable Sync"
        )

        last_sync_raw = self.settings.get("lastRun")
        if last_sync_raw:
            try:
                dt = datetime.fromisoformat(last_sync_raw)
                pretty_time = humanize.naturaltime(datetime.now() - dt)
                self.last_sync_label.setText(f"Last Sync: {pretty_time}")
            except Exception:
                self.last_sync_label.setText(f"Last Sync: {last_sync_raw}")
        else:
            self.last_sync_label.setText("Last Sync: Not recorded")

    def sync_now(self):
        def run_and_update():
            run_all_syncs()
            self.settings["lastRun"] = datetime.now().isoformat()
            save_settings(self.settings)
        self.last_sync_label.setText("Last sync: Just now ...") # update UI once
        # run run_and_update in a background thread
        threading.Thread(target=run_and_update, daemon=True).start()

    def update_sync_interval(self, value):
        self.settings["syncInterval"] = value * 60  # Convert to seconds
        save_settings(self.settings)
        self.interval_label.setText(f"Sync Interval: {value} min")
        #QMessageBox.information(self, "Settings Updated", "Sync interval updated.") # display notif

    def toggle_sync(self):
        self.settings["enabled"] = not self.settings.get("enabled", True)
        save_settings(self.settings)
        self.load_state()

    def show_recent_logs(self):
        try:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()[-10:]
                log_text = "".join(lines) or "Log is empty."
        except Exception as e:
            log_text = f"Failed to read log: {e}" #nb use f"text str" so e is expanded to its val

        dialog = QDialog(self)
        dialog.setWindowTitle("Recent Log Entries")
        dialog.resize(1100, 300)  # w x h  nice and wide the messages are long on each line
        layout = QVBoxLayout()
        log_box = QTextEdit()
        log_box.setReadOnly(True)
        log_box.setPlainText(log_text)
        layout.addWidget(log_box)
        dialog.setLayout(layout)
        dialog.exec()

    def show_help_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About CopyToTheBox")
        dialog.resize(500, 600)  # Set a reasonable default size w x h
        layout = QVBoxLayout()
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>CopyToTheBox</h2>
        <p><b>Version:</b> 1.0</p>
        <p>This app automatically synchronizes selected folders to your private server using <code>rsync</code>.</p>
        
        <h3>Features</h3>
        <ul>
            <li>Background syncing at regular intervals</li>
            <li>Set the interval between 10 minutes and 2 hours</li>
            <li>Automatic sync when your computer wakes from suspend or starts up</li>
            <li>Sync with a button</li>
            <li>View recent sync logs</li>
            <li>Enable or disable it</li>
        </ul>
        <h3>What files does it back up?</h3>
        <p>It will back up any files on your device which are <strong>changed</strong> or <strong>created</strong> since the last sync</p>
        <ul>
            <li>Documents folder</li>
            <li>Downloads folder</li>
            <li>Pictures folder</li>
            <li>Videos folder</li>
        </ul>
        <h3>Setting up</h3>
        <p>Enter your Brainbox username and password when you first start</p>

        <h4>Author: Henrietta Newton 2025</h4>
        """)
        layout.addWidget(help_text)
        dialog.setLayout(layout)
        dialog.exec()

    def uninstall_app(self):
        reply = QMessageBox.question(
            self,
            "Uninstall Confirmation",
            "Are you sure you want to uninstall CopyToTheBox?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.copy(UNINSTALL_FILE, TEMP_UNINSTALL_PATH)
                os.chmod(TEMP_UNINSTALL_PATH, 0o755)
                subprocess.Popen(["/bin/bash", TEMP_UNINSTALL_PATH], close_fds=True)
                QMessageBox.information(self, "Uninstalling", "Uninstall has started. The app will now close.")
                QApplication.quit()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Uninstall failed:\n{e}")

