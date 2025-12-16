"""
Unstructured.io extractor for document content extraction
"""

import os
import tempfile
from typing import Dict, List, Optional
from datetime import datetime
try:
    from .base_extractor import BaseExtractor
except:
    from base_extractor import BaseExtractor

try:
    from ..utils import FileUtils, Logger
except:
    from utils import FileUtils, Logger

# from unstructured.partition.auto import partition

class UnstructuredExtractor(BaseExtractor):
    """
    Extract content using unstructured.io library
    
    Supports: PDF, DOCX, TXT, HTML, and more
    """
    
    def __init__(
        self,
        strategy: str = "hi_res",
        infer_table_structure: bool = True,
        extract_images: bool = True,
        languages: List[str] = None, 
        logger: Optional[Logger] = None
    ):
        """
        Initialize UnstructuredExtractor
        
        Args:
            strategy: Extraction strategy ('fast', 'hi_res', 'ocr_only')
            infer_table_structure: Whether to extract table structure
            extract_images: Whether to extract image descriptions
            logger: Logger instance
        """
        super().__init__(name="unstructured", version="0.11.6")
        
        self.strategy = strategy
        self.infer_table_structure = infer_table_structure
        self.extract_images = extract_images
        self.languages = languages or ['eng']  # ← Default to English
        self.logger = logger or Logger.get_logger("UnstructuredExtractor")
        
        # Import unstructured library
        try:
            from unstructured.partition.auto import partition
            self.partition = partition
            self.available = True
        except ImportError:
            self.logger.error("unstructured library not installed")
            self.available = False
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract content from file using unstructured.io
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: {
                'success': bool,
                'text': str,
                'tables': list,
                'images': list,
                'elements': list,
                'metadata': dict
            }
        """
        start_time = datetime.now()
        
        # Validate library availability
        if not self.available:
            return self._standardize_output(
                success=False,
                error="unstructured library not available"
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
            self.logger.info(f"Languages: {', '.join(self.languages)}") 
            # Extract content with unstructured
            elements = self.partition(
                filename=file_path,
                strategy=self.strategy,
                infer_table_structure=self.infer_table_structure,
                extract_image_block_types=["Image", "Figure"] if self.extract_images else None,
                languages=self.languages
               
            )
            
            # Process elements
            text_content = []
            tables = []
            images = []
            all_elements = []
            
            for element in elements:
                element_dict = {
                    'type': element.category if hasattr(element, 'category') else 'unknown',
                    'text': str(element),
                    'metadata': element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                }
                all_elements.append(element_dict)
                
                # Categorize by type
                if element.category == "Table":
                    tables.append({
                        'text': str(element),
                        'metadata': element.metadata.to_dict() if hasattr(element, 'metadata') else {},
                        'html': getattr(element.metadata, 'text_as_html', None) if hasattr(element, 'metadata') else None
                    })
                elif element.category in ["Image", "Figure"]:
                    images.append({
                        'type': element.category,
                        'text': str(element),
                        'metadata': element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                    })
                else:
                    text_content.append(str(element))
            
            # Combine text
            full_text = "\n\n".join(text_content)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Increment counter
            self._increment_counter()
            
            # Log success
            self.logger.log_extraction(
                file_name=os.path.basename(file_path),
                extractor=self.name,
                status="SUCCESS",
                elements_count=len(elements),
                duration=duration
            )
            
            return self._standardize_output(
                success=True,
                text=full_text,
                tables=tables,
                images=images,
                metadata={
                    'total_elements': len(elements),
                    'text_elements': len(text_content),
                    'table_count': len(tables),
                    'image_count': len(images),
                    'strategy': self.strategy,
                    'duration_seconds': duration,
                    'file_name': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'elements': all_elements
                }
            )
        
        except Exception as e:
            self.logger.error(f"Extraction failed: {str(e)}", exc_info=True)
            return self._standardize_output(
                success=False,
                error=f"Extraction error: {str(e)}"
            )
        
    def set_languages(self, languages: List[str]):
        """
        Change OCR languages
        
        Args:
            languages: List of language codes
                Common codes:
                - 'eng' - English
                - 'jpn' - Japanese
                - 'chi_sim' - Simplified Chinese
                - 'chi_tra' - Traditional Chinese
                - 'kor' - Korean
        
        Example:
            extractor.set_languages(['jpn', 'eng'])
        """
        self.languages = languages
        self.logger.info(f"Languages set to: {', '.join(languages)}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get commonly used language codes
        
        Returns:
            dict: Language code -> Language name
        
        Example:
            langs = extractor.get_supported_languages()
            print(langs['jpn'])  # Output: Japanese
        """
        return {
            'eng': 'English',
            'jpn': 'Japanese',
            'chi_sim': 'Simplified Chinese',
            'chi_tra': 'Traditional Chinese',
            'kor': 'Korean',
            'ara': 'Arabic',
            'rus': 'Russian',
            'fra': 'French',
            'deu': 'German',
            'spa': 'Spanish',
            'ita': 'Italian',
            'por': 'Portuguese',
            'tha': 'Thai',
            'vie': 'Vietnamese',
            'hin': 'Hindi',
            'ben': 'Bengali'
        }
    
    def get_current_languages(self) -> List[str]:
        """
        Get currently configured languages
        
        Returns:
            list: Current language codes
        
        Example:
            langs = extractor.get_current_languages()
            print(langs)  # ['jpn', 'eng']
        """
        return self.languages.copy()
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
                error="unstructured library not available"
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
    
    def set_strategy(self, strategy: str):
        """
        Change extraction strategy
        
        Args:
            strategy: New strategy ('fast', 'hi_res', 'ocr_only')
        """
        if strategy in ['fast', 'hi_res', 'ocr_only']:
            self.strategy = strategy
            self.logger.info(f"Strategy changed to: {strategy}")
        else:
            self.logger.warning(f"Invalid strategy: {strategy}")
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats
        
        Returns:
            list: Supported extensions
        """
        return [
            '.pdf', '.docx', '.doc', '.txt', '.html', '.xml',
            '.pptx', '.xlsx', '.csv', '.tsv', '.md', '.rtf',
            '.odt', '.epub', '.msg', '.eml'
        ]
    
if __name__ == "__main__":
    file_path = r"C:\Users\106761\Desktop\Rag_Test_Files\下野部工場\02AC001：下野部工場　機密区域管理要領\02AC001(1)：下野部工場　機密区域管理要領.pdf"
    extractor = UnstructuredExtractor()

    # Extract from PDF
    result = extractor.extract(file_path=file_path)

    if result['success']:
        print(f"Extracted text: {result['text'][:100]}...")
        print(f"Found {len(result['tables'])} tables")
        print(f"Found {len(result['images'])} images")
    else:
        print(f"Extraction failed: {result['error']}")