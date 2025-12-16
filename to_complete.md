data_ingestion/
│
├── core/
│   ├── __init__.py
│   ├── document_processor.py      # File management ONLY
│   └── database.py                 # Database operations
│
├── extractors/
│   ├── __init__.py
│   ├── base_extractor.py          # Abstract base class
│   ├── unstructured_extractor.py  # Unstructured.io
│   ├── docling_extractor.py       # Docling
│   └── vlm_processor.py           # Vision models
│
├── processors/
│   ├── __init__.py
│   ├── chunker.py                 # Content chunking
│   └── embedding_generator.py     # Embeddings
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py              # File operations
│   └── logger.py                  # Logging
│
└── main.py                        # Orchestration