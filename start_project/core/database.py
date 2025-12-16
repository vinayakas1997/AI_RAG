"""
Database manager for storing file metadata and blobs
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os


class DatabaseManager:
    """
    Manages SQLite database operations for document storage and metadata
    """
    
    def __init__(self, db_path: str = "document_metadata.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables and indexes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for storing processed files with blobs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_files (
                file_hash TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_blob BLOB NOT NULL,
                processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP,
                model_used TEXT,
                extractor_used TEXT,
                use_unstructured BOOLEAN,
                use_docling BOOLEAN,
                status TEXT DEFAULT 'pending',
                chunk_count INTEGER DEFAULT 0,
                error_message TEXT,
                metadata_json TEXT
            )
        ''')
        
        # Table for storing extracted content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content_text TEXT,
                content_json TEXT,
                extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                extractor_name TEXT,
                extractor_version TEXT,
                FOREIGN KEY (file_hash) REFERENCES processed_files(file_hash)
            )
        ''')
        
        # Table for storing chunks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_chunks (
                chunk_id TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                chunk_size INTEGER NOT NULL,
                chunk_metadata TEXT,
                embedding_vector BLOB,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_hash) REFERENCES processed_files(file_hash)
            )
        ''')
        
        # Create indexes for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_path 
            ON processed_files(file_path)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_hash 
            ON processed_files(file_hash)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status 
            ON processed_files(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_extracted_file_hash 
            ON extracted_content(file_hash)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chunks_file_hash 
            ON content_chunks(file_hash)
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def insert_file(
        self,
        file_hash: str,
        file_path: str,
        file_name: str,
        file_extension: str,
        file_size: int,
        file_blob: bytes,
        model_used: Optional[str] = None,
        extractor_used: Optional[str] = None,
        use_unstructured: bool = False,
        use_docling: bool = False,
        status: str = 'pending',
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Insert file record into database
        
        Args:
            file_hash: MD5 hash of file
            file_path: Path to file
            file_name: Name of file
            file_extension: File extension
            file_size: Size in bytes
            file_blob: Binary file content
            model_used: VLM model name if used
            extractor_used: Extractor name used
            use_unstructured: Whether unstructured.io was used
            use_docling: Whether docling was used
            status: Processing status
            metadata: Additional metadata as dict
            
        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO processed_files 
                (file_hash, file_path, file_name, file_extension, file_size, 
                 file_blob, last_modified, model_used, extractor_used, 
                 use_unstructured, use_docling, status, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_hash, file_path, file_name, file_extension, file_size,
                file_blob, last_modified, model_used, extractor_used,
                use_unstructured, use_docling, status, metadata_json
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error inserting file: {e}")
            return False
    
    def get_file_by_hash(self, file_hash: str) -> Optional[Dict]:
        """
        Get file record by hash
        
        Args:
            file_hash: MD5 hash of file
            
        Returns:
            dict or None: File record
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT file_hash, file_path, file_name, file_extension, 
                       file_size, processed_date, last_modified, model_used, 
                       extractor_used, status, chunk_count, metadata_json
                FROM processed_files
                WHERE file_hash = ?
            ''', (file_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'file_hash': result[0],
                    'file_path': result[1],
                    'file_name': result[2],
                    'file_extension': result[3],
                    'file_size': result[4],
                    'processed_date': result[5],
                    'last_modified': result[6],
                    'model_used': result[7],
                    'extractor_used': result[8],
                    'status': result[9],
                    'chunk_count': result[10],
                    'metadata': json.loads(result[11]) if result[11] else None
                }
            return None
        
        except Exception as e:
            print(f"Error getting file: {e}")
            return None
    
    def get_file_blob(self, file_hash: str) -> Optional[bytes]:
        """
        Get file blob by hash
        
        Args:
            file_hash: MD5 hash of file
            
        Returns:
            bytes or None: File binary content
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT file_blob FROM processed_files
                WHERE file_hash = ?
            ''', (file_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        
        except Exception as e:
            print(f"Error getting blob: {e}")
            return None
    
    def update_file_status(
        self,
        file_hash: str,
        status: str,
        error_message: Optional[str] = None,
        chunk_count: Optional[int] = None
    ) -> bool:
        """
        Update file processing status
        
        Args:
            file_hash: MD5 hash of file
            status: New status
            error_message: Error message if failed
            chunk_count: Number of chunks created
            
        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if chunk_count is not None:
                cursor.execute('''
                    UPDATE processed_files
                    SET status = ?, error_message = ?, chunk_count = ?
                    WHERE file_hash = ?
                ''', (status, error_message, chunk_count, file_hash))
            else:
                cursor.execute('''
                    UPDATE processed_files
                    SET status = ?, error_message = ?
                    WHERE file_hash = ?
                ''', (status, error_message, file_hash))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error updating status: {e}")
            return False
    
    def insert_extracted_content(
        self,
        file_hash: str,
        content_type: str,
        content_text: Optional[str] = None,
        content_json: Optional[Dict] = None,
        extractor_name: Optional[str] = None,
        extractor_version: Optional[str] = None
    ) -> bool:
        """
        Insert extracted content
        
        Args:
            file_hash: MD5 hash of file
            content_type: Type of content (text, table, image, etc.)
            content_text: Plain text content
            content_json: Structured content as dict
            extractor_name: Name of extractor used
            extractor_version: Version of extractor
            
        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            content_json_str = json.dumps(content_json) if content_json else None
            
            cursor.execute('''
                INSERT INTO extracted_content
                (file_hash, content_type, content_text, content_json, 
                 extractor_name, extractor_version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                file_hash, content_type, content_text, content_json_str,
                extractor_name, extractor_version
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error inserting extracted content: {e}")
            return False
    
    def get_extracted_content(self, file_hash: str) -> List[Dict]:
        """
        Get all extracted content for a file
        
        Args:
            file_hash: MD5 hash of file
            
        Returns:
            list: List of extracted content records
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content_type, content_text, content_json, 
                       extraction_date, extractor_name, extractor_version
                FROM extracted_content
                WHERE file_hash = ?
                ORDER BY id
            ''', (file_hash,))
            
            results = cursor.fetchall()
            conn.close()
            
            content_list = []
            for row in results:
                content_list.append({
                    'id': row[0],
                    'content_type': row[1],
                    'content_text': row[2],
                    'content_json': json.loads(row[3]) if row[3] else None,
                    'extraction_date': row[4],
                    'extractor_name': row[5],
                    'extractor_version': row[6]
                })
            
            return content_list
        
        except Exception as e:
            print(f"Error getting extracted content: {e}")
            return []
    
    def insert_chunk(
        self,
        chunk_id: str,
        file_hash: str,
        chunk_index: int,
        chunk_text: str,
        chunk_metadata: Optional[Dict] = None,
        embedding_vector: Optional[bytes] = None
    ) -> bool:
        """
        Insert content chunk
        
        Args:
            chunk_id: Unique chunk identifier
            file_hash: MD5 hash of source file
            chunk_index: Index of chunk in sequence
            chunk_text: Text content of chunk
            chunk_metadata: Additional metadata as dict
            embedding_vector: Embedding vector as bytes
            
        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            chunk_size = len(chunk_text)
            metadata_json = json.dumps(chunk_metadata) if chunk_metadata else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO content_chunks
                (chunk_id, file_hash, chunk_index, chunk_text, chunk_size,
                 chunk_metadata, embedding_vector)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                chunk_id, file_hash, chunk_index, chunk_text, chunk_size,
                metadata_json, embedding_vector
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error inserting chunk: {e}")
            return False
    
    def get_chunks_by_file(self, file_hash: str) -> List[Dict]:
        """
        Get all chunks for a file
        
        Args:
            file_hash: MD5 hash of file
            
        Returns:
            list: List of chunk records
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT chunk_id, chunk_index, chunk_text, chunk_size,
                       chunk_metadata, created_date
                FROM content_chunks
                WHERE file_hash = ?
                ORDER BY chunk_index
            ''', (file_hash,))
            
            results = cursor.fetchall()
            conn.close()
            
            chunks = []
            for row in results:
                chunks.append({
                    'chunk_id': row[0],
                    'chunk_index': row[1],
                    'chunk_text': row[2],
                    'chunk_size': row[3],
                    'chunk_metadata': json.loads(row[4]) if row[4] else None,
                    'created_date': row[5]
                })
            
            return chunks
        
        except Exception as e:
            print(f"Error getting chunks: {e}")
            return []
    
    def get_all_files_by_status(self, status: str) -> List[Dict]:
        """
        Get all files with specific status
        
        Args:
            status: Status to filter by
            
        Returns:
            list: List of file records
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT file_hash, file_path, file_name, status
                FROM processed_files
                WHERE status = ?
                ORDER BY processed_date DESC
            ''', (status,))
            
            results = cursor.fetchall()
            conn.close()
            
            files = []
            for row in results:
                files.append({
                    'file_hash': row[0],
                    'file_path': row[1],
                    'file_name': row[2],
                    'status': row[3]
                })
            
            return files
        
        except Exception as e:
            print(f"Error getting files by status: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            dict: Statistics about stored files
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total files
            cursor.execute('SELECT COUNT(*) FROM processed_files')
            total_files = cursor.fetchone()[0]
            
            # Files by status
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM processed_files 
                GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # Total size
            cursor.execute('SELECT SUM(file_size) FROM processed_files')
            total_size = cursor.fetchone()[0] or 0
            
            # Total chunks
            cursor.execute('SELECT COUNT(*) FROM content_chunks')
            total_chunks = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_files': total_files,
                'status_counts': status_counts,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_chunks': total_chunks
            }
        
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def delete_file(self, file_hash: str) -> bool:
        """
        Delete file and all associated data
        
        Args:
            file_hash: MD5 hash of file
            
        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete chunks
            cursor.execute('DELETE FROM content_chunks WHERE file_hash = ?', (file_hash,))
            
            # Delete extracted content
            cursor.execute('DELETE FROM extracted_content WHERE file_hash = ?', (file_hash,))
            
            # Delete file record
            cursor.execute('DELETE FROM processed_files WHERE file_hash = ?', (file_hash,))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False