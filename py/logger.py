from datetime import date
from pathlib import Path

import logging

class Logger:
    def __init__(self, python_file_name: str, log_dir: str = "../log", console_level: int = logging.INFO, file_level: int = logging.DEBUG):
        """
        Initialize the Logger instance.

        Args:
            python_file_name (str): The name of the Python script using the logger.
            log_dir (str, optional): The directory where log files will be stored (default is "../log").
            console_level (int, optional): The logging level for console output (default is logging.INFO).
            file_level (int, optional): The logging level for log files (default is logging.DEBUG).
        """
        self._python_file_name = python_file_name
        self._log_dir = log_dir
        self._console_level = console_level
        self._file_level = file_level
        self._configure_logger()

    def _configure_logger(self):
        """
        Configure the logger with console and file handlers, log levels, and formatting.
        """
        # Create the log directory if it doesn't exist
        Path(self._log_dir).mkdir(parents=True, exist_ok=True)
        
        # Define the log message format using a custom formatter.
        formatter = logging.Formatter('%(asctime)s - %(name)-15s - %(levelname)-5s - %(message)s')

        # Create a console handler for log messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self._console_level)
        console_handler.setFormatter(formatter)

        # Create a file handler for detailed log messages
        file_handler = logging.FileHandler(Path(self._log_dir) / (date.today().__str__() + ".log"), encoding='utf-8')
        file_handler.setLevel(self._file_level)
        file_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger = logging.getLogger(self._python_file_name)
        logger.setLevel(logging.DEBUG)  # You can set the global logger level here
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.

        Returns:
            logging.Logger: The configured logger.
        """
        return logging.getLogger(self._python_file_name)
