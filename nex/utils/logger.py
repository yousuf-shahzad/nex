"""
Centralized logging configuration for the nex package
"""
import logging
import sys
from typing import Optional

def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting and configuration.
    
    Args:
        name: The name of the logger
        level: Optional logging level. Defaults to INFO if not specified.
    
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Set the logging level
        logger.setLevel(level or logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger 