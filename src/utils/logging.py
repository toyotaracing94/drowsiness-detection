import logging
import os
import sys
from datetime import datetime

from loguru import logger

# Ensure logs directory exists
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

# Generate timestamp for filename, matching your original style
t = datetime.now()
current_time = t.strftime("%Y_%m_%d_%H_%M_%S.%f")
log_filepath = os.path.join(log_dir, f"{current_time}.log")

log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "[<level>{level: <8}</level>] "
    "<cyan>{module}</cyan>.<cyan>{function}</cyan>: {message}"
)

# Remove any default Loguru handlers
logger.remove()

# Console handler with color
logger.add(
    sys.stdout,
    format=log_format,
    level="INFO",
    colorize=True,
    enqueue=True,
)

# File handler with exact timestamp filename, no colors
file_log_format = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} "
    "[{level: <8}] "
    "{module}.{function}: {message}"
)

logger.add(
    log_filepath,
    format=file_log_format,
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# Intercept stdlib logging and forward to Loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

logging_default = logger.bind(name="default")