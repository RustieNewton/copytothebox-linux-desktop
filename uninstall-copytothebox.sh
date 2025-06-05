#! /bin/bash
LOG_FILE="$HOME/Desktop/copytothebox-uninstall.log" #nb desktop and not hidden
SYSTEMD_DIR="$HOME/.config/systemd/user"
DESKTOP_DIR="$HOME/.local/share/applications/"
PROJECT_DIR="$HOME/.copytothebox"

echo "YOU CAN DELETE THIS FILE WITHOUT HARMING ANYTHING" >> "$LOG_FILE"

{
	# Kill the app
	# these are the 2 running processes
	#/usr/bin/python3 -u -m rsync.sync_timer
	#python3 /home/rustie/.copytothebox/main.py
	pkill -f "rsync.sync_timer"
	pkill -f ".copytothebox/main.py"

	# Wait a bit
	sleep 2

	# desktop files
	rm  $DESKTOP_DIR/copytothebox.desktop 

	# systemd service files
	systemctl --user disable copytothebox-login.service
	systemctl --user disable copytothebox-timer.service
	rm "$SYSTEMD_DIR/copytothebox-login.service"   
	rm "$SYSTEMD_DIR/copytothebox-timer.service"  

	# applications files
	rm -r $PROJECT_DIR/*
	rmdir $PROJECT_DIR

	zenity --info --text="MyApp has been uninstalled."

	 # Delete this script (running from /tmp)
	 echo "removing uninstall script. this really is goodbye. Adieu my friend."
	 rm -- "$0"
	 
} >> "$LOG_FILE" 2>&1
