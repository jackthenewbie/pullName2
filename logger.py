import logging
import datetime
import os

# --- Logger Configuration ---
APP_LOGGER_NAME = 'loggerr' # A unique name for your application's logger

# 1. Get a specific logger instance
logger = logging.getLogger(APP_LOGGER_NAME)

# 2. Set the level for this logger. INFO and above will be processed.
logger.setLevel(logging.INFO)

# 3. Prevent messages from propagating to the root logger's handlers.
# This is key to ensuring only this logger's handlers process its messages.
logger.propagate = False

# 4. Configure the handler and formatter
# Generate a log filename with a timestamp
log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"

# Optional: Create a 'logs' directory if it doesn't exist
# log_dir = "logs" # You can specify a subdirectory
# if not os.path.exists(log_dir):
#    os.makedirs(log_dir)
# log_filepath = os.path.join(log_dir, log_filename) # Then use log_filepath

# Create a FileHandler
# Make sure the user running the script has write permissions to the log file's location.
file_handler = logging.FileHandler(log_filename) # Using log_filename directly
file_handler.setLevel(logging.INFO) # Set the level for this specific handler

# Create a Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 5. Add the handler to the logger
# Check to prevent adding handlers multiple times if the module were reloaded (unlikely for simple scripts)
if not logger.handlers:
    logger.addHandler(file_handler)

# --- End Logger Configuration ---

# The 'logger' object is now configured and can be imported by other modules.