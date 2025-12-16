"""
Logger utility for document processing pipeline
"""

import logging
import os
from datetime import datetime
from typing import Optional
from pathlib import Path


class Logger:
    """
    Custom logger for document processing
    Provides structured logging with file and console output
    """
    
    def __init__(
        self,
        name: str = "DocumentProcessor",
        log_dir: str = "logs",
        log_level: str = "INFO",
        log_to_file: bool = True,
        log_to_console: bool = True
    ):
        """
        Initialize logger
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Enable file logging
            log_to_console: Enable console logging
        """
        self.name = name
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        if log_to_console:
            self._add_console_handler()
        
        if log_to_file:
            self._add_file_handler()
    
    def _add_console_handler(self):
        """Add console handler with formatting"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Console format - simpler
        console_format = logging.Formatter(
            '%(levelname)-8s | %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """Add file handler with formatting"""
        # Create log directory if not exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(self.log_dir, f"{self.name}_{timestamp}.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # File format - more detailed
        file_format = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """
        Log error message
        
        Args:
            message: Error message
            exc_info: Include exception traceback
        """
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """
        Log critical message
        
        Args:
            message: Critical message
            exc_info: Include exception traceback
        """
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message: str):
        """Log exception with traceback"""
        self.logger.exception(message)
    
    def log_file_operation(
        self,
        operation: str,
        file_path: str,
        status: str,
        details: Optional[str] = None
    ):
        """
        Log file operation
        
        Args:
            operation: Operation type (e.g., 'READ', 'WRITE', 'PROCESS')
            file_path: Path to file
            status: Status (e.g., 'SUCCESS', 'FAILED')
            details: Additional details
        """
        file_name = os.path.basename(file_path)
        message = f"[{operation}] {file_name} - {status}"
        if details:
            message += f" | {details}"
        
        if status.upper() in ['SUCCESS', 'COMPLETED']:
            self.info(message)
        elif status.upper() in ['FAILED', 'ERROR']:
            self.error(message)
        else:
            self.debug(message)
    
    def log_extraction(
        self,
        file_name: str,
        extractor: str,
        status: str,
        elements_count: Optional[int] = None,
        duration: Optional[float] = None
    ):
        """
        Log content extraction
        
        Args:
            file_name: Name of file
            extractor: Extractor used (unstructured, docling, vlm)
            status: Extraction status
            elements_count: Number of elements extracted
            duration: Processing duration in seconds
        """
        message = f"[EXTRACTION] {file_name} | Extractor: {extractor} | Status: {status}"
        
        if elements_count is not None:
            message += f" | Elements: {elements_count}"
        
        if duration is not None:
            message += f" | Duration: {duration:.2f}s"
        
        if status.upper() in ['SUCCESS', 'COMPLETED']:
            self.info(message)
        else:
            self.error(message)
    
    def log_chunking(
        self,
        file_name: str,
        chunks_count: int,
        status: str,
        chunk_size: Optional[int] = None
    ):
        """
        Log chunking operation
        
        Args:
            file_name: Name of file
            chunks_count: Number of chunks created
            status: Chunking status
            chunk_size: Size of each chunk
        """
        message = f"[CHUNKING] {file_name} | Chunks: {chunks_count} | Status: {status}"
        
        if chunk_size:
            message += f" | Chunk size: {chunk_size} tokens"
        
        self.info(message)
    
    def log_embedding(
        self,
        file_name: str,
        model: str,
        chunks_count: int,
        status: str,
        duration: Optional[float] = None
    ):
        """
        Log embedding generation
        
        Args:
            file_name: Name of file
            model: Embedding model used
            chunks_count: Number of chunks embedded
            status: Embedding status
            duration: Processing duration in seconds
        """
        message = f"[EMBEDDING] {file_name} | Model: {model} | Chunks: {chunks_count} | Status: {status}"
        
        if duration is not None:
            message += f" | Duration: {duration:.2f}s"
        
        self.info(message)
    
    def log_pipeline_start(self, file_path: str, config: dict):
        """
        Log pipeline start
        
        Args:
            file_path: Path being processed
            config: Pipeline configuration
        """
        separator = "=" * 60
        self.info(separator)
        self.info("PIPELINE STARTED")
        self.info(separator)
        self.info(f"Path: {file_path}")
        
        for key, value in config.items():
            self.info(f"{key}: {value}")
        
        self.info(separator)
    
    def log_pipeline_end(self, summary: dict):
        """
        Log pipeline end with summary
        
        Args:
            summary: Summary statistics
        """
        separator = "=" * 60
        self.info(separator)
        self.info("PIPELINE COMPLETED")
        self.info(separator)
        
        for key, value in summary.items():
            self.info(f"{key}: {value}")
        
        self.info(separator)
    
    def log_error_with_context(
        self,
        error_type: str,
        file_path: str,
        error_message: str,
        stage: str
    ):
        """
        Log error with context
        
        Args:
            error_type: Type of error
            file_path: File being processed
            error_message: Error message
            stage: Processing stage where error occurred
        """
        self.error(f"[{error_type}] {os.path.basename(file_path)} | Stage: {stage}")
        self.error(f"Error details: {error_message}")
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        items_count: int = 1
    ):
        """
        Log performance metrics
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            items_count: Number of items processed
        """
        avg_time = duration / items_count if items_count > 0 else duration
        
        message = f"[PERFORMANCE] {operation} | "
        message += f"Total: {duration:.2f}s | "
        message += f"Items: {items_count} | "
        message += f"Avg: {avg_time:.3f}s/item"
        
        self.info(message)
    
    def set_level(self, level: str):
        """
        Change logging level
        
        Args:
            level: New level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        new_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(new_level)
        
        for handler in self.logger.handlers:
            handler.setLevel(new_level)
    
    @staticmethod
    def get_logger(
        name: str,
        log_level: str = "INFO",
        log_dir: str = "logs"
    ) -> 'Logger':
        """
        Factory method to create logger
        
        Args:
            name: Logger name
            log_level: Logging level
            log_dir: Log directory
            
        Returns:
            Logger instance
        """
        return Logger(
            name=name,
            log_level=log_level,
            log_dir=log_dir
        )


# Create default logger instance
default_logger = Logger(
    name="DocumentProcessor",
    log_level="INFO",
    log_to_file=True,
    log_to_console=True
)