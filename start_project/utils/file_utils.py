"""
File utility functions for document processing
"""

import os
import hashlib
import mimetypes
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class FileUtils:
    """
    Utility class for file operations
    """
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'md5') -> Optional[str]:
        """
        Generate hash of file content
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('md5', 'sha256', 'sha1')
            
        Returns:
            str or None: Hash as hex string
        """
        try:
            if algorithm == 'md5':
                hasher = hashlib.md5()
            elif algorithm == 'sha256':
                hasher = hashlib.sha256()
            elif algorithm == 'sha1':
                hasher = hashlib.sha1()
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
        
        except Exception as e:
            print(f"Error hashing file {file_path}: {e}")
            return None
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """
        Get comprehensive file information
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: File information
        """
        try:
            stat = os.stat(file_path)
            
            return {
                'path': file_path,
                'absolute_path': os.path.abspath(file_path),
                'name': os.path.basename(file_path),
                'extension': os.path.splitext(file_path)[1].lower(),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path),
                'exists': os.path.exists(file_path),
                'mime_type': mimetypes.guess_type(file_path)[0]
            }
        
        except Exception as e:
            return {
                'path': file_path,
                'error': str(e),
                'exists': False
            }
    
    @staticmethod
    def validate_file(
        file_path: str,
        allowed_extensions: List[str] = None,
        max_size_mb: Optional[int] = None,
        min_size_bytes: int = 1
    ) -> Tuple[bool, str]:
        """
        Validate file based on criteria
        
        Args:
            file_path: Path to file
            allowed_extensions: List of allowed extensions
            max_size_mb: Maximum file size in MB
            min_size_bytes: Minimum file size in bytes
            
        Returns:
            tuple: (is_valid: bool, reason: str)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return (False, "File does not exist")
        
        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            return (False, "Path is not a file")
        
        # Check extension
        if allowed_extensions:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in allowed_extensions:
                return (False, f"Extension {ext} not in allowed list: {allowed_extensions}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        
        if file_size < min_size_bytes:
            return (False, f"File too small (< {min_size_bytes} bytes)")
        
        if max_size_mb and file_size > (max_size_mb * 1024 * 1024):
            return (False, f"File too large (> {max_size_mb} MB)")
        
        return (True, "Valid file")
    
    @staticmethod
    def create_temp_file(content: bytes, suffix: str = '') -> str:
        """
        Create temporary file with content
        
        Args:
            content: Binary content
            suffix: File suffix/extension
            
        Returns:
            str: Path to temporary file
        """
        import tempfile
        
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix)
            
            with os.fdopen(fd, 'wb') as f:
                f.write(content)
            
            return temp_path
        
        except Exception as e:
            print(f"Error creating temp file: {e}")
            return None
    
    @staticmethod
    def safe_filename(filename: str, max_length: int = 255) -> str:
        """
        Create safe filename by removing invalid characters
        
        Args:
            filename: Original filename
            max_length: Maximum length
            
        Returns:
            str: Safe filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            name = name[:max_length - len(ext)]
            filename = name + ext
        
        return filename
    
    @staticmethod
    def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
        """
        Copy file from source to destination
        
        Args:
            src: Source file path
            dst: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            bool: True if successful
        """
        try:
            if not overwrite and os.path.exists(dst):
                print(f"Destination file already exists: {dst}")
                return False
            
            # Create destination directory if needed
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            
            shutil.copy2(src, dst)
            return True
        
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    @staticmethod
    def move_file(src: str, dst: str, overwrite: bool = False) -> bool:
        """
        Move file from source to destination
        
        Args:
            src: Source file path
            dst: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            bool: True if successful
        """
        try:
            if not overwrite and os.path.exists(dst):
                print(f"Destination file already exists: {dst}")
                return False
            
            # Create destination directory if needed
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            
            shutil.move(src, dst)
            return True
        
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete file
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if successful
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    @staticmethod
    def ensure_directory(dir_path: str) -> bool:
        """
        Ensure directory exists (create if needed)
        
        Args:
            dir_path: Directory path
            
        Returns:
            bool: True if successful
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
    
    @staticmethod
    def get_directory_size(dir_path: str) -> int:
        """
        Calculate total size of directory
        
        Args:
            dir_path: Directory path
            
        Returns:
            int: Size in bytes
        """
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        
        except Exception as e:
            print(f"Error calculating directory size: {e}")
        
        return total_size
    
    @staticmethod
    def list_files(
        dir_path: str,
        extensions: List[str] = None,
        recursive: bool = False
    ) -> List[str]:
        """
        List files in directory
        
        Args:
            dir_path: Directory path
            extensions: Filter by extensions (e.g., ['.pdf', '.txt'])
            recursive: Search subdirectories
            
        Returns:
            list: List of file paths
        """
        files = []
        
        try:
            if recursive:
                for root, dirs, filenames in os.walk(dir_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        
                        # Filter by extension if specified
                        if extensions:
                            ext = os.path.splitext(filename)[1].lower()
                            if ext in extensions:
                                files.append(file_path)
                        else:
                            files.append(file_path)
            else:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    
                    if os.path.isfile(item_path):
                        # Filter by extension if specified
                        if extensions:
                            ext = os.path.splitext(item)[1].lower()
                            if ext in extensions:
                                files.append(item_path)
                        else:
                            files.append(item_path)
        
        except Exception as e:
            print(f"Error listing files: {e}")
        
        return files
    
    @staticmethod
    def read_file_binary(file_path: str) -> Optional[bytes]:
        """
        Read file as binary
        
        Args:
            file_path: Path to file
            
        Returns:
            bytes or None: File content
        """
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    @staticmethod
    def read_file_text(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read file as text
        
        Args:
            file_path: Path to file
            encoding: Text encoding
            
        Returns:
            str or None: File content
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    @staticmethod
    def write_file_binary(file_path: str, content: bytes) -> bool:
        """
        Write binary content to file
        
        Args:
            file_path: Path to file
            content: Binary content
            
        Returns:
            bool: True if successful
        """
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return True
        
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    
    @staticmethod
    def write_file_text(
        file_path: str,
        content: str,
        encoding: str = 'utf-8'
    ) -> bool:
        """
        Write text content to file
        
        Args:
            file_path: Path to file
            content: Text content
            encoding: Text encoding
            
        Returns:
            bool: True if successful
        """
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return True
        
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            str: Formatted size (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def save_extraction_results(
        result: Dict,
        output_dir: str = "extraction_results",
        file_name: str = None
    ) -> Dict:
        """
        Save extraction results to files for inspection
        
        Args:
            result: Extraction result dict from extractor
            output_dir: Directory to save results
            file_name: Base filename (auto-generated if None)
            
        Returns:
            dict: Paths to saved files
        """
        import json
        from datetime import datetime
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename if not provided
            if not file_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"extraction_{timestamp}"
            
            # Remove extension if present
            file_name = os.path.splitext(file_name)[0]
            
            saved_files = {}
            
            # 1. Save full result as JSON
            json_path = os.path.join(output_dir, f"{file_name}_full.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            saved_files['json'] = json_path
            
            # 2. Save extracted text
            if result.get('text'):
                text_path = os.path.join(output_dir, f"{file_name}_text.txt")
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
                saved_files['text'] = text_path
            
            # 3. Save tables separately
            if result.get('tables'):
                tables_dir = os.path.join(output_dir, f"{file_name}_tables")
                os.makedirs(tables_dir, exist_ok=True)
                
                for i, table in enumerate(result['tables']):
                    # Save as text
                    table_txt_path = os.path.join(tables_dir, f"table_{i+1}.txt")
                    with open(table_txt_path, 'w', encoding='utf-8') as f:
                        f.write(table['text'])
                    
                    # Save as HTML if available
                    if table.get('html'):
                        table_html_path = os.path.join(tables_dir, f"table_{i+1}.html")
                        with open(table_html_path, 'w', encoding='utf-8') as f:
                            f.write(table['html'])
                    
                    # Save metadata as JSON
                    table_json_path = os.path.join(tables_dir, f"table_{i+1}_metadata.json")
                    with open(table_json_path, 'w', encoding='utf-8') as f:
                        json.dump(table.get('metadata', {}), f, indent=2, ensure_ascii=False)
                
                saved_files['tables_dir'] = tables_dir
            
            # 4. Save images info
            if result.get('images'):
                images_path = os.path.join(output_dir, f"{file_name}_images.json")
                with open(images_path, 'w', encoding='utf-8') as f:
                    json.dump(result['images'], f, indent=2, ensure_ascii=False)
                saved_files['images'] = images_path
            
            # 5. Save metadata
            if result.get('metadata'):
                metadata_path = os.path.join(output_dir, f"{file_name}_metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(result['metadata'], f, indent=2, ensure_ascii=False)
                saved_files['metadata'] = metadata_path
            
            # 6. Save summary report
            summary_path = os.path.join(output_dir, f"{file_name}_summary.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("EXTRACTION SUMMARY\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Success: {result.get('success')}\n")
                f.write(f"Extractor: {result.get('extractor')}\n")
                f.write(f"Version: {result.get('extractor_version')}\n")
                f.write(f"Extraction Time: {result.get('extraction_time')}\n\n")
                
                if result.get('metadata'):
                    f.write("Statistics:\n")
                    f.write(f"  Total Elements: {result['metadata'].get('total_elements', 0)}\n")
                    f.write(f"  Text Elements: {result['metadata'].get('text_elements', 0)}\n")
                    f.write(f"  Tables: {result['metadata'].get('table_count', 0)}\n")
                    f.write(f"  Images: {result['metadata'].get('image_count', 0)}\n")
                    f.write(f"  Duration: {result['metadata'].get('duration_seconds', 0):.2f}s\n\n")
                
                f.write(f"Text Length: {len(result.get('text', ''))} characters\n\n")
                
                f.write("Saved Files:\n")
                for key, path in saved_files.items():
                    f.write(f"  {key}: {path}\n")
            
            saved_files['summary'] = summary_path
            
            return {
                'success': True,
                'saved_files': saved_files,
                'output_dir': output_dir
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        


