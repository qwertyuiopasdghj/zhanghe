import logging

default_format = (
    "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d:%(funcName)s] %(message)s"
)
logging.basicConfig(format=default_format, level="INFO")
logger = logging.getLogger(__name__)
