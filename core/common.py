import logging
from .config import settings


logger = logging.getLogger(__name__)

def configure_logging():
    logging.basicConfig(level = settings.logging_level,
                        datefmt = "%Y-%m-%d %H:%M:%S",
                        format = '[%(asctime)s.%(msecs)03d]%(funcName)14s %(module)9s:%(lineno)3d %(levelname)7s - %(message)s')
configure_logging()