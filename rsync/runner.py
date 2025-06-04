import os
import subprocess
import sys # used for sys.exit

from datetime import datetime
from logger import logger 
from auth.auth_manager import load_auth_data
from config.config_manager import load_settings, save_settings

def run_all_syncs():

    # check the sync is enabled, or bail
    settings = load_settings()
    if not settings.get("enabled", True ):
        return

    # check for auth token, or bail
    auth = load_auth_data()
    if not auth:
        logger.error("No auth data available. Cannot run rsync.")
        return

    # decide which host to use, or bail
    public_domain = auth['publicDomain']
    domain = resolve_sync_host(public_domain)
    if not domain:
        logger.error("No server available. Cannot run rsync.")
        return    

    rsync_id = auth['rsyncID']
    server_id = auth['serverID'] # not in use at present, here to remind me
    home = os.path.expanduser("~")

    sync_jobs = {
        "Documents/": "documents",
        "Downloads/": "downloads",
        "Pictures/": "photos",
        "Videos/": "videos",
    }

    for folder, suffix in sync_jobs.items():
        local_path = os.path.join(home, folder)
        remote_module = f"{rsync_id}_{suffix}"
        remote_url = f"rsync://bbx@{domain}:873/{remote_module}"

        cmd = ["rsync", "-rtpu", local_path, remote_url]
        logger.debug(f"Running command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Sync successful for {folder}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Sync failed for {folder}: {e.stderr}")

    # update last run time
    update_last_run()

def resolve_sync_host(public_domain):
    try:
        # Try to ping the local hostname (short timeout)
        subprocess.run(["ping", "-c", "1", "-W", "1", "brainbox"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Local hostname 'Brainbox' available, using that")
        return "brainbox"
    except subprocess.CalledProcessError:
        if public_domain:
            logger.info("public domain name is available, using that")
            return public_domain
        else:
            logger.warning("Neither local hostname nor public domain name available, cannot sync this time")
            return None  # or False, u/c F

def update_last_run():
    try:
        settings = load_settings()
        now = datetime.now().isoformat()
        settings["lastRun"] = now
        save_settings(settings)
        logger.info(f"Updated lastRun to {now}")
    except Exception as e:
        logger.error(f"Exception in update_last_run: {e}")

def main(): # req if run standalone by systemd, which it is
   
    try:
        # the main purpose
        logger.info("Sync started by systemd login or logout service, not the timer ...")
        run_all_syncs()
        logger.info("Sync completed successfully.")

    except Exception as e:
        logger.error(f"Error during sync: {e}")
        sys.exit(1)  # added for clarity of exit value for systemd

if __name__ == "__main__":
    main()
