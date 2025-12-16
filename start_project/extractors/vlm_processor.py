"""
VLM (Vision Language Model) Processor for visual document understanding
Uses Ollama for local model inference
"""

import os
import base64
import json
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path
from io import BytesIO

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

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class VLMProcessor(BaseExtractor):
    """
    Vision Language Model processor using Ollama
    
    Handles:
    - Image-based PDFs (scanned documents)
    - Flowcharts and diagrams
    - Complex layouts
    - Visual understanding tasks
    """
    
    def __init__(
        self,
        model_name: str = "qwen2.5vl:3b-q4_K_M",
        ollama_host: str = "http://localhost:11434",
        auto_pull: bool = True,
        timeout: int = 300,
        logger: Optional[Logger] = None
    ):
        """
        Initialize VLM Processor
        
        Args:
            model_name: Ollama model name
            ollama_host: Ollama server URL
            auto_pull: Auto-pull model if not available
            timeout: Request timeout in seconds
            logger: Logger instance
        """
        super().__init__(name="vlm", version="1.0.0")
        
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.auto_pull = auto_pull
        self.timeout = timeout
        self.logger = logger or Logger.get_logger("VLMProcessor")
        
        # Check dependencies
        self.pil_available = PIL_AVAILABLE
        self.pymupdf_available = PYMUPDF_AVAILABLE
        
        if not self.pil_available:
            self.logger.warning("PIL not available. Install with: pip install Pillow")
        
        if not self.pymupdf_available:
            self.logger.warning("PyMuPDF not available. Install with: pip install PyMuPDF")
        
        # Check Ollama and model availability
        self.ollama_available = self._check_ollama_running()
        self.model_available = False
        
        if self.ollama_available:
            self.model_available = self._check_model_available()
        
        # Overall availability
        self.available = (
            self.pil_available and 
            self.pymupdf_available and 
            self.ollama_available and 
            self.model_available
        )
        
        # Log status
        self._log_status()
    
    def _check_ollama_running(self) -> bool:
        """
        Check if Ollama server is running
        
        Returns:
            bool: True if Ollama is accessible
        """
        try:
            response = requests.get(
                f"{self.ollama_host}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info(f"✓ Ollama server running at {self.ollama_host}")
                return True
            else:
                self.logger.error(f"✗ Ollama server returned status {response.status_code}")
                return False
        
        except requests.exceptions.ConnectionError:
            self.logger.error(f"✗ Cannot connect to Ollama at {self.ollama_host}")
            self.logger.error("  Make sure Ollama is running: ollama serve")
            return False
        
        except Exception as e:
            self.logger.error(f"✗ Error checking Ollama: {str(e)}")
            return False
    
    def _check_model_available(self) -> bool:
        """
        Check if model is available locally
        If not and auto_pull=True, download it
        
        Returns:
            bool: True if model is available
        """
        try:
            # List local models
            response = requests.get(
                f"{self.ollama_host}/api/tags",
                timeout=10
            )
            
            if response.status_code != 200:
                self.logger.error(f"Failed to list models: {response.status_code}")
                return False
            
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            
            # Check if our model exists
            if self.model_name in model_names:
                self.logger.info(f"✓ Model '{self.model_name}' found locally")
                return True
            
            # Model not found
            self.logger.warning(f"✗ Model '{self.model_name}' not found locally")
            
            # Auto-pull if enabled
            if self.auto_pull:
                self.logger.info(f"Pulling model '{self.model_name}' from Ollama...")
                return self._pull_model()
            else:
                self.logger.error(f"Auto-pull disabled. Pull manually with: ollama pull {self.model_name}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error checking model availability: {str(e)}")
            return False
    
    def _pull_model(self) -> bool:
        """
        Pull model from Ollama registry with progress bar
        
        Returns:
            bool: True if pull succeeded
        """
        try:
            from tqdm import tqdm
            TQDM_AVAILABLE = True
        except ImportError:
            TQDM_AVAILABLE = False
            self.logger.warning("tqdm not available. Install with: pip install tqdm")
        
        try:
            self.logger.info(f"Downloading {self.model_name}... (this may take a few minutes)")
            
            response = requests.post(
                f"{self.ollama_host}/api/pull",
                json={"name": self.model_name},
                timeout=self.timeout,
                stream=True
            )
            
            if response.status_code != 200:
                self.logger.error(f"Failed to pull model: {response.status_code}")
                return False
            
            # Initialize progress bar
            pbar = None
            last_status = ""
            
            # Parse streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get('status', '')
                        
                        # Handle progress with tqdm
                        if 'total' in data and 'completed' in data:
                            total = data['total']
                            completed = data['completed']
                            
                            if TQDM_AVAILABLE:
                                # Create progress bar on first iteration
                                if pbar is None:
                                    pbar = tqdm(
                                        total=total,
                                        unit='B',
                                        unit_scale=True,
                                        unit_divisor=1024,
                                        desc=f"Downloading {self.model_name}",
                                        ncols=100
                                    )
                                
                                # Update progress bar
                                pbar.n = completed
                                pbar.refresh()
                            else:
                                # Fallback: Only log when percentage changes by 5%
                                percent = (completed / total * 100) if total > 0 else 0
                                if int(percent) % 5 == 0 and status != last_status:
                                    self.logger.info(f"  Progress: {percent:.1f}% - {status}")
                                    last_status = status
                        
                        else:
                            # Status updates without progress
                            if status and status != last_status:
                                if TQDM_AVAILABLE and pbar:
                                    pbar.set_postfix_str(status)
                                else:
                                    self.logger.info(f"  {status}")
                                last_status = status
                        
                        # Check if done
                        if status == 'success':
                            if TQDM_AVAILABLE and pbar:
                                pbar.close()
                            self.logger.info(f"✓ Model '{self.model_name}' downloaded successfully")
                            return True
                    
                    except json.JSONDecodeError:
                        pass
            
            # Close progress bar if still open
            if TQDM_AVAILABLE and pbar:
                pbar.close()
            
            return True
        
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout pulling model (>{self.timeout}s)")
            self.logger.error(f"Try manually: ollama pull {self.model_name}")
            return False
        
        except Exception as e:
            self.logger.error(f"Error pulling model: {str(e)}")
            return False
    
    def _log_status(self):
        """Log processor status"""
        self.logger.info("=" * 60)
        self.logger.info("VLM Processor Status")
        self.logger.info("=" * 60)
        self.logger.info(f"PIL Available: {'✓' if self.pil_available else '✗'}")
        self.logger.info(f"PyMuPDF Available: {'✓' if self.pymupdf_available else '✗'}")
        self.logger.info(f"Ollama Running: {'✓' if self.ollama_available else '✗'}")
        self.logger.info(f"Model Available: {'✓' if self.model_available else '✗'}")
        self.logger.info(f"Overall Status: {'✓ READY' if self.available else '✗ NOT READY'}")
        self.logger.info("=" * 60)
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract content from file using VLM
        
        Args:
            file_path: Path to file (PDF or image)
            
        Returns:
            dict: Extraction results
        """
        start_time = datetime.now()
        
        # Check availability
        if not self.available:
            return self._standardize_output(
                success=False,
                error="VLM processor not available. Check logs for details."
            )
        
        # Validate file
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            return self._standardize_output(
                success=False,
                error=error_msg
            )
        
        try:
            self.logger.info(f"Processing with VLM: {os.path.basename(file_path)}")
            
            # Get file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            # Process based on file type
            if ext == '.pdf':
                result = self._process_pdf(file_path)
            elif ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                result = self._process_image(file_path)
            else:
                return self._standardize_output(
                    success=False,
                    error=f"Unsupported file type: {ext}"
                )
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            result['metadata']['duration_seconds'] = duration
            
            # Increment counter
            self._increment_counter()
            
            # Log success
            self.logger.log_extraction(
                file_name=os.path.basename(file_path),
                extractor=self.name,
                status="SUCCESS" if result['success'] else "FAILED",
                duration=duration
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"VLM processing failed: {str(e)}", exc_info=True)
            return self._standardize_output(
                success=False,
                error=f"VLM processing error: {str(e)}"
            )
    
    def _process_pdf(self, pdf_path: str) -> Dict:
        """
        Process PDF file with VLM (with progress bar)
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            dict: Processing results
        """
        try:
            from tqdm import tqdm
            TQDM_AVAILABLE = True
        except ImportError:
            TQDM_AVAILABLE = False
        
        doc = fitz.open(pdf_path)
        all_text = []
        all_pages_data = []
        
        total_pages = len(doc)  # ← Get this BEFORE closing
        self.logger.info(f"Processing {total_pages} pages with VLM...")
        
        # Create progress bar for pages
        if TQDM_AVAILABLE:
            page_iterator = tqdm(
                range(total_pages),
                desc="Processing pages",
                unit="page",
                ncols=100
            )
        else:
            page_iterator = range(total_pages)
        
        for page_num in page_iterator:
            if not TQDM_AVAILABLE:
                self.logger.info(f"  Processing page {page_num + 1}/{total_pages}...")
            
            page = doc[page_num]
            
            # Convert page to image
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Update progress bar description
            if TQDM_AVAILABLE:
                page_iterator.set_postfix_str(f"Page {page_num + 1}/{total_pages}")
            
            # Process with VLM
            page_result = self._query_ollama(
                image_base64=img_base64,
                prompt="""
                This is a Japanese document page. Please extract ALL content with complete accuracy:

                IMPORTANT: This document contains Japanese text. Preserve all Japanese characters exactly.

                Extract the following:

                1. ALL TEXT CONTENT:
                - Transcribe every word, number, and character exactly as shown
                - Maintain the original reading order (top to bottom, left to right)
                - Preserve line breaks and paragraph structure
                - Include headers, footers, page numbers, and any marginal notes

                2. TABLES (if present):
                - Identify all tables on the page
                - For each table, provide:
                    * Table title or caption (if any)
                    * Number of rows and columns
                    * Complete table content in a structured format
                    * Preserve cell alignment and merged cells
                - Format: Use markdown table syntax or describe clearly

                3. IMAGES/FIGURES (if present):
                - Identify all images, diagrams, charts, or figures
                - For each image, provide:
                    * Image type (photo, diagram, chart, logo, etc.)
                    * Detailed description of what is shown
                    * Any text or labels within the image
                    * Position on the page (top, middle, bottom)
                - Include figure numbers and captions if present

                4. FLOWCHARTS/DIAGRAMS (if present):
                - Identify all flowchart boxes and their text content
                - Describe the flow direction and connections
                - Note decision points and branches
                - Explain the process flow logically

                5. LAYOUT INFORMATION:
                - Note any special formatting (bold, italic, underlined text)
                - Identify section numbers or bullet points
                - Preserve hierarchical structure

                OUTPUT FORMAT:
                Provide a complete, structured transcription maintaining the original document layout and order.
                Do not summarize - transcribe completely and accurately.
                """
            )
            
            if page_result['success']:
                page_text = page_result['response']
                all_text.append(f"=== Page {page_num + 1} ===\n{page_text}\n")
                
                all_pages_data.append({
                    'page_number': page_num + 1,
                    'text': page_text,
                    'tokens_used': page_result.get('tokens', 0)
                })
            else:
                if not TQDM_AVAILABLE:
                    self.logger.error(f"  Failed to process page {page_num + 1}: {page_result.get('error')}")
        
        # Close document BEFORE using len(doc)
        doc.close()
        
        # Combine all pages
        full_text = "\n\n".join(all_text)
        
        # Use total_pages variable instead of len(doc)
        return self._standardize_output(
            success=True,
            text=full_text,
            metadata={
                'total_pages': total_pages,  # ← Use variable, not len(doc)
                'pages_processed': len(all_pages_data),
                'pages_data': all_pages_data,
                'model': self.model_name,
                'file_name': os.path.basename(pdf_path),
                'file_size': os.path.getsize(pdf_path)
            }
        )
    
    def _process_image(self, image_path: str) -> Dict:
        """
        Process single image with VLM
        
        Args:
            image_path: Path to image
            
        Returns:
            dict: Processing results
        """
        # Read and convert image to base64
        img_bytes = FileUtils.read_file_binary(image_path)
        if not img_bytes:
            return self._standardize_output(
                success=False,
                error="Failed to read image file"
            )
        
        img_base64 = base64.b64encode(img_bytes).decode()
        
        # Process with VLM
        result = self._query_ollama(
            image_base64=img_base64,
            prompt="""
            This image may contain Japanese text. Please analyze and extract ALL content:

            1. TEXT CONTENT:
               - Extract all visible text (Japanese, English, numbers, symbols)
               - Preserve reading order and layout
               - Note text size, style, or emphasis

            2. VISUAL ELEMENTS:
               - Describe all images, diagrams, charts, or graphics
               - Identify logos, stamps, or seals
               - Note colors and visual styling if relevant

            3. TABLES (if present):
               - Describe table structure (rows, columns)
               - Extract complete table content

            4. STRUCTURAL ELEMENTS:
               - Identify headers, footers, titles
               - Note any forms, boxes, or borders
               - Describe overall layout

            Provide a complete and detailed description of everything visible in this image.
            """
        )
        
        if result['success']:
            return self._standardize_output(
                success=True,
                text=result['response'],
                metadata={
                    'model': self.model_name,
                    'tokens_used': result.get('tokens', 0),
                    'file_name': os.path.basename(image_path)
                }
            )
        else:
            return self._standardize_output(
                success=False,
                error=result.get('error', 'Unknown error')
            )
    
    def _query_ollama(
        self,
        image_base64: str,
        prompt: str,
        temperature: float = 0.1
    ) -> Dict:
        """
        Query Ollama with image and prompt
        
        Args:
            image_base64: Base64 encoded image
            prompt: Text prompt
            temperature: Model temperature
            
        Returns:
            dict: {
                'success': bool,
                'response': str,
                'tokens': int,
                'error': str
            }
        """
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Ollama returned status {response.status_code}"
                }
            
            data = response.json()
            
            return {
                'success': True,
                'response': data.get('response', ''),
                'tokens': data.get('eval_count', 0),
                'error': None
            }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': f"Request timeout (>{self.timeout}s)"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_from_blob(self, blob: bytes, file_extension: str) -> Dict:
        """
        Extract content from binary data
        
        Args:
            blob: Binary file content
            file_extension: File extension
            
        Returns:
            dict: Extraction results
        """
        if not self.available:
            return self._standardize_output(
                success=False,
                error="VLM processor not available"
            )
        
        try:
            # Create temporary file
            temp_path = FileUtils.create_temp_file(blob, suffix=file_extension)
            
            if not temp_path:
                return self._standardize_output(
                    success=False,
                    error="Failed to create temporary file"
                )
            
            # Process
            result = self.extract(temp_path)
            
            # Clean up
            FileUtils.delete_file(temp_path)
            
            return result
        
        except Exception as e:
            return self._standardize_output(
                success=False,
                error=f"Error processing blob: {str(e)}"
            )
    
    def process_flowchart(
        self,
        file_path: str,
        prompt: str = None
    ) -> Dict:
        """
        Specialized method for flowchart extraction
        
        Args:
            file_path: Path to file
            prompt: Custom prompt (optional)
            
        Returns:
            dict: Flowchart extraction results
        """
        if not self.available:
            return self._standardize_output(
                success=False,
                error="VLM processor not available"
            )
        
        if not prompt:
            prompt = """
            This is a FLOWCHART in Japanese. Please extract complete information:

            IMPORTANT: Preserve all Japanese text exactly as shown.

            Extract the following:

            1. FLOWCHART TITLE:
               - Main title or heading of the flowchart

            2. ALL BOXES/NODES:
               - List every box, rectangle, or shape in the flowchart
               - For each box, provide:
                 * Box number or identifier
                 * Complete text content inside the box
                 * Box type (process, decision, start/end, etc.)
                 * Position in the flow

            3. CONNECTIONS/ARROWS:
               - Describe all arrows and their directions
               - Show which boxes connect to which
               - Note any labels on arrows
               - Indicate the flow direction

            4. DECISION POINTS:
               - Identify all decision points (usually diamond shapes)
               - List the decision criteria
               - Show the branching paths (Yes/No, conditions, etc.)

            5. START AND END POINTS:
               - Clearly mark the starting point
               - Clearly mark the ending point(s)

            6. ADDITIONAL ELEMENTS:
               - Any legends or keys
               - Notes or annotations
               - Database symbols or other special shapes

            OUTPUT FORMAT:
            Provide a structured description that captures the complete flowchart logic.
            Format as JSON if possible, with the following structure:
            {
              "title": "flowchart title",
              "boxes": [
                {"id": "box1", "text": "content", "type": "process", "connects_to": ["box2"]}
              ],
              "start": "box_id",
              "end": "box_id",
              "decision_points": [...]
            }

            If JSON is not suitable, provide a clear textual description maintaining the flow logic.
            """
        
        # Process with custom prompt
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.pdf':
                doc = fitz.open(file_path)
                all_flowcharts = []
                
                for page_num in range(len(doc)):
                    self.logger.info(f"  Processing flowchart on page {page_num + 1}/{len(doc)}...")
                    
                    page = doc[page_num]
                    
                    # Convert to image
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Query with flowchart prompt
                    result = self._query_ollama(img_base64, prompt)
                    
                    if result['success']:
                        all_flowcharts.append({
                            'page': page_num + 1,
                            'flowchart_data': result['response']
                        })
                
                # doc.close()
                
                combined = "\n\n".join([
                    f"=== PAGE {fc['page']} FLOWCHART ===\n{fc['flowchart_data']}"
                    for fc in all_flowcharts
                ])
                doc.close()
                return self._standardize_output(
                    success=True,
                    text=combined,
                    metadata={
                        'content_type': 'flowchart',
                        'pages_with_flowcharts': len(all_flowcharts),
                        'model': self.model_name,
                        'specialized_prompt': True
                    }
                )
            
            elif ext in ['.png', '.jpg', '.jpeg']:
                img_bytes = FileUtils.read_file_binary(file_path)
                img_base64 = base64.b64encode(img_bytes).decode()
                
                result = self._query_ollama(img_base64, prompt)
                
                if result['success']:
                    return self._standardize_output(
                        success=True,
                        text=result['response'],
                        metadata={
                            'content_type': 'flowchart',
                            'model': self.model_name,
                            'specialized_prompt': True
                        }
                    )
                else:
                    return self._standardize_output(
                        success=False,
                        error=result.get('error')
                    )
        
        except Exception as e:
            return self._standardize_output(
                success=False,
                error=f"Flowchart processing error: {str(e)}"
            )
    
    def process_tables(
        self,
        file_path: str
    ) -> Dict:
        """
        Specialized method for table extraction
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: Table extraction results
        """
        if not self.available:
            return self._standardize_output(
                success=False,
                error="VLM processor not available"
            )
        
        # Validate file
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            return self._standardize_output(
                success=False,
                error=error_msg
            )
        
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext != '.pdf':
                return self._standardize_output(
                    success=False,
                    error="Table extraction currently only supports PDF files"
                )
            
            doc = fitz.open(file_path)
            all_tables = []
            
            for page_num in range(len(doc)):
                self.logger.info(f"Extracting tables from page {page_num + 1}/{len(doc)}...")
                
                page = doc[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Convert to base64
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Table-focused prompt
                result = self._query_ollama(
                    image_base64=img_base64,
                    prompt="""
                    This page contains Japanese text and may have tables. Focus on TABLE EXTRACTION:

                    1. IDENTIFY ALL TABLES:
                       - Count how many tables are on this page
                       - If no tables, explicitly state "No tables found"

                    2. FOR EACH TABLE:
                       - Extract the complete table structure
                       - Provide table in markdown format:
                         | Header 1 | Header 2 | Header 3 |
                         |----------|----------|----------|
                         | Cell 1   | Cell 2   | Cell 3   |
                       
                       - Include:
                         * Table number or title (if present)
                         * All headers
                         * All data rows
                         * Merged cells (note them)
                         * Any notes or captions below the table

                    3. TABLE CONTEXT:
                       - What section is this table in?
                       - What is the table describing?
                       - Any relevant surrounding text

                    IMPORTANT: 
                    - Preserve all Japanese characters exactly
                    - Maintain table structure precisely
                    - Do not skip any cells
                    - Note empty cells as "empty" or "-"
                    """
                )
                
                if result['success']:
                    all_tables.append({
                        'page': page_num + 1,
                        'content': result['response']
                    })
            
            # doc.close()
            
            # Combine results
            combined = "\n\n".join([
                f"=== PAGE {t['page']} TABLES ===\n{t['content']}"
                for t in all_tables
            ])

            doc.close()
            
            return self._standardize_output(
                success=True,
                text=combined,
                tables=all_tables,
                metadata={
                    'total_pages': len(doc),
                    'pages_with_tables': len(all_tables),
                    'model': self.model_name,
                    'extraction_type': 'tables_focused'
                }
            )
        
        except Exception as e:
            self.logger.error(f"Table extraction failed: {str(e)}", exc_info=True)
            return self._standardize_output(
                success=False,
                error=f"Table extraction error: {str(e)}"
            )
    
    def get_supported_formats(self) -> List[str]:
        """
        Get supported file formats
        
        Returns:
            list: Supported extensions
        """
        return ['.pdf', '.png', '.jpg', '.jpeg', '.webp', '.gif']