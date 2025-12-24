"""
Logging utilities for routing logs to UI and file.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal


class QtLogHandler(logging.Handler, QObject):
    """Custom logging handler that emits Qt signals for UI display."""

    log_signal = pyqtSignal(str)

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record):
        """Emit log record as Qt signal."""
        msg = self.format(record)
        self.log_signal.emit(msg)


def setup_logging(log_file: Optional[Path] = None, qt_handler: Optional[QtLogHandler] = None):
    """
    Setup application logging.

    Args:
        log_file: Optional file path for logging
        qt_handler: Optional Qt handler for UI logging
    """
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Qt handler for UI
    if qt_handler:
        qt_handler.setLevel(logging.INFO)
        qt_formatter = logging.Formatter('%(levelname)s: %(message)s')
        qt_handler.setFormatter(qt_formatter)
        logger.addHandler(qt_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

