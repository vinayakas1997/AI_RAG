"""
Document Processor - File management and validation only
Handles file/folder scanning, validation, blob storage, and metadata tracking
"""

import os
from typing import List, Dict, Optional
from datetime import datetime

from .database import DatabaseManager
from ..utils import FileUtils


class DocumentProcessor:
    """
    Document processor for RAG pipeline
    
    Responsibilities:
    - File/folder scanning
    - File type validation
    - Blob storage in database
    - Metadata tracking
    - Processing status management
    
    Does NOT handle:
    - Content extraction (delegated to extractors)
    - Chunking (delegated to chunker)
    - Embeddings (delegated to embedding generator)
    """
    
    def __init__(
        self,
        file_path: str,
        use_unstructured: bool = True,
        use_docling: bool = False,
        model_name: str = "qwen2.5vl:3b-q4_K_M",
        allowed_extensions: List[str] = None,
        max_file_size_mb: int = 100,
        db_path: str = "document_metadata.db"
    ):
        """
        Initialize DocumentProcessor
        
        Args:
            file_path: Path to file or folder to process
            use_unstructured: Flag to use unstructured.io (for extractors)
            use_docling: Flag to use docling (for extractors)
            model_name: VLM model name (for extractors)
            allowed_extensions: List of allowed file extensions
            max_file_size_mb: Maximum file size in MB
            db_path: Path to SQLite database
        """
        self.file_path = file_path
        self.use_unstructured = use_unstructured
        self.use_docling = use_docling
        self.model_name = model_name
        self.allowed_extensions = allowed_extensions or ['.pdf', '.txt', '.docx', '.doc']
        self.max_file_size_mb = max_file_size_mb
        self.db_path = db_path
        
        # Initialize database
        self.db = DatabaseManager(db_path)
    
    def check_if_processed(self, file_path: str) -> Dict:
        """
        Check if file already processed in database
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: {
                'processed': bool,
                'file_hash': str,
                'metadata': dict or None
            }
        """
        try:
            # Use FileUtils for hashing
            file_hash = FileUtils.get_file_hash(file_path)
            if not file_hash:
                return {
                    'processed': False,
                    'file_hash': None,
                    'metadata': None,
                    'error': 'Failed to generate file hash'
                }
            
            # Check database
            file_record = self.db.get_file_by_hash(file_hash)
            
            if file_record:
                return {
                    'processed': True,
                    'file_hash': file_hash,
                    'metadata': file_record
                }
            else:
                return {
                    'processed': False,
                    'file_hash': file_hash,
                    'metadata': None
                }
        
        except Exception as e:
            return {
                'processed': False,
                'file_hash': None,
                'metadata': None,
                'error': str(e)
            }
    
    def is_file_or_folder(self, path: str) -> Dict:
        """
        Determine if path is file, folder, or invalid
        
        Args:
            path: Path to check
            
        Returns:
            dict: {
                'type': 'file' | 'folder' | 'invalid',
                'exists': bool,
                'path': str,
                'absolute_path': str
            }
        """
        abs_path = os.path.abspath(path)
        
        if os.path.isfile(path):
            return {
                'type': 'file',
                'exists': True,
                'path': path,
                'absolute_path': abs_path
            }
        elif os.path.isdir(path):
            return {
                'type': 'folder',
                'exists': True,
                'path': path,
                'absolute_path': abs_path
            }
        else:
            return {
                'type': 'invalid',
                'exists': False,
                'path': path,
                'absolute_path': abs_path,
                'error': 'Path does not exist'
            }
    
    def get_all_files_recursive(self, folder_path: str) -> Dict:
        """
        Recursively get all files from folder with nested structure
        Uses FileUtils for file operations
        
        Args:
            folder_path: Path to folder
            
        Returns:
            dict: {
                'root': str,
                'total_files': int,
                'total_size': int,
                'total_size_mb': float,
                'structure': dict (nested tree structure)
            }
        """
        def build_tree(path: str) -> Dict:
            """Helper function to build nested tree structure"""
            tree = {
                'path': path,
                'name': os.path.basename(path),
                'type': 'folder',
                'files': [],
                'subfolders': []
            }
            
            try:
                # Get files in current directory using FileUtils
                files_in_dir = FileUtils.list_files(
                    path,
                    extensions=self.allowed_extensions,
                    recursive=False  # Only current directory
                )
                
                # Get file info using FileUtils
                for file_path in files_in_dir:
                    file_info = FileUtils.get_file_info(file_path)
                    if 'error' not in file_info:
                        tree['files'].append({
                            'path': file_path,
                            'name': file_info['name'],
                            'extension': file_info['extension'],
                            'size': file_info['size'],
                            'modified': file_info['modified']
                        })
                
                # Handle subdirectories recursively
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        tree['subfolders'].append(build_tree(item_path))
            
            except PermissionError:
                tree['error'] = 'Permission denied'
            except Exception as e:
                tree['error'] = str(e)
            
            return tree
        
        # Build the tree structure
        structure = build_tree(folder_path)
        
        # Calculate totals
        def count_files_and_size(node: Dict):
            """Helper to count total files and size"""
            file_count = len(node.get('files', []))
            total_size = sum(f['size'] for f in node.get('files', []))
            
            for subfolder in node.get('subfolders', []):
                sub_count, sub_size = count_files_and_size(subfolder)
                file_count += sub_count
                total_size += sub_size
            
            return file_count, total_size
        
        total_files, total_size = count_files_and_size(structure)
        
        return {
            'root': folder_path,
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'structure': structure
        }
    
    def store_file_as_blob(
        self,
        file_path: str,
        file_hash: str = None,
        status: str = 'pending'
    ) -> Dict:
        """
        Store file as blob in database
        Uses FileUtils for file operations
        
        Args:
            file_path: Path to file
            file_hash: Pre-computed file hash (optional)
            status: Processing status (default: 'pending')
            
        Returns:
            dict: {
                'success': bool,
                'file_hash': str,
                'file_path': str,
                'message': str
            }
        """
        try:
            # Read file using FileUtils
            file_blob = FileUtils.read_file_binary(file_path)
            if not file_blob:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': 'Failed to read file',
                    'message': 'Could not read file as binary'
                }
            
            # Generate hash using FileUtils if not provided
            if not file_hash:
                file_hash = FileUtils.get_file_hash(file_path)
            
            if not file_hash:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': 'Failed to generate file hash',
                    'message': 'File hash generation failed'
                }
            
            # Get file info using FileUtils
            file_info = FileUtils.get_file_info(file_path)
            if 'error' in file_info:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': file_info['error'],
                    'message': 'Failed to get file info'
                }
            
            file_name = file_info['name']
            file_extension = file_info['extension']
            file_size = file_info['size']
            
            # Store in database
            success = self.db.insert_file(
                file_hash=file_hash,
                file_path=file_path,
                file_name=file_name,
                file_extension=file_extension,
                file_size=file_size,
                file_blob=file_blob,
                model_used=self.model_name,
                use_unstructured=self.use_unstructured,
                use_docling=self.use_docling,
                status=status
            )
            
            if success:
                return {
                    'success': True,
                    'file_hash': file_hash,
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_size': file_size,
                    'file_size_formatted': FileUtils.format_size(file_size),
                    'message': 'File stored successfully'
                }
            else:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': 'Database insertion failed',
                    'message': 'Failed to store file in database'
                }
        
        except Exception as e:
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e),
                'message': f'Failed to store file: {str(e)}'
            }
    
    def get_file_from_blob(self, file_hash: str) -> Optional[bytes]:
        """
        Retrieve file blob from database
        
        Args:
            file_hash: Hash of the file
            
        Returns:
            bytes or None: File content
        """
        return self.db.get_file_blob(file_hash)
    
    def process(self) -> Dict:
        """
        Main orchestration method
        Scans, validates, and stores files
        
        Returns:
            dict: {
                'success': bool,
                'summary': dict,
                'details': dict
            }
        """
        print(f"{'=' * 60}")
        print(f"Document Processor Started")
        print(f"{'=' * 60}")
        print(f"Path: {self.file_path}")
        print(f"Use Unstructured: {self.use_unstructured}")
        print(f"Use Docling: {self.use_docling}")
        print(f"Model: {self.model_name}")
        print(f"Allowed Extensions: {self.allowed_extensions}")
        print(f"Max File Size: {self.max_file_size_mb} MB")
        print(f"{'=' * 60}\n")
        
        # Step 1: Check if file or folder
        path_info = self.is_file_or_folder(self.file_path)
        print(f"Step 1: Path Type Check")
        print(f"  Type: {path_info['type']}")
        print(f"  Exists: {path_info['exists']}")
        
        if path_info['type'] == 'invalid':
            return {
                'success': False,
                'message': 'Invalid path',
                'path_info': path_info
            }
        
        # Step 2: Collect files to process
        files_to_process = []
        
        if path_info['type'] == 'folder':
            print(f"\nStep 2: Scanning folder recursively...")
            folder_structure = self.get_all_files_recursive(self.file_path)
            print(f"  Total files found: {folder_structure['total_files']}")
            print(f"  Total size: {folder_structure['total_size_mb']} MB")
            
            # Flatten structure to get all file paths
            def extract_files(node: Dict, file_list: List):
                for file_info in node.get('files', []):
                    file_list.append(file_info['path'])
                for subfolder in node.get('subfolders', []):
                    extract_files(subfolder, file_list)
            
            extract_files(folder_structure['structure'], files_to_process)
        else:
            # Single file
            files_to_process = [self.file_path]
            print(f"\nStep 2: Processing single file")
        
        # Step 3: Validate file types using FileUtils
        print(f"\nStep 3: Validating files...")
        valid_files = []
        invalid_files = []
        
        for file_path in files_to_process:
            # Use FileUtils for comprehensive validation
            is_valid, reason = FileUtils.validate_file(
                file_path,
                allowed_extensions=self.allowed_extensions,
                max_size_mb=self.max_file_size_mb,
                min_size_bytes=1
            )
            
            if is_valid:
                valid_files.append(file_path)
            else:
                invalid_files.append({
                    'path': file_path,
                    'reason': reason
                })
                print(f"  ✗ Invalid: {os.path.basename(file_path)} - {reason}")
        
        print(f"  Valid files: {len(valid_files)}")
        print(f"  Invalid files: {len(invalid_files)}")
        
        # Step 4: Check which files are already processed
        print(f"\nStep 4: Checking processed status...")
        processed_files = []
        unprocessed_files = []
        
        for file_path in valid_files:
            check_result = self.check_if_processed(file_path)
            
            if check_result['processed']:
                processed_files.append({
                    'path': file_path,
                    'hash': check_result['file_hash'],
                    'metadata': check_result['metadata']
                })
                print(f"  ✓ Already processed: {os.path.basename(file_path)}")
            else:
                unprocessed_files.append({
                    'path': file_path,
                    'hash': check_result['file_hash']
                })
        
        print(f"  Already processed: {len(processed_files)}")
        print(f"  Need processing: {len(unprocessed_files)}")
        
        # Step 5: Store unprocessed files as blobs
        print(f"\nStep 5: Storing files as blobs...")
        stored_files = []
        failed_files = []
        
        for file_info in unprocessed_files:
            result = self.store_file_as_blob(
                file_path=file_info['path'],
                file_hash=file_info['hash'],
                status='pending'
            )
            
            if result['success']:
                stored_files.append(result)
                print(f"  ✓ Stored: {os.path.basename(file_info['path'])} ({result['file_size_formatted']})")
            else:
                failed_files.append(result)
                print(f"  ✗ Failed: {os.path.basename(file_info['path'])} - {result.get('error')}")
        
        # Summary
        print(f"\n{'=' * 60}")
        print(f"Processing Summary")
        print(f"{'=' * 60}")
        print(f"Total files scanned: {len(files_to_process)}")
        print(f"Valid files: {len(valid_files)}")
        print(f"Invalid files: {len(invalid_files)}")
        print(f"Already processed: {len(processed_files)}")
        print(f"Newly stored: {len(stored_files)}")
        print(f"Failed: {len(failed_files)}")
        print(f"{'=' * 60}\n")
        
        return {
            'success': True,
            'summary': {
                'total_files_scanned': len(files_to_process),
                'valid_files': len(valid_files),
                'invalid_files': len(invalid_files),
                'already_processed': len(processed_files),
                'newly_stored': len(stored_files),
                'failed': len(failed_files)
            },
            'details': {
                'valid_files': valid_files,
                'invalid_files': invalid_files,
                'processed_files': processed_files,
                'unprocessed_files': unprocessed_files,
                'stored_results': stored_files,
                'failed_results': failed_files
            }
        }
    
    def get_pending_files(self) -> List[Dict]:
        """
        Get all files with 'pending' status
        
        Returns:
            list: Files ready for extraction
        """
        return self.db.get_all_files_by_status('pending')
    
    def get_failed_files(self) -> List[Dict]:
        """
        Get all files with 'failed' status
        
        Returns:
            list: Files that need reprocessing
        """
        return self.db.get_all_files_by_status('failed')
    
    def get_completed_files(self) -> List[Dict]:
        """
        Get all files with 'completed' status
        
        Returns:
            list: Successfully processed files
        """
        return self.db.get_all_files_by_status('completed')
    
    def get_database_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            dict: Statistics about stored files
        """
        return self.db.get_statistics()