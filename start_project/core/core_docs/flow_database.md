┌──────────────────────────────────┐
│  Table 1: processed_files        │
│  -------------------------        │
│  • Raw PDF blob                  │
│  • File hash, path, name         │
│  • Status: pending/completed     │
└────────────┬─────────────────────┘
             │
             ▼
    [Extraction with unstructured.io]
    [Extraction with docling]
    [Extraction with VLM]
             │
             ▼
┌──────────────────────────────────┐
│  Table 2: extracted_content      │
│  ---------------------------      │
│  • Text elements                 │
│  • Tables (as JSON)              │
│  • Images (descriptions)         │
│  • Extractor name & version      │
│  • Can have 50+ rows per file    │
└────────────┬─────────────────────┘
             │
             ▼
       [Chunking Strategy]
       [Add overlap]
       [Add metadata]
             │
             ▼
┌──────────────────────────────────┐
│  Table 3: content_chunks         │
│  ------------------------         │
│  • Chunk text (500 tokens)       │
│  • Chunk index (order)           │
│  • Embedding vector (when ready) │
│  • Used by vector DB             │
│  • Can have 150+ rows per file   │
└──────────────────────────────────┘