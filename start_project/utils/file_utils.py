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