"""
Docling extractor for document content extraction
"""

import os
import tempfile
from typing import Dict, List, Optional
from datetime import datetime

# from .base_extractor import BaseExtractor
# from ..utils import FileUtils, Logger
try:
    from .base_extractor import BaseExtractor
except:
    from base_extractor import BaseExtractor

try:
    from ..utils import FileUtils, Logger
except:
    from utils import FileUtils, Logger

class DoclingExtractor(BaseExtractor):
    """
    Extract content using Docling library
    
    Docling specializes in document layout analysis
    """
    
    def __init__(
        self,
        extract_tables: bool = True,
        extract_images: bool = True,
        languages: List[str] = None,
        logger: Optional[Logger] = None
    ):
        """
        Initialize DoclingExtractor
        
        Args:
            extract_tables: Whether to extract tables
            extract_images: Whether to extract images
            languages: List of languages (for OCR if needed)
            logger: Logger instance
        """
        super().__init__(name="docling", version="1.0.0")
        
        self.extract_tables = extract_tables
        self.extract_images = extract_images
        self.languages = languages or ['eng']
        self.logger = logger or Logger.get_logger("DoclingExtractor")
        
        # Import docling library
        try:
            from docling.document_converter import DocumentConverter
            self.DocumentConverter = DocumentConverter
            self.available = True
        except ImportError:
            self.logger.error("docling library not installed")
            self.available = False
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract content from file using Docling
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: {
                'success': bool,
                'text': str,
                'tables': list,
                'images': list,
                'metadata': dict
            }
        """
        start_time = datetime.now()
        
        # Validate library availability
        if not self.available:
            return self._standardize_output(
                success=False,
                error="docling library not available"
            )
        
        # Validate file
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            return self._standardize_output(
                success=False,
                error=error_msg
            )
        
        try:
            self.logger.info(f"Extracting content from: {os.path.basename(file_path)}")
            
            # Create converter
            converter = self.DocumentConverter()
            
            # Convert document
            result = converter.convert(file_path)
            
            # Extract text content
            full_text = result.document.export_to_markdown()
            
            # Extract tables
            tables = []
            if self.extract_tables and hasattr(result.document, 'tables'):
                for i, table in enumerate(result.document.tables):
                    tables.append({
                        'index': i,
                        'text': str(table),
                        'data': table.export_to_dataframe().to_dict() if hasattr(table, 'export_to_dataframe') else {},
                        'metadata': {
                            'rows': getattr(table, 'num_rows', 0),
                            'cols': getattr(table, 'num_cols', 0)
                        }
                    })
            
            # Extract images
            images = []
            if self.extract_images and hasattr(result.document, 'pictures'):
                for i, picture in enumerate(result.document.pictures):
                    images.append({
                        'index': i,
                        'caption': getattr(picture, 'caption', ''),
                        'metadata': {
                            'page': getattr(picture, 'page', None)
                        }
                    })
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Increment counter
            self._increment_counter()
            
            # Log success
            self.logger.log_extraction(
                file_name=os.path.basename(file_path),
                extractor=self.name,
                status="SUCCESS",
                elements_count=len(tables) + len(images),
                duration=duration
            )
            
            return self._standardize_output(
                success=True,
                text=full_text,
                tables=tables,
                images=images,
                metadata={
                    'table_count': len(tables),
                    'image_count': len(images),
                    'languages': self.languages,
                    'duration_seconds': duration,
                    'file_name': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path)
                }
            )
        
        except Exception as e:
            self.logger.error(f"Extraction failed: {str(e)}", exc_info=True)
            return self._standardize_output(
                success=False,
                error=f"Extraction error: {str(e)}"
            )
    
    def extract_from_blob(self, blob: bytes, file_extension: str) -> Dict:
        """
        Extract content from binary data
        
        Args:
            blob: Binary file content
            file_extension: File extension (e.g., '.pdf')
            
        Returns:
            dict: Extraction results
        """
        # Validate library availability
        if not self.available:
            return self._standardize_output(
                success=False,
                error="docling library not available"
            )
        
        try:
            # Create temporary file
            temp_path = FileUtils.create_temp_file(blob, suffix=file_extension)
            
            if not temp_path:
                return self._standardize_output(
                    success=False,
                    error="Failed to create temporary file"
                )
            
            # Extract from temporary file
            result = self.extract(temp_path)
            
            # Clean up
            FileUtils.delete_file(temp_path)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Extraction from blob failed: {str(e)}", exc_info=True)
            return self._standardize_output(
                success=False,
                error=f"Extraction from blob error: {str(e)}"
            )
    
    def extract_tables_only(self, file_path: str) -> List[Dict]:
        """
        Extract only tables from document
        
        Args:
            file_path: Path to file
            
        Returns:
            list: List of table dictionaries
        """
        result = self.extract(file_path)
        
        if result['success']:
            return result['tables']
        else:
            return []
    
    def extract_text_only(self, file_path: str) -> str:
        """
        Extract only text from document
        
        Args:
            file_path: Path to file
            
        Returns:
            str: Extracted text
        """
        result = self.extract(file_path)
        
        if result['success']:
            return result['text']
        else:
            return ""
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats
        
        Returns:
            list: Supported extensions
        """
        return [
            '.pdf', '.docx', '.doc', '.pptx', '.html', 
            '.xlsx', '.md', '.txt'
        ]