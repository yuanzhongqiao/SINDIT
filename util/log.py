import logging

FORMAT = "%(asctime)s SINDIT: %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("sindit")
logger.setLevel(logging.INFO)
