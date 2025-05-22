"""
Centralized logging configuration for the Zego Site Crawler.
Provides standardized logging across all modules with both console and file output.
"""

import logging
from datetime import datetime
from pathlib import Path


class LoggerSetup:
    """Handles configuration and setup of application-wide logging."""

    _initialized = False
    _logger = None

    @classmethod
    def setup(cls, log_level=logging.INFO, verbose=False):
        """
        Set up the logger with console and file handlers.

        Args:
            log_level (int): The logging level (e.g., logging.INFO, logging.DEBUG)
            verbose (bool): Whether to enable debug-level logging

        Returns:
            logging.Logger: The configured logger instance
        """
        if cls._initialized:
            return cls._logger

        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Create a timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"crawler_{timestamp}.log"

        # Configure the root logger
        root_logger = logging.getLogger()

        # Set the log level based on verbose flag
        if verbose:
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(log_level)

        # Create formatters
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")

        # Create and configure file handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file

        # Create and configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        if verbose:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(log_level)

        # Add handlers to the root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # Mark as initialized and store the logger
        cls._initialized = True
        cls._logger = root_logger

        root_logger.info("Logging initialized with file output to %s", log_file)
        return root_logger

    @classmethod
    def get_logger(cls, name=None):
        """
        Get a logger instance.

        Args:
            name (str, optional): Logger name, typically the module name

        Returns:
            logging.Logger: A configured logger instance
        """
        if not cls._initialized:
            cls.setup()

        if name:
            return logging.getLogger(name)

        return cls._logger


# Standard and custom log level mappings
def map_log_level(logger, level):
    """
    Map custom and standard log levels to logger methods.

    Args:
        logger (logging.Logger): The logger instance
        level (str): The log level name (e.g., "INFO", "LINKS", "FETCH")

    Returns:
        function: The appropriate logging method
    """
    # Map log levels to standard logging methods
    return {
        "INFO": logger.info,
        "ERROR": logger.error,
        "WARNING": logger.warning,
        "DEBUG": logger.debug,
        # Custom log levels - all map to debug
        "LINKS": logger.debug,
        "FETCH": logger.debug,
        "SUCCESS": logger.debug,
        "STATUS": logger.debug,
    }.get(level, logger.info)


def log_with_level(logger, message, level, args=None):
    """
    Log a message with a specified level.

    Args:
        logger (logging.Logger): The logger instance
        message (str): The message to log
        level (str): The log level (standard or custom)
        args (tuple, optional): Arguments for string formatting in the message
    """
    if args is None:
        args = ()

    # Get the appropriate logging method
    log_method = map_log_level(logger, level)

    # Call the appropriate logging method
    if args:
        log_method(message, *args)
    else:
        log_method(message)


# Convenience functions to easily get loggers
def setup_logging(log_level=logging.INFO, verbose=False):
    """
    Initialize the logging system.

    Args:
        log_level (int): The logging level
        verbose (bool): Whether to enable verbose logging

    Returns:
        logging.Logger: The root logger
    """
    return LoggerSetup.setup(log_level, verbose)


def get_logger(name=None):
    """
    Get a logger instance.

    Args:
        name (str, optional): Logger name

    Returns:
        logging.Logger: A configured logger instance
    """
    return LoggerSetup.get_logger(name)
