# rsync/sync_timer.py
import time
import os
import sys

from datetime import datetime
from rsync.runner import run_all_syncs  
from config.config_manager import load_settings
from logger import logger

def main():
    while True:
        try:
            settings = load_settings()
            if settings.get("enabled", True):
                logger.info("Background sync triggered by timer.")
                run_all_syncs()
            else:
                # in dev only
                logger.info("Background sync skipped — disabled in settings.")
        except Exception as e:
            logger.error(f"Error during scheduled sync: {e}")
        
        # 🟡 RELOAD after run_all_syncs in case the file changed
        try:
            settings = load_settings()
            interval = settings.get("syncInterval", 1800)
        except Exception as e:
            logger.error(f"Error loading interval from settings: {e}")
            interval = 1800  # fallback

        time.sleep(interval)

if __name__ == "__main__":
    main()
