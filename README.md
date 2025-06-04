# OVERVIEW
A user-friendly Linux desktop app in Python that is a wrapper for rsync. It pushes new and updated files from the users documents, downloads, photos, and videos to their personal home server, called Brainbox.  
It runs in the background with a timer script that periodically calls a runner to sync.  It also establishes a systemd service that runs on user login. 

# detail
The user signs in at first with their server credentials, and on success the app receives auth token and public domain name from the server.
On system start the systemd service starts a timer.
The user has a UI to update settings which the timer and runner will read when running.
The user can also disable sync altogether, read logs, see last sync. and other wonderful and useful things.

# repo structure
copytothebox-linux-desktop/
├── ui/
│   └── main_window.py      # Main app window (PyQt6)
│   └── login_dialog.py     # login fields if first time
│   └── __init__.py         # to make a module, apparently
├── auth/
│   └── auth_manager.py     # Token logic
│   └── __init__.py         # to make a module, apparently
├── assets/
│   └── icon.png            # App icon
├── config/
│   └── config_manager.py   # Token logic
│   └── settings.json       # User config (initially empty), path def in constants.
│   └── auth.json           # could be in auth dir, but ok here, path def in constants
│   └── constants.py        # paths
│   └── __init__.py         # to make a module, apparently
├── logs/
│   └── copytothebox.log    # log file, def in constants.py
├── rsync/
│   └── runner.py           # rsync wrapper logic
│   └── sync_timer.py       # background timer logic
│   └── __init__.py         # to make a module, apparently
├── main.py                 # App entry point
├── logger.py               # logging classes
├── __init__.py             # to make a module
├── copytothebox-lastest.zip      # the zipped project excluding install.sh
├── copytothebox.desktop          # Desktop launcher
├── copytothebox-timer.service    # systemd service file
├── copytothebox-login.service    # systemd service file
├── README.md                     # for repo
├── INSTRUCTIONS                  # for user
├── nextSTEPS.md                  # the todo list ...  gitignore file
├── LICENSE
├── install.sh                    # install script
├── uninstall-copytothebox.sh     # uninstall script
├── copytothebox-latest.zip       # zip file containing the app less dev and repo files
└── requirements.txt

# PREPARE ZIP file 
  cd copytothebox-linux-desktop
  find . -type d -name "__pycache__" -exec rm -r {} +
  #echo "" > logs/copytothebox.log
  #rm config/auth.json # create on registration
  echo "{\"enabled\": true, \"lastRun\": false, \"syncInterval\": 1800}" > config/settings.json
  rm copytothebox-latest.zip
  zip -r copytothebox-latest.zip * -x install.sh nextSTEPS.md README.md  # README.md is for devs

# how does it work
on first opening the user supplies their brainbox username and password, 
the following auth details are saved to 
config/auth.json
{
  "rsyncID": "wkiKsRsh",
  "publicDomain": "newton.house",
  "serverID": "fe138db692ff4bceb5aee6f62c9cfcd7"
}

It runs periodically with 
  1) a timer started by systemd
  2) systemd hooks  
timer interval is in config/settings.json
{
    "enabled": true,
    "lastRun": "2025-06-03T12:01:35.204559",
    "syncInterval": 1800
}
expansion
It automatically runs on wake and shutdown, and restart (shutdown, then start)
running sync at the user-level on:
  Wake from suspend/hibernate
  Before shutdown
  is definitely doable using user-level systemd services.


## OVERVIEW
Goal: A user-friendly Linux desktop app that:

Use a Python background timer script (sync_timer.py) that:

  Runs continuously in the background
  Checks the config for enabled: true
  Executes runner.py when it should
  Sleeps for syncInterval seconds
  Logs the result
  Updates lastRun

What happens to your timer during sleep?
  The Python process does not run while suspended — its execution halts.
  The timer (e.g., a time.sleep() or any countdown) does NOT progress during sleep.
  When the system wakes up, the timer resumes exactly where it left off, not reset to zero.
  So if your timer was at 25 minutes counting down before sleep, it will resume at 25 minutes after wake — it "remembers" the elapsed time because it simply paused.

Run on system events
  Use a systemd service to launch this background timer at boot

  Use another systemd service to trigger runner.py at login
    the systemd files are user services not system services
    they are located in the HOME dir 
    they do not recieve system messages like shutdown restart
    but they do receive messages like GUI login
    it is not triggered by suspend > sign in, that does not start a new GUI session
    however the timer picks up where it left off on system sleep, so it will sync soon after

structure
  it is in modules