import logging
from pathlib import Path

def configure_logging() -> logging.Logger:
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger("invoice_system")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        file_handler = logging.FileHandler("logs/agent_messages.log", encoding="utf-8")
        file_handler.setFormatter(fmt)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger
