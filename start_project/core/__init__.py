"""
Core module for document processing
"""

from .document_processor import DocumentProcessor
from .database import DatabaseManager

__all__ = [
    'DocumentProcessor',
    'DatabaseManager'
]

__version__ = '1.0.0'