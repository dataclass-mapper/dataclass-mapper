import logging

logger = logging.getLogger("dataclass_mapper")
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
