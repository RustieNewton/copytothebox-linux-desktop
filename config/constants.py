import os
import tempfile

# urls
#AUTH_URL = "https:newton.house/cgi/register.php"   DEV ONLY
AUTH_URL = "http://brainbox/cgi/register.php"

# app dir
#APP_DIR = os.path.expanduser("~/BRAINBOX/copytothebox-linux-desktop") #  FOR DEVELOPMENT ONLY
APP_DIR = os.path.expanduser("~/.copytothebox") # created in install.sh

# dirs
CONFIG_DIR = os.path.join(APP_DIR, "config")
LOG_DIR = os.path.join(APP_DIR, "logs")

# file names
UNINSTALL_FILENAME = "uninstall_copytothebox.sh"
CONFIG_FILENAME = "settings.json"
AUTH_FILENAME  = "auth.json"
LOG_FILENAME =  "copytothebox.log"

#file paths
CONFIG_FILE = os.path.join(CONFIG_DIR, CONFIG_FILENAME)
AUTH_FILE = os.path.join(CONFIG_DIR, AUTH_FILENAME)
LOG_FILE = os.path.join(LOG_DIR, LOG_FILENAME)
UNINSTALL_FILE = os.path.join(APP_DIR, UNINSTALL_FILENAME)
TEMP_UNINSTALL_PATH = os.path.join(tempfile.gettempdir(), UNINSTALL_FILENAME) #for uninstall in tmp dir