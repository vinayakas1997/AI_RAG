import os
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import sqlite3

class DocumentProcessor:
    """
    Document processor for RAG pipeline with blob storage
    """

    """
        Initialize DocumentProcessor
        
        Args:
            file_path: Path to file or folder to process
            use_unstructured: Use unstructured.io for processing
            use_docling: Use docling for processing
            model_name: VLM model to use for OCR
            allowed_extensions: List of allowed file extensions
            db_path: Path to SQLite database for metadata
        """
    
    def __init__(
        self,
        file_path: str,
        use_unstructured: bool = True,
        use_docling: bool = False,
        model_name: str = "qwen2.5vl:3b-q4_K_M",
        allowed_extensions: List[str] = None,
        db_path: str = "document_metadata.db"
    ):
        
        self.file_path = file_path
        self.use_unstructured = use_unstructured
        self.use_docling = use_docling
        self.model_name = model_name
        self.allowed_extensions = allowed_extensions or ['.pdf', '.txt', '.docx', '.doc']
        self.db_path = db_path
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """
        Initialize SQLite database for blob storage
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for storing file metadata and blobs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_files (
                file_hash TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_blob BLOB NOT NULL,
                processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_used TEXT NOT NULL,
                use_unstructured BOOLEAN NOT NULL,
                use_docling BOOLEAN NOT NULL,
                status TEXT DEFAULT 'pending',
                chunk_count INTEGER DEFAULT 0,
                error_message TEXT
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_path 
            ON processed_files(file_path)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status 
            ON processed_files(status)
        ''')
        
        conn.commit()
        conn.close()
    
    def get_file_hash(self, file_path: str) -> str:
        """
        Generate MD5 hash of file content
        
        Args:
            file_path: Path to file
            
        Returns:
            str: MD5 hash
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    # Step a) Check if already processed
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
            file_hash = self.get_file_hash(file_path)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT file_hash, file_path, file_name, file_extension, 
                       file_size, processed_date, model_used, status, chunk_count
                FROM processed_files
                WHERE file_hash = ?
            ''', (file_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'processed': True,
                    'file_hash': result[0],
                    'metadata': {
                        'file_path': result[1],
                        'file_name': result[2],
                        'file_extension': result[3],
                        'file_size': result[4],
                        'processed_date': result[5],
                        'model_used': result[6],
                        'status': result[7],
                        'chunk_count': result[8]
                    }
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
    
    # Step b) Check if file or folder
    def is_file_or_folder(self, path: str) -> Dict:
        """
        Determine if path is file or folder
        
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
                'absolute_path': abs_path
            }
    
    # Step c) Get all files recursively with nested structure
    def get_all_files_recursive(self, folder_path: str) -> Dict:
        """
        Recursively get all files from folder in nested structure
        
        Args:
            folder_path: Path to folder
            
        Returns:
            dict: {
                'root': str,
                'total_files': int,
                'total_size': int,
                'structure': dict (nested structure)
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
                items = os.listdir(path)
            except PermissionError:
                tree['error'] = 'Permission denied'
                return tree
            
            for item in items:
                item_path = os.path.join(path, item)
                
                if os.path.isfile(item_path):
                    file_info = {
                        'path': item_path,
                        'name': item,
                        'extension': os.path.splitext(item)[1].lower(),
                        'size': os.path.getsize(item_path),
                        'modified': datetime.fromtimestamp(
                            os.path.getmtime(item_path)
                        ).isoformat()
                    }
                    tree['files'].append(file_info)
                
                elif os.path.isdir(item_path):
                    subtree = build_tree(item_path)
                    tree['subfolders'].append(subtree)
            
            return tree
        
        # Build the tree structure
        structure = build_tree(folder_path)
        
        # Calculate totals
        def count_files_and_size(node: Dict) -> Tuple[int, int]:
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
    
    # Step d) Validate file type
    def validate_file_type(self, file_path: str) -> Dict:
        """
        Validate if file extension is allowed
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: {
                'valid': bool,
                'file_path': str,
                'extension': str,
                'reason': str
            }
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in self.allowed_extensions:
            return {
                'valid': True,
                'file_path': file_path,
                'extension': ext,
                'reason': 'Valid file type'
            }
        else:
            return {
                'valid': False,
                'file_path': file_path,
                'extension': ext,
                'reason': f'Extension {ext} not in allowed list: {self.allowed_extensions}'
            }
    
    def store_file_as_blob(self, file_path: str, status: str = 'pending') -> Dict:
        """
        Store file as blob in database
        
        Args:
            file_path: Path to file
            status: Processing status ('pending', 'processing', 'completed', 'failed')
            
        Returns:
            dict: Operation result
        """
        try:
            # Read file as binary
            with open(file_path, 'rb') as f:
                file_blob = f.read()
            
            file_hash = self.get_file_hash(file_path)
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()
            file_size = os.path.getsize(file_path)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO processed_files 
                (file_hash, file_path, file_name, file_extension, file_size, 
                 file_blob, model_used, use_unstructured, use_docling, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_hash, file_path, file_name, file_extension, file_size,
                file_blob, self.model_name, self.use_unstructured, 
                self.use_docling, status
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'file_hash': file_hash,
                'file_path': file_path,
                'file_name': file_name,
                'file_size': file_size,
                'message': 'File stored successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e),
                'message': 'Failed to store file'
            }
    
    def get_file_from_blob(self, file_hash: str) -> Optional[bytes]:
        """
        Retrieve file blob from database
        
        Args:
            file_hash: Hash of the file
            
        Returns:
            bytes: File content or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT file_blob FROM processed_files
                WHERE file_hash = ?
            ''', (file_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
        
        except Exception as e:
            print(f"Error retrieving blob: {e}")
            return None
    
    def process(self) -> Dict:
        """
        Main orchestration method
        
        Returns:
            dict: Processing results
        """
        print(f"=" * 60)
        print(f"Document Processor Started")
        print(f"=" * 60)
        print(f"File/Folder: {self.file_path}")
        print(f"Use Unstructured: {self.use_unstructured}")
        print(f"Use Docling: {self.use_docling}")
        print(f"Model: {self.model_name}")
        print(f"Allowed Extensions: {self.allowed_extensions}")
        print(f"=" * 60)
        
        # Step b) Check if file or folder
        path_info = self.is_file_or_folder(self.file_path)
        print(f"\nStep 1: Path Type Check")
        print(f"Type: {path_info['type']}")
        print(f"Exists: {path_info['exists']}")
        
        if path_info['type'] == 'invalid':
            return {
                'success': False,
                'message': 'Invalid path',
                'path_info': path_info
            }
        
        files_to_process = []
        
        if path_info['type'] == 'folder':
            # Step c) Get all files recursively
            print(f"\nStep 2: Scanning folder recursively...")
            folder_structure = self.get_all_files_recursive(self.file_path)
            print(f"Total files found: {folder_structure['total_files']}")
            print(f"Total size: {folder_structure['total_size_mb']} MB")
            
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
        
        print(f"\nStep 3: Validating file types...")
        valid_files = []
        invalid_files = []
        
        for file_path in files_to_process:
            # Step d) Validate file type
            validation = self.validate_file_type(file_path)
            
            if validation['valid']:
                valid_files.append(file_path)
            else:
                invalid_files.append({
                    'path': file_path,
                    'reason': validation['reason']
                })
        
        print(f"Valid files: {len(valid_files)}")
        print(f"Invalid files: {len(invalid_files)}")
        
        # Step a) Check which files are already processed
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
            else:
                unprocessed_files.append({
                    'path': file_path,
                    'hash': check_result['file_hash']
                })
        
        print(f"Already processed: {len(processed_files)}")
        print(f"Need processing: {len(unprocessed_files)}")
        
        # Store unprocessed files as blobs
        print(f"\nStep 5: Storing files as blobs...")
        stored_files = []
        
        for file_info in unprocessed_files:
            result = self.store_file_as_blob(file_info['path'], status='pending')
            stored_files.append(result)
            if result['success']:
                print(f"✓ Stored: {file_info['path']}")
            else:
                print(f"✗ Failed: {file_info['path']} - {result.get('error')}")
        
        print(f"\n{'=' * 60}")
        print(f"Processing Summary")
        print(f"{'=' * 60}")
        
        return {
            'success': True,
            'summary': {
                'total_files_scanned': len(files_to_process),
                'valid_files': len(valid_files),
                'invalid_files': len(invalid_files),
                'already_processed': len(processed_files),
                'newly_stored': len([s for s in stored_files if s.get('success')])
            },
            'details': {
                'valid_files': valid_files,
                'invalid_files': invalid_files,
                'processed_files': processed_files,
                'unprocessed_files': unprocessed_files,
                'stored_results': stored_files
            }
        }


# Usage Example
if __name__ == "__main__":
    # Example 1: Process single file
    processor = DocumentProcessor(
        file_path="test_document.pdf",
        use_unstructured=True,
        use_docling=False,
        model_name="qwen2.5vl:3b-q4_K_M"
    )
    
    result = processor.process()
    print(json.dumps(result['summary'], indent=2))
    
    # Example 2: Process entire folder
    # processor = DocumentProcessor(
    #     file_path="/path/to/documents",
    #     use_unstructured=True,
    #     use_docling=False
    # )
    # result = processor.process()