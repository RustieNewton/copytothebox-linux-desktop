import logging
import os
from config.constants import LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger("copytothebox")
