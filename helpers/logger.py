import logging
import os

# Configure logging
def setup_logger(log_file:str='agent.log'):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    log_folder = "log"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    log_path = os.path.join(log_folder, log_file)

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger