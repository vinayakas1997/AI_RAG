# Database Architecture Documentation

## Overview

The database system uses SQLite to manage document processing pipeline with three main tables representing different stages of the RAG (Retrieval Augmented Generation) workflow.

---

## Database Schema

### Architecture Flow
```
┌──────────────────────┐
│  processed_files     │  ← Table 1: Raw file storage
│  (File metadata +    │
│   binary blobs)      │
└──────────┬───────────┘
           │
           ▼ [Extraction: Unstructured/Docling/VLM]
           │
┌──────────────────────┐
│ extracted_content    │  ← Table 2: Structured extraction results
│ (Text, tables,       │
│  images, etc.)       │
└──────────┬───────────┘
           │
           ▼ [Chunking: Break into pieces]
           │
┌──────────────────────┐
│  content_chunks      │  ← Table 3: Vector DB ready chunks
│  (Chunks +           │
│   embeddings)        │
└──────────────────────┘
```

---

## Table Purposes

### Table 1: `processed_files`
**Purpose:** Store raw files and track processing status

**When populated:** Immediately upon file upload/scan

**Stores:**
- Original file as binary blob (immutable)
- File metadata (hash, path, name, size)
- Processing status (pending, processing, completed, failed)
- Extractor configuration used
- Links to downstream extractions

**Use cases:**
- Check if file already processed
- Retrieve original file for reprocessing
- Track which files failed
- Audit trail of all processed documents

---

### Table 2: `extracted_content`
**Purpose:** Store structured content extracted by different tools

**When populated:** After extraction with unstructured.io, docling, or VLM

**Stores:**
- Text elements from documents
- Tables (as structured JSON)
- Image descriptions
- Extractor name and version
- Multiple extraction results per file (comparison)

**Use cases:**
- Compare different extraction methods
- Query specific content types (all tables, all images)
- Debug extraction quality
- Reprocess without re-extracting

**Note:** One file can have 50+ rows (one per element extracted)

---

### Table 3: `content_chunks`
**Purpose:** Store chunked content ready for vector database and RAG

**When populated:** After chunking extracted content

**Stores:**
- Text chunks (typically 500-1000 tokens)
- Chunk sequence/order
- Embedding vectors (added later when model chosen)
- Chunk metadata (page, section, etc.)

**Use cases:**
- RAG retrieval (semantic search)
- Store embeddings from different models
- Experiment with chunking strategies
- Direct integration with vector databases

**Note:** One file can have 150+ rows (many chunks per document)

---

## DatabaseManager Class

### Purpose
Centralized database operations manager providing clean interface for all database interactions.

---

## Functions Reference

### Initialization Functions

#### `__init__(db_path)`
**Purpose:** Initialize database manager and create database file

**Parameters:**
- `db_path` (str): Path to SQLite database file

**Returns:** DatabaseManager instance

**Example:**
```python
db = DatabaseManager("documents.db")
```

---

#### `init_database()`
**Purpose:** Create all tables, indexes, and schema if they don't exist

**Called by:** `__init__()` automatically

**Creates:**
- 3 main tables (processed_files, extracted_content, content_chunks)
- 5 indexes for fast lookups
- Foreign key relationships

**Example:**
```python
db.init_database()  # Usually automatic
```

---

### Connection Management

#### `get_connection()`
**Purpose:** Get SQLite database connection

**Returns:** sqlite3.Connection object

**Use case:** For custom queries not covered by provided methods

**Example:**
```python
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM processed_files LIMIT 10")
conn.close()
```

---

### File Management Functions (Table 1)

#### `insert_file(...)`
**Purpose:** Store new file in database with metadata and blob

**Parameters:**
- `file_hash` (str): MD5 hash of file (unique identifier)
- `file_path` (str): Original file path
- `file_name` (str): File name
- `file_extension` (str): Extension (.pdf, .txt, etc.)
- `file_size` (int): Size in bytes
- `file_blob` (bytes): Binary file content
- `model_used` (str, optional): VLM model name if used
- `extractor_used` (str, optional): Extractor name ('unstructured', 'docling', 'vlm')
- `use_unstructured` (bool): Flag for unstructured.io usage
- `use_docling` (bool): Flag for docling usage
- `status` (str): Processing status (default: 'pending')
- `metadata` (dict, optional): Additional metadata as dictionary

**Returns:** bool (True if successful)

**Example:**
```python
with open('document.pdf', 'rb') as f:
    blob = f.read()

success = db.insert_file(
    file_hash='abc123',
    file_path='/docs/document.pdf',
    file_name='document.pdf',
    file_extension='.pdf',
    file_size=1024000,
    file_blob=blob,
    extractor_used='unstructured',
    use_unstructured=True,
    status='pending'
)
```

---

#### `get_file_by_hash(file_hash)`
**Purpose:** Retrieve file metadata (without blob) by hash

**Parameters:**
- `file_hash` (str): MD5 hash of file

**Returns:** dict or None with file metadata

**Example:**
```python
file_info = db.get_file_by_hash('abc123')
if file_info:
    print(f"Status: {file_info['status']}")
    print(f"Chunks: {file_info['chunk_count']}")
```

---

#### `get_file_blob(file_hash)`
**Purpose:** Retrieve original file binary content

**Parameters:**
- `file_hash` (str): MD5 hash of file

**Returns:** bytes or None (file binary content)

**Use case:** Reprocessing file with different extractor without re-upload

**Example:**
```python
blob = db.get_file_blob('abc123')
if blob:
    # Save to temporary file for reprocessing
    with open('temp.pdf', 'wb') as f:
        f.write(blob)
```

---

#### `update_file_status(file_hash, status, error_message, chunk_count)`
**Purpose:** Update processing status of file

**Parameters:**
- `file_hash` (str): MD5 hash of file
- `status` (str): New status ('pending', 'processing', 'completed', 'failed')
- `error_message` (str, optional): Error message if failed
- `chunk_count` (int, optional): Number of chunks created

**Returns:** bool (True if successful)

**Example:**
```python
# Mark as processing
db.update_file_status('abc123', 'processing')

# Mark as completed with chunk count
db.update_file_status('abc123', 'completed', chunk_count=150)

# Mark as failed with error
db.update_file_status('abc123', 'failed', error_message='Extraction failed')
```

---

#### `get_all_files_by_status(status)`
**Purpose:** Get all files with specific processing status

**Parameters:**
- `status` (str): Status to filter by

**Returns:** list of dicts (file records)

**Use case:** Find files that need reprocessing or are pending

**Example:**
```python
# Get all failed files
failed = db.get_all_files_by_status('failed')
for file in failed:
    print(f"Failed: {file['file_name']}")

# Get all pending files
pending = db.get_all_files_by_status('pending')
```

---

### Extracted Content Functions (Table 2)

#### `insert_extracted_content(...)`
**Purpose:** Store content extracted by unstructured.io, docling, or VLM

**Parameters:**
- `file_hash` (str): MD5 hash of source file
- `content_type` (str): Type of content ('text', 'table', 'image', 'diagram')
- `content_text` (str, optional): Plain text content
- `content_json` (dict, optional): Structured content (tables as JSON)
- `extractor_name` (str, optional): Name of extractor used
- `extractor_version` (str, optional): Version of extractor

**Returns:** bool (True if successful)

**Use case:** Store each extracted element separately

**Example:**
```python
# Store extracted text
db.insert_extracted_content(
    file_hash='abc123',
    content_type='text',
    content_text='Chapter 1: Introduction...',
    extractor_name='unstructured',
    extractor_version='0.11.6'
)

# Store extracted table
db.insert_extracted_content(
    file_hash='abc123',
    content_type='table',
    content_json={'headers': [...], 'rows': [...]},
    extractor_name='unstructured'
)
```

---

#### `get_extracted_content(file_hash)`
**Purpose:** Get all extracted content for a specific file

**Parameters:**
- `file_hash` (str): MD5 hash of file

**Returns:** list of dicts (all extracted content records)

**Use case:** Review what was extracted, compare extractors

**Example:**
```python
content = db.get_extracted_content('abc123')
for item in content:
    print(f"Type: {item['content_type']}")
    print(f"Extractor: {item['extractor_name']}")
    if item['content_type'] == 'table':
        print(f"Table data: {item['content_json']}")
```

---

### Chunk Management Functions (Table 3)

#### `insert_chunk(...)`
**Purpose:** Store chunked content ready for vector database

**Parameters:**
- `chunk_id` (str): Unique chunk identifier
- `file_hash` (str): MD5 hash of source file
- `chunk_index` (int): Index of chunk in sequence (0, 1, 2, ...)
- `chunk_text` (str): Text content of chunk
- `chunk_metadata` (dict, optional): Additional metadata (page, section, etc.)
- `embedding_vector` (bytes, optional): Embedding vector as binary

**Returns:** bool (True if successful)

**Example:**
```python
# Store chunk without embedding
db.insert_chunk(
    chunk_id='abc123_chunk_0',
    file_hash='abc123',
    chunk_index=0,
    chunk_text='Introduction to motor systems...',
    chunk_metadata={'page': 1, 'section': 'Introduction'}
)

# Store chunk with embedding
db.insert_chunk(
    chunk_id='abc123_chunk_1',
    file_hash='abc123',
    chunk_index=1,
    chunk_text='Maintenance procedures...',
    embedding_vector=embedding_bytes
)
```

---

#### `get_chunks_by_file(file_hash)`
**Purpose:** Get all chunks for a specific file

**Parameters:**
- `file_hash` (str): MD5 hash of file

**Returns:** list of dicts (chunk records in order)

**Use case:** Retrieve all chunks for RAG, regenerate embeddings

**Example:**
```python
chunks = db.get_chunks_by_file('abc123')
print(f"Total chunks: {len(chunks)}")
for chunk in chunks:
    print(f"Chunk {chunk['chunk_index']}: {chunk['chunk_text'][:100]}...")
```

---

### Statistics & Utility Functions

#### `get_statistics()`
**Purpose:** Get database statistics and overview

**Returns:** dict with statistics

**Statistics included:**
- Total files processed
- Files by status (pending, completed, failed)
- Total storage size
- Total chunks created

**Example:**
```python
stats = db.get_statistics()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']} MB")
print(f"Completed: {stats['status_counts'].get('completed', 0)}")
print(f"Total chunks: {stats['total_chunks']}")
```

---

#### `delete_file(file_hash)`
**Purpose:** Delete file and all associated data (cascading delete)

**Parameters:**
- `file_hash` (str): MD5 hash of file

**Returns:** bool (True if successful)

**Deletes:**
- File record from processed_files
- All extracted content from extracted_content
- All chunks from content_chunks

**Example:**
```python
# Delete file and all related data
success = db.delete_file('abc123')
if success:
    print("File and all related data deleted")
```

---

## Typical Workflow

### 1. File Upload
```python
db = DatabaseManager("documents.db")

# Store file
with open('manual.pdf', 'rb') as f:
    blob = f.read()

db.insert_file(
    file_hash='abc123',
    file_path='manual.pdf',
    file_name='manual.pdf',
    file_extension='.pdf',
    file_size=len(blob),
    file_blob=blob,
    status='pending'
)
```

### 2. Extraction
```python
# Update status
db.update_file_status('abc123', 'processing')

# Extract content with unstructured
# ... extraction code ...

# Store extracted content
db.insert_extracted_content(
    file_hash='abc123',
    content_type='text',
    content_text=extracted_text,
    extractor_name='unstructured'
)

# Mark as completed
db.update_file_status('abc123', 'completed')
```

### 3. Chunking
```python
# Get extracted content
content = db.get_extracted_content('abc123')

# Chunk content
# ... chunking code ...

# Store chunks
for i, chunk in enumerate(chunks):
    db.insert_chunk(
        chunk_id=f'abc123_chunk_{i}',
        file_hash='abc123',
        chunk_index=i,
        chunk_text=chunk
    )

# Update chunk count
db.update_file_status('abc123', 'completed', chunk_count=len(chunks))
```

### 4. Embeddings (Later)
```python
# Get chunks
chunks = db.get_chunks_by_file('abc123')

# Generate embeddings
# ... embedding code ...

# Update chunks with embeddings (requires custom UPDATE query)
```

---

## Status Values

| Status | Meaning |
|--------|---------|
| `pending` | File stored, awaiting extraction |
| `processing` | Currently being processed |
| `completed` | Successfully processed and chunked |
| `failed` | Processing failed (see error_message) |

---

## Best Practices

### 1. Always check if file exists before inserting
```python
existing = db.get_file_by_hash(file_hash)
if existing:
    print("File already processed")
else:
    db.insert_file(...)
```

### 2. Update status at each stage
```python
db.update_file_status(file_hash, 'processing')
# ... do work ...
db.update_file_status(file_hash, 'completed')
```

### 3. Store extraction errors
```python
try:
    # extraction code
except Exception as e:
    db.update_file_status(
        file_hash,
        'failed',
        error_message=str(e)
    )
```

### 4. Use transactions for bulk inserts
```python
conn = db.get_connection()
try:
    for chunk in chunks:
        db.insert_chunk(...)
    conn.commit()
except:
    conn.rollback()
finally:
    conn.close()
```

---

## Schema Details

### Indexes
- `idx_file_path` - Fast lookup by file path
- `idx_file_hash` - Fast lookup by hash
- `idx_status` - Fast filtering by status
- `idx_extracted_file_hash` - Fast lookup of extracted content
- `idx_chunks_file_hash` - Fast lookup of chunks

### Foreign Keys
- `extracted_content.file_hash` → `processed_files.file_hash`
- `content_chunks.file_hash` → `processed_files.file_hash`

---

## File Location
`core/database.py`

## Dependencies
- `sqlite3` (Python standard library)
- `json` (Python standard library)

---

## Version
1.0.0

## Last Updated
2024-12-16