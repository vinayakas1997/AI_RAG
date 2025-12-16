"""
Base extractor abstract class
Defines interface that all extractors must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class BaseExtractor(ABC):
    """
    Abstract base class for all document extractors
    
    All extractors (Unstructured, Docling, VLM) must inherit from this
    and implement the required methods
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize base extractor
        
        Args:
            name: Extractor name
            version: Extractor version
        """
        self.name = name
        self.version = version
        self.extraction_count = 0
        self.last_extraction_time = None
    
    @abstractmethod
    def extract(self, file_path: str) -> Dict:
        """
        Extract content from file
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: {
                'success': bool,
                'text': str,
                'tables': list,
                'images': list,
                'metadata': dict,
                'error': str (if failed)
            }
        """
        pass
    
    @abstractmethod
    def extract_from_blob(self, blob: bytes, file_extension: str) -> Dict:
        """
        Extract content from binary data
        
        Args:
            blob: Binary file content
            file_extension: File extension (e.g., '.pdf')
            
        Returns:
            dict: Extraction results (same format as extract())
        """
        pass
    
    def get_info(self) -> Dict:
        """
        Get extractor information
        
        Returns:
            dict: Extractor metadata
        """
        return {
            'name': self.name,
            'version': self.version,
            'extraction_count': self.extraction_count,
            'last_extraction_time': self.last_extraction_time
        }
    
    def _increment_counter(self):
        """Increment extraction counter and update timestamp"""
        self.extraction_count += 1
        self.last_extraction_time = datetime.now().isoformat()
    
    def _standardize_output(
        self,
        success: bool,
        text: str = "",
        tables: List = None,
        images: List = None,
        metadata: Dict = None,
        error: str = None
    ) -> Dict:
        """
        Standardize output format across all extractors
        
        Args:
            success: Whether extraction succeeded
            text: Extracted text content
            tables: List of extracted tables
            images: List of extracted images
            metadata: Additional metadata
            error: Error message if failed
            
        Returns:
            dict: Standardized extraction result
        """
        return {
            'success': success,
            'extractor': self.name,
            'extractor_version': self.version,
            'extraction_time': datetime.now().isoformat(),
            'text': text,
            'tables': tables or [],
            'images': images or [],
            'metadata': metadata or {},
            'error': error
        }
    
    def validate_file(self, file_path: str) -> tuple:
        """
        Basic file validation
        
        Args:
            file_path: Path to file
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        import os
        
        if not os.path.exists(file_path):
            return (False, "File does not exist")
        
        if not os.path.isfile(file_path):
            return (False, "Path is not a file")
        
        if os.path.getsize(file_path) == 0:
            return (False, "File is empty")
        
        return (True, None)
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.name} v{self.version}"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}')>"