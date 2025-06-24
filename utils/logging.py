"""
Logging utilities for the payment system.
"""
import os
import logging
from datetime import datetime
from typing import Optional


class DayNameFormatter(logging.Formatter):
    """Custom formatter that includes day name in log records."""
    
    def format(self, record):
        day_name = datetime.now().strftime('%A')
        record.day_name = day_name
        return super().format(record)


def setup_logger(
    name: str,
    log_dir: Optional[str] = None,
    level: int = logging.DEBUG
) -> logging.Logger:
    """
    Set up a logger with file output and day name formatting.
    
    Args:
        name: Logger name
        log_dir: Directory to save logs (defaults to ./logs)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    # Get the directory where the main script is located
    if log_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(os.path.dirname(script_dir), "logs")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate log filename with current date and day name
    current_date = datetime.now()
    day_name = current_date.strftime('%A')
    date_str = current_date.strftime('%Y-%m-%d')
    log_filename = os.path.join(log_dir, f"payment_mcp_{date_str}_{day_name}.log")
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_filename, mode='a')
    file_handler.setLevel(level)
    
    # Create formatter
    formatter = DayNameFormatter(
        '%(asctime)s - %(day_name)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    logger.info(f"Logger '{name}' initialized. Logs will be saved to: {log_filename}")
    
    return logger
