import requests
import json
import os

from logger import logger
from config.constants import AUTH_FILE, AUTH_URL

def login(username, password):
    try:
        # Optional: encode credentials if special characters are likely
        import urllib.parse
        user_enc = urllib.parse.quote(username)
        pass_enc = urllib.parse.quote(password)

        url = f"{AUTH_URL}?u={user_enc}&p={pass_enc}"
        logger.debug(f"Login request URL: {url}")

        response = requests.get(url, timeout=5)
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Parsed JSON: {data}")
            # serverID doesn't do anything really, rsync doesn't use it, 
            # I could add it to the module to identify the server AND user
            auth_data = {
                "rsyncID": data.get("rsyncID"),
                "publicDomain": data.get("publicDomain"),
                "serverID": data.get("serverID")
            }

            if all(auth_data.values()):
                save_auth_data(auth_data)
                logger.info("Token and server info saved successfully.")
                return auth_data["rsyncID"]
            else:
                logger.error("Missing one or more required fields in response.")
                logger.debug(f"auth_data: {auth_data}")
        else:
            logger.error(f"Server returned status code {response.status_code}")

    except requests.RequestException as e:
        logger.exception("Login request failed due to network error.")

    return None

def save_auth_data(auth_data):
    with open(AUTH_FILE, 'w') as f:
        json.dump(auth_data, f, indent=2)
    os.chmod(AUTH_FILE, 0o600)

def load_auth_data():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, 'r') as f:
            return json.load(f)
    return None

def load_token():
    data = load_auth_data()
    return data.get("rsyncID") if data else None

# at present clear_token() is unused
def clear_token():
    if os.path.exists(AUTH_FILE):
        os.remove(AUTH_FILE)
