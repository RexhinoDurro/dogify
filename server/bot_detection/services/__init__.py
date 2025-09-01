# server/bot_detection/services/__init__.py
"""
Bot Detection Services Package

This package contains all the service classes and utilities for bot detection.
"""

from .bot_detection_service import BotDetectionService

__all__ = ['BotDetectionService']

# Version information
__version__ = '1.0.0'
__author__ = 'Bot Detection Team'

# Service instances can be imported directly
bot_detection_service = BotDetectionService()

# Export commonly used functions/classes
def get_bot_detection_service():
    """
    Get the singleton instance of BotDetectionService
    
    Returns:
        BotDetectionService: The bot detection service instance
    """
    return bot_detection_service