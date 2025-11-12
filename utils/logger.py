"""
Logging configuration for ScanLabel AI.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: Optional[str] = None, level: Optional[str] = None, log_format: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure logger for the application.
    
    Args:
        name: Logger name (defaults to root logger)
        level: Log level (defaults to INFO)
        log_format: Log format string
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Get log level, default to INFO
    try:
        from config import settings
        log_level_str = settings.LOG_LEVEL
        fmt = settings.LOG_FORMAT
    except ImportError:
        log_level_str = level or "INFO"
        fmt = log_format or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(fmt)
    
    # Create console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler (write to log file)
    try:
        file_handler = logging.FileHandler('scanlabel_ai.log', encoding='utf-8', mode='a')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # If file logging fails, continue with console only
        pass
    
    return logger


# Create default logger (lazy initialization to avoid circular imports)
logger = None

def get_logger():
    """Get or create the default logger."""
    global logger
    if logger is None:
        logger = setup_logger("scanlabel_ai")
    return logger

# Initialize logger on import
logger = setup_logger("scanlabel_ai")

