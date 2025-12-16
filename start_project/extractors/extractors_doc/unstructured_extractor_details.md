# UnstructuredExtractor Documentation

## Overview

`UnstructuredExtractor` is a content extraction class that uses the unstructured.io library to extract text, tables, and images from various document formats including PDF, DOCX, TXT, HTML, and more.

## Purpose

- Extract structured content from unstructured documents
- Handle multiple file formats with a single interface
- Categorize content by type (text, tables, images)
- Provide metadata about extracted content

---

## Class Hierarchy
```
BaseExtractor (Abstract)
    ↓
UnstructuredExtractor (Concrete Implementation)
```

Inherits from `BaseExtractor` and implements all required abstract methods.

---

## Initialization

### `__init__(strategy, infer_table_structure, extract_images, logger)`

**Purpose:** Initialize the UnstructuredExtractor with configuration options

**Parameters:**
- `strategy` (str, default: "hi_res"): Extraction strategy
  - `"fast"` - Quick extraction, lower quality
  - `"hi_res"` - High resolution extraction, better quality
  - `"ocr_only"` - Force OCR on all documents
- `infer_table_structure` (bool, default: True): Whether to extract table structure
- `extract_images` (bool, default: True): Whether to extract image descriptions
- `logger` (Logger, optional): Logger instance for logging operations

**Example:**
```python
from extractors import UnstructuredExtractor
from utils import Logger

# Basic initialization
extractor = UnstructuredExtractor()

# Custom configuration
extractor = UnstructuredExtractor(
    strategy="hi_res",
    infer_table_structure=True,
    extract_images=True,
    logger=Logger.get_logger("MyExtractor")
)
```

**Attributes Set:**
- `self.name` = "unstructured"
- `self.version` = "0.11.6"
- `self.available` = True/False (based on library import)

---

## Core Methods

### 1. `extract(file_path)`

**Purpose:** Extract all content from a file

**Parameters:**
- `file_path` (str): Path to the file to extract

**Returns:**
```python
dict: {
    'success': bool,                    # True if extraction succeeded
    'extractor': 'unstructured',        # Extractor name
    'extractor_version': '0.11.6',      # Version
    'extraction_time': '2024-12-16...',  # ISO timestamp
    'text': str,                        # All extracted text
    'tables': [                         # List of tables
        {
            'text': str,                # Table as text
            'metadata': dict,           # Table metadata
            'html': str or None         # Table as HTML
        }
    ],
    'images': [                         # List of images
        {
            'type': 'Image' or 'Figure',
            'text': str,                # Image description
            'metadata': dict            # Image metadata
        }
    ],
    'metadata': {                       # Extraction metadata
        'total_elements': int,          # Total elements found
        'text_elements': int,           # Number of text elements
        'table_count': int,             # Number of tables
        'image_count': int,             # Number of images
        'strategy': str,                # Strategy used
        'duration_seconds': float,      # Processing time
        'file_name': str,               # Original filename
        'file_size': int,               # File size in bytes
        'elements': [...]               # All elements with details
    },
    'error': str or None                # Error message if failed
}
```

**Example:**
```python
extractor = UnstructuredExtractor()

# Extract from PDF
result = extractor.extract("document.pdf")

if result['success']:
    print(f"Extracted text: {result['text'][:100]}...")
    print(f"Found {len(result['tables'])} tables")
    print(f"Found {len(result['images'])} images")
else:
    print(f"Extraction failed: {result['error']}")
```

**Processing Flow:**
```
1. Validate library availability
2. Validate file exists and is readable
3. Call unstructured.partition() with strategy
4. Process returned elements:
   - Categorize as text, table, or image
   - Extract metadata for each element
5. Combine text elements
6. Return standardized output
```

**Error Handling:**
- Returns `success: False` if library not installed
- Returns `success: False` if file doesn't exist
- Returns `success: False` if extraction fails
- All errors logged with traceback

---

### 2. `extract_from_blob(blob, file_extension)`

**Purpose:** Extract content from binary data (from database blob)

**Parameters:**
- `blob` (bytes): Binary file content
- `file_extension` (str): File extension (e.g., '.pdf', '.docx')

**Returns:** Same dict format as `extract()`

**Example:**
```python
from core import DatabaseManager

# Get blob from database
db = DatabaseManager()
blob = db.get_file_blob('abc123hash')

# Extract from blob
extractor = UnstructuredExtractor()
result = extractor.extract_from_blob(blob, '.pdf')

if result['success']:
    print(f"Extracted {result['metadata']['total_elements']} elements")
```

**Processing Flow:**
```
1. Create temporary file from blob
2. Call extract() on temporary file
3. Delete temporary file
4. Return result
```

**Why this method exists:**
Files stored as blobs in database need to be written to temp file before unstructured.io can process them.

---

### 3. `extract_tables_only(file_path)`

**Purpose:** Convenience method to extract only tables

**Parameters:**
- `file_path` (str): Path to file

**Returns:**
```python
list: [
    {
        'text': str,
        'metadata': dict,
        'html': str or None
    },
    ...
]
```

**Example:**
```python
extractor = UnstructuredExtractor()
tables = extractor.extract_tables_only("report.pdf")

for i, table in enumerate(tables):
    print(f"Table {i+1}:")
    print(table['text'])
    if table['html']:
        print(f"HTML: {table['html']}")
```

**Use Case:**
When you only need tables and want to skip processing other content.

---

### 4. `extract_text_only(file_path)`

**Purpose:** Convenience method to extract only text (no tables/images)

**Parameters:**
- `file_path` (str): Path to file

**Returns:** `str` - Extracted text or empty string if failed

**Example:**
```python
extractor = UnstructuredExtractor()
text = extractor.extract_text_only("document.pdf")

print(f"Extracted {len(text)} characters")
print(text[:500])  # First 500 characters
```

**Use Case:**
Simple text extraction without need for tables or images.

---

## Configuration Methods

### 5. `set_strategy(strategy)`

**Purpose:** Change extraction strategy after initialization

**Parameters:**
- `strategy` (str): New strategy ('fast', 'hi_res', 'ocr_only')

**Example:**
```python
extractor = UnstructuredExtractor(strategy="fast")

# Process with fast strategy
result1 = extractor.extract("doc1.pdf")

# Switch to high resolution
extractor.set_strategy("hi_res")

# Process with hi_res strategy
result2 = extractor.extract("doc2.pdf")
```

**Valid Strategies:**
- `"fast"` - Fastest, uses native text when available
- `"hi_res"` - Better quality, more processing time
- `"ocr_only"` - Forces OCR even on native PDFs

---

### 6. `get_supported_formats()`

**Purpose:** Get list of file formats supported by this extractor

**Returns:** `list` of supported file extensions

**Example:**
```python
extractor = UnstructuredExtractor()
formats = extractor.get_supported_formats()

print("Supported formats:")
for fmt in formats:
    print(f"  - {fmt}")
```

**Output:**
```
Supported formats:
  - .pdf
  - .docx
  - .doc
  - .txt
  - .html
  - .xml
  - .pptx
  - .xlsx
  - .csv
  - .tsv
  - .md
  - .rtf
  - .odt
  - .epub
  - .msg
  - .eml
```

---

## Inherited Methods (from BaseExtractor)

### 7. `get_info()`

**Purpose:** Get extractor metadata

**Returns:**
```python
dict: {
    'name': 'unstructured',
    'version': '0.11.6',
    'extraction_count': int,          # Number of successful extractions
    'last_extraction_time': str       # ISO timestamp of last extraction
}
```

**Example:**
```python
extractor = UnstructuredExtractor()

# Do some extractions
extractor.extract("doc1.pdf")
extractor.extract("doc2.pdf")

# Get info
info = extractor.get_info()
print(f"Performed {info['extraction_count']} extractions")
print(f"Last extraction: {info['last_extraction_time']}")
```

---

### 8. `validate_file(file_path)`

**Purpose:** Validate file before extraction

**Parameters:**
- `file_path` (str): Path to file

**Returns:** `tuple: (is_valid: bool, error_message: str or None)`

**Example:**
```python
extractor = UnstructuredExtractor()

is_valid, error = extractor.validate_file("document.pdf")

if is_valid:
    result = extractor.extract("document.pdf")
else:
    print(f"Invalid file: {error}")
```

**Validation Checks:**
- File exists
- Path is a file (not directory)
- File is not empty

---

## Usage Patterns

### Pattern 1: Basic Extraction
```python
from extractors import UnstructuredExtractor

# Initialize
extractor = UnstructuredExtractor()

# Extract
result = extractor.extract("document.pdf")

# Use results
if result['success']:
    print(result['text'])
```

---

### Pattern 2: Extract from Database Blob
```python
from extractors import UnstructuredExtractor
from core import DatabaseManager

# Get file from database
db = DatabaseManager()
file_record = db.get_file_by_hash('abc123')
blob = db.get_file_blob('abc123')

# Extract
extractor = UnstructuredExtractor()
result = extractor.extract_from_blob(
    blob, 
    file_record['file_extension']
)

# Store extracted content
if result['success']:
    db.insert_extracted_content(
        file_hash='abc123',
        content_type='text',
        content_text=result['text'],
        content_json={'tables': result['tables']},
        extractor_name=extractor.name,
        extractor_version=extractor.version
    )
```

---

### Pattern 3: Process Multiple Files
```python
from extractors import UnstructuredExtractor
from utils import FileUtils

# Initialize
extractor = UnstructuredExtractor(strategy="hi_res")

# Get all PDF files
files = FileUtils.list_files(
    "/documents",
    extensions=['.pdf'],
    recursive=True
)

# Process each file
for file_path in files:
    print(f"Processing: {file_path}")
    
    result = extractor.extract(file_path)
    
    if result['success']:
        print(f"  ✓ Extracted {result['metadata']['total_elements']} elements")
    else:
        print(f"  ✗ Failed: {result['error']}")

# Get statistics
info = extractor.get_info()
print(f"\nTotal extractions: {info['extraction_count']}")
```

---

### Pattern 4: Table Extraction Pipeline
```python
from extractors import UnstructuredExtractor
import json

# Initialize with table focus
extractor = UnstructuredExtractor(
    strategy="hi_res",
    infer_table_structure=True,
    extract_images=False  # Don't need images
)

# Extract tables
tables = extractor.extract_tables_only("financial_report.pdf")

# Process tables
for i, table in enumerate(tables):
    # Save table as JSON
    with open(f"table_{i+1}.json", 'w') as f:
        json.dump(table, f, indent=2)
    
    # Save table as HTML (if available)
    if table['html']:
        with open(f"table_{i+1}.html", 'w') as f:
            f.write(table['html'])

print(f"Extracted {len(tables)} tables")
```

---

### Pattern 5: Strategy Comparison
```python
from extractors import UnstructuredExtractor
import time

# Initialize
extractor = UnstructuredExtractor()

strategies = ['fast', 'hi_res', 'ocr_only']
file_path = "complex_document.pdf"

for strategy in strategies:
    extractor.set_strategy(strategy)
    
    start = time.time()
    result = extractor.extract(file_path)
    duration = time.time() - start
    
    print(f"\nStrategy: {strategy}")
    print(f"Duration: {duration:.2f}s")
    print(f"Elements: {result['metadata']['total_elements']}")
    print(f"Tables: {result['metadata']['table_count']}")
```

---

## Integration with Other Components

### With DocumentProcessor
```python
from core import DocumentProcessor
from extractors import UnstructuredExtractor

# Process files
processor = DocumentProcessor(
    file_path="/documents",
    use_unstructured=True
)

# Scan and store files
scan_result = processor.process()

# Get pending files
pending = processor.get_pending_files()

# Extract content from each
extractor = UnstructuredExtractor()

for file_record in pending:
    # Get blob
    blob = processor.get_file_from_blob(file_record['file_hash'])
    
    # Extract
    result = extractor.extract_from_blob(
        blob,
        file_record['file_extension']
    )
    
    # Store results
    if result['success']:
        processor.db.insert_extracted_content(
            file_hash=file_record['file_hash'],
            content_type='full_extraction',
            content_text=result['text'],
            content_json={
                'tables': result['tables'],
                'images': result['images']
            },
            extractor_name=extractor.name,
            extractor_version=extractor.version
        )
```

---

### With Logger
```python
from extractors import UnstructuredExtractor
from utils import Logger

# Create logger
logger = Logger(name="ExtractionPipeline", log_level="DEBUG")

# Initialize extractor with logger
extractor = UnstructuredExtractor(logger=logger)

# Extract (will be logged automatically)
result = extractor.extract("document.pdf")

# Logs will show:
# INFO | Extracting content from: document.pdf
# INFO | [EXTRACTION] document.pdf | Extractor: unstructured | Status: SUCCESS | Elements: 45 | Duration: 2.30s
```

---

## Performance Considerations

### Strategy Impact

| Strategy | Speed | Quality | Best For |
|----------|-------|---------|----------|
| `fast` | ⚡⚡⚡ Fast | ⭐⭐ Medium | Simple documents, native PDFs |
| `hi_res` | ⚡⚡ Medium | ⭐⭐⭐⭐ High | Complex layouts, mixed content |
| `ocr_only` | ⚡ Slow | ⭐⭐⭐ Good | Scanned documents, images |

### Processing Times (Approximate)

- **Simple PDF (10 pages, native text):** 1-3 seconds
- **Complex PDF (50 pages, tables):** 10-30 seconds
- **Scanned PDF (100 pages, OCR):** 60-120 seconds

### Memory Usage

- **Small files (< 1 MB):** ~50-100 MB RAM
- **Medium files (1-10 MB):** ~200-500 MB RAM
- **Large files (> 10 MB):** ~500-1000 MB RAM

---

## Error Handling

### Common Errors

1. **Library Not Available**
```python
result = extractor.extract("file.pdf")
# Returns: {'success': False, 'error': 'unstructured library not available'}
```

2. **File Not Found**
```python
result = extractor.extract("missing.pdf")
# Returns: {'success': False, 'error': 'File does not exist'}
```

3. **Empty File**
```python
result = extractor.extract("empty.pdf")
# Returns: {'success': False, 'error': 'File is empty'}
```

4. **Extraction Failed**
```python
result = extractor.extract("corrupted.pdf")
# Returns: {'success': False, 'error': 'Extraction error: [detailed error]'}
```

### Error Handling Best Practices
```python
extractor = UnstructuredExtractor()

try:
    result = extractor.extract(file_path)
    
    if result['success']:
        # Process successful extraction
        process_content(result['text'])
    else:
        # Handle extraction failure
        logger.error(f"Extraction failed: {result['error']}")
        # Try alternative method or skip
        
except Exception as e:
    # Handle unexpected errors
    logger.exception("Unexpected error during extraction")
```

---

## Limitations

1. **Requires unstructured library** - Must be installed separately
2. **Processing speed** - Hi-res strategy can be slow on large files
3. **OCR accuracy** - Depends on document quality
4. **Table structure** - Complex tables may not parse perfectly
5. **Image extraction** - Only descriptions, not actual image data
6. **Language support** - Best with English, varies with other languages

---

## Dependencies
```python
# Required
from unstructured.partition.auto import partition

# Internal
from .base_extractor import BaseExtractor
from ..utils import FileUtils, Logger
```

---

## File Location

`extractors/unstructured_extractor.py`

---

## Version

1.0.0 (Extractor wrapper version)
Unstructured.io library version: 0.11.6

---

## Last Updated

2025-12-16