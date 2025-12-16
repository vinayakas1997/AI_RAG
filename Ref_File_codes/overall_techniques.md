### RAG Pipeline Steps and Associated Techniques

The Retrieval-Augmented Generation (RAG) pipeline typically consists of the following steps: (1) Document Ingestion/Preprocessing, (2) Chunking, (3) Embedding, (4) Indexing/Storage, (5) Retrieval, (6) Reranking (optional), and (7) Generation/Post-processing. Below, I list relevant techniques from the provided folder, prefixed by their file names. Each technique is described briefly, with notes on whether it's considered "new" (recently proposed or innovative) or "better" (an improvement over basic RAG, based on the descriptions in the files). These are advanced methods that enhance performance, relevance, or efficiency compared to simple RAG (e.g., basic vector retrieval).

#### 1. Document Ingestion/Preprocessing
Techniques for loading, cleaning, and preparing multi-modal or structured data (e.g., PDFs, CSVs, images).
- **multi_model_rag_with_captioning.ipynb**: Multi-modal RAG with image captioning using Gemini for summarizing visuals in PDFs. (Better: Handles multi-modal data for richer context.)
- **multi_model_rag_with_colpali.ipynb**: Multi-modal RAG using ColPali for processing images and text in PDFs. (New/Better: Leverages vision-language models for advanced document understanding.)
- **simple_csv_rag.ipynb**: Basic RAG for CSV files using LangChain. (Better: Extends RAG to structured tabular data.)
- **simple_csv_rag_with_llamaindex.ipynb**: CSV RAG using LlamaIndex for structured data processing. (Better: Improved handling of tabular data with indexing.)

#### 2. Chunking
Methods for splitting documents into meaningful units, improving retrieval granularity.
- **choose_chunk_size.ipynb**: Evaluates optimal chunk sizes for RAG performance. (Better: Data-driven approach to chunking for balanced context and precision.)
- **semantic_chunking.ipynb**: Semantic chunking using embeddings to split at natural breakpoints. (New/Better: Preserves semantic coherence over fixed-size chunks.)
- **proposition_chunking.ipynb**: Breaks text into atomic, factual propositions for finer retrieval. (New/Better: Enables precise, fact-based retrieval with quality checks.)
- **contextual_chunk_headers.ipynb**: Adds document-level context (e.g., titles, summaries) to chunks. (Better: Enhances chunk relevance by providing higher-level context.)

#### 3. Embedding
Techniques for generating vector representations of text or queries.
- **HyPE_Hypothetical_Prompt_Embeddings.ipynb**: Generates hypothetical questions per chunk for multi-vector embedding. (New/Better: Improves query alignment by precomputing diverse representations.)
- **HyDe_Hypothetical_Document_Embedding.ipynb**: Expands queries into hypothetical documents for embedding. (New/Better: Bridges query-document style mismatch for better retrieval.)

#### 4. Indexing/Storage
Advanced storage structures for efficient retrieval, beyond basic vector stores.
- **hierarchical_indices.ipynb**: Hierarchical indexing with document summaries and chunks. (Better: Enables multi-level retrieval for large documents.)
- **graph_rag.ipynb**: Graph-based indexing using knowledge graphs for entity relationships. (New/Better: Supports complex, multi-hop queries via graph traversal.)
- **graphrag_with_milvus_vectordb.ipynb**: Graph RAG with Milvus vector database for scalable graph operations. (New/Better: Combines graphs and vectors for efficient, distributed storage.)
- **Microsoft_GraphRag.ipynb**: Microsoft's GraphRAG for knowledge graph-enhanced indexing. (New/Better: Enterprise-scale graph integration for global sensemaking.)

#### 5. Retrieval
Core retrieval methods, often with enhancements for relevance or diversity.
- **adaptive_retrieval.ipynb**: Adaptive retrieval based on query type (e.g., factual vs. analytical). (New/Better: Dynamically adjusts strategy for query-specific needs.)
- **Agentic_RAG.ipynb**: Agentic RAG with query reformulation and multi-turn reasoning. (New/Better: Autonomous query processing for complex tasks.)
- **contextual_compression.ipynb**: Compresses retrieved documents to focus on relevant parts. (Better: Reduces noise by extracting key context.)
- **context_enrichment_window_around_chunk.ipynb**: Adds surrounding context to retrieved chunks. (Better: Improves coherence by expanding chunk windows.)
- **context_enrichment_window_around_chunk_with_llamaindex.ipynb**: Context enrichment using LlamaIndex's SentenceWindowNodeParser. (Better: Automated context expansion for better understanding.)
- **crag.ipynb**: Corrective RAG with web search fallback for low-relevance retrievals. (New/Better: Self-corrects retrieval failures with external knowledge.)
- **dartboard.ipynb**: Dartboard RAG for balanced relevance-diversity retrieval. (New/Better: Optimizes for both relevant and varied results.)
- **document_augmentation.ipynb**: Augments documents with generated questions for retrieval. (Better: Enhances document representation for query matching.)
- **explainable_retrieval.ipynb**: Provides explanations for why documents were retrieved. (Better: Increases transparency and trust in results.)
- **fusion_retrieval.ipynb**: Combines vector and BM25 retrieval for hybrid search. (Better: Leverages strengths of semantic and keyword-based methods.)
- **fusion_retrieval_with_llamaindex.ipynb**: Fusion retrieval using LlamaIndex for hybrid search. (Better: Integrated hybrid approach for improved accuracy.)
- **raptor.ipynb**: RAPTOR with hierarchical summarization and tree-based retrieval. (New/Better: Scales to large corpora with multi-level abstraction.)
- **relevant_segment_extraction.ipynb**: Extracts contiguous, relevant segments from documents. (New/Better: Reconstructs coherent sections for better context.)
- **retrieval_with_feedback_loop.ipynb**: Retrieval with user feedback for continuous improvement. (New/Better: Adapts over time based on user input.)
- **self_rag.ipynb**: Self-RAG with dynamic retrieval decisions and quality checks. (New/Better: Self-evaluates and corrects for reliability.)
- **simple_rag.ipynb**: Basic vector-based retrieval. (Baseline: Standard RAG for comparison.)
- **simple_rag_with_llamaindex.ipynb**: Basic RAG using LlamaIndex. (Baseline: Improved baseline with modular framework.)

#### 6. Reranking (Optional)
Post-retrieval refinement to reorder results for better relevance.
- **reranking.ipynb**: LLM and cross-encoder-based reranking techniques. (Better: Improves top-k results by reassessing relevance.)
- **reranking_with_llamaindex.ipynb**: Reranking using LlamaIndex's post-processors. (Better: Integrated reranking for enhanced accuracy.)

#### 7. Generation/Post-processing
Enhancements to query processing or response generation.
- **query_transformations.ipynb**: Query rewriting, step-back prompting, and sub-query decomposition. (Better: Transforms queries for more effective retrieval.)
- **reliable_rag.ipynb**: Reliable RAG with hallucination checks and document verification. (Better: Adds safeguards for factual accuracy.)

These techniques represent advancements over basic RAG, focusing on scalability, multi-modality, explainability, and robustness. Many are "new" (proposed in recent papers, e.g., 2023-2024) and "better" due to empirical improvements in benchmarks like KITE or FinanceBench. For implementation details, refer to the individual notebook files. If you need deeper explanations or code examples for specific techniques, let me know!