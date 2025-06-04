#!/bin/bash

LOG_FILE="$HOME/Desktop/copytothebox-install.log" #nb desktop and not hidden
SYSTEMD_DIR="$HOME/.config/systemd/user"
DESKTOP_DIR="$HOME/.local/share/applications/"
PROJECT_DIR="$HOME/.copytothebox"
UNINSTALL_FILE="$PROJECT_DIR/uninstall-copytothebox.sh" # can be inside proj dir, moved on uninstall

# Get the package name (the first file starting with 'copytothebox' and ending with .zip)
PACKAGE_NAME=$(ls | grep '^copytothebox.*\.zip$' | head -n 1)

echo "YOU CAN DELETE THIS FILE WITHOUT HARMING ANYTHING"

{

  # Optional: Check if the file was found
  echo "checking package name"
  if [ -z "$PACKAGE_NAME" ]; then
    echo "No package found matching 'copytothebox*.zip'"
    exit 1
  fi
  echo "package found $PACKAGE_NAME"

  # Create app dir
  echo "making project directory"
  mkdir "$PROJECT_DIR"

  # unpack the zip file into the project directory
  echo "unpacking zip file"
  unzip -o "$PACKAGE_NAME" -d "$PROJECT_DIR"

  #clean up zip file in the curr dir (alongside the this install script)
  echo "removing zipped package"
  rm "$PACKAGE_NAME"

  # change to project dir
  cd $PROJECT_DIR
  echo "changed dir to $PROJECT_DIR"

  # Install Python dependencies (must be within project main dir for modules dependencies)
  echo "installing python3, pip and dependencies"
  #sudo apt update
  #sudo apt install -y rsync python3-pip
  python3 -m pip install -r requirements.txt # from within the project main dir

  # Copy desktop icon and launcher
  echo "installing desktop icon and launcher"
  mkdir -p "$DESKTOP_DIR"
  mv copytothebox.desktop "$DESKTOP_DIR"
  echo "editing copytothebox.desktop using stream editor (sed)"
  sed -i "s|\$HOME|$HOME|g" "$HOME/.local/share/applications/copytothebox.desktop"

  # systemd service files
  echo "installing systemd files"
  mkdir -p $SYSTEMD_DIR
  mv copytothebox-login.service   $SYSTEMD_DIR
  mv copytothebox-timer.service    $SYSTEMD_DIR
  # enable services
  echo "enabling systemd services"
  systemctl --user daemon-reexec
  systemctl --user daemon-reload
  systemctl --user enable copytothebox-login.service
  systemctl --user enable copytothebox-timer.service

  # INSTALL uninstall script (hidden and outside the project root)
  echo "enabling uninstall script"
  chmod +x  $UNINSTALL_FILE
  # If the uninstaller has sensitive deletion logic, make sure it's not writable by other users:
  chmod 700 $UNINSTALL_FILE
  zenity --info --text="CopyToTheBox app has been installed."

  # Delete this script (running from /tmp)
  echo " PRETENDING TO remov install script."
  #rm -- "$0"

} >> "$LOG_FILE" 2>&1