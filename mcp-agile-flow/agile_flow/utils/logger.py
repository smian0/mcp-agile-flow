"""
Logging utility for the MCP Agile Flow server.
"""

import logging
import sys
from ..config import Config


def setup_logger(name: str = "agile_flow") -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: The name of the logger.
        
    Returns:
        A configured logger instance.
    """
    config = Config()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(config.get_log_level())
    
    # Create console handler and set level
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(config.get_log_level())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add formatter to handler
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger
