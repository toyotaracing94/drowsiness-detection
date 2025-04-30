import logging
import os
from datetime import datetime

def create_logger(log_filepath:str, formatter, logger_name:str=None):
    if not os.path.exists(os.path.dirname(log_filepath)):
        os.makedirs(os.path.dirname(log_filepath))

    file_handler = logging.FileHandler(log_filepath)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger = logging.getLogger(logger_name)
    
    # Avoid adding duplicate handlers
    if not logger.hasHandlers():
        logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)

    return logger

# Get the current timestamp for log file naming
t = datetime.now()
current_time = t.strftime("%Y_%m_%d_%H_%M_%S.%f")
log_filepath = f"log/{current_time}.log"

# Define formatters
default_logging_formatter = logging.Formatter("%(asctime)-15s [%(levelname)s] %(module)s.%(funcName)s: %(message)s")

# Create specific logger for default logging
logging_default = create_logger(log_filepath, default_logging_formatter, 'default')