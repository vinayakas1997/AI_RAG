-> Cannot close object, library is destroyed. This may cause a memory leak!
(.venv) PS C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project> python .\test_docling.py
============================================================
Testing DoclingExtractor
============================================================

Extracting: 02AC001(1)：下野部工場　機密区域管理要領.pdf
INFO     | Extracting content from: 02AC001(1)：下野部工場　機密区域管理要領.pdf
2025-12-16 17:28:22,792 - INFO - Extracting content from: 02AC001(1)：下野部工場　機密区域管理要領.pdf
2025-12-16 17:28:22,799 - INFO - detected formats: [<InputFormat.PDF: 'pdf'>]
2025-12-16 17:28:22,896 - INFO - Going to convert document batch...
2025-12-16 17:28:22,897 - INFO - Initializing pipeline for StandardPdfPipeline with options hash e15bc6f248154cc62f8db15ef18a8ab7
2025-12-16 17:28:22,938 - INFO - Loading plugin 'docling_defaults'
2025-12-16 17:28:22,941 - INFO - Registered picture descriptions: ['vlm', 'api']
2025-12-16 17:28:22,986 - INFO - Loading plugin 'docling_defaults'
2025-12-16 17:28:22,993 - INFO - Registered ocr engines: ['auto', 'easyocr', 'ocrmac', 'rapidocr', 'tesserocr', 'tesseract']
2025-12-16 17:28:23,256 - INFO - Accelerator device: 'cpu'
[INFO] 2025-12-16 17:28:23,267 [RapidOCR] base.py:22: Using engine_name: onnxruntime
[INFO] 2025-12-16 17:28:23,276 [RapidOCR] download_file.py:60: File exists and is valid: C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\rapidocr\models\ch_PP-OCRv4_det_infer.onnx
[INFO] 2025-12-16 17:28:23,276 [RapidOCR] main.py:53: Using C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\rapidocr\models\ch_PP-OCRv4_det_infer.onnx
[INFO] 2025-12-16 17:28:23,365 [RapidOCR] base.py:22: Using engine_name: onnxruntime
[INFO] 2025-12-16 17:28:23,367 [RapidOCR] download_file.py:60: File exists and is valid: C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\rapidocr\models\ch_ppocr_mobile_v2.0_cls_infer.onnx
[INFO] 2025-12-16 17:28:23,368 [RapidOCR] main.py:53: Using C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\rapidocr\models\ch_ppocr_mobile_v2.0_cls_infer.onnx
[INFO] 2025-12-16 17:28:23,449 [RapidOCR] base.py:22: Using engine_name: onnxruntime
[INFO] 2025-12-16 17:28:23,595 [RapidOCR] download_file.py:60: File exists and is valid: C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\rapidocr\models\ch_PP-OCRv4_rec_infer.onnx
[INFO] 2025-12-16 17:28:23,661 [RapidOCR] main.py:53: Using C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\rapidocr\models\ch_PP-OCRv4_rec_infer.onnx
2025-12-16 17:28:23,920 - INFO - Auto OCR model selected rapidocr with onnxruntime.
2025-12-16 17:28:24,042 - INFO - Loading plugin 'docling_defaults'
2025-12-16 17:28:24,048 - INFO - Registered layout engines: ['docling_layout_default', 'docling_experimental_table_crops_layout']
2025-12-16 17:28:24,059 - INFO - Accelerator device: 'cpu'
ERROR    | Extraction failed: Missing model config file: C:\Users\106761\.cache\huggingface\hub\models--docling-project--docling-layout-heron\snapshots\bdb7099d742220552d703932cc0ce0a26a7a8da8\config.json
Traceback (most recent call last):
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\extractors\docling_extractor.py", line 101, in extract
    result = converter.convert(file_path)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\pydantic\_internal\_validate_call.py", line 39, in wrapper_function
    return wrapper(*args, **kwargs)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\pydantic\_internal\_validate_call.py", line 136, in __call__
    res = self.__pydantic_validator__.validate_python(pydantic_core.ArgsKwargs(args, kwargs))
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 265, in convert
    return next(all_res)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 288, in convert_all
    for conv_res in conv_res_iter:
                    ^^^^^^^^^^^^^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 364, in _convert
    for item in map(
                ~~~^
        process_func,
        ^^^^^^^^^^^^^
        input_batch,
        ^^^^^^^^^^^^
    ):
    ^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 411, in _process_document
    conv_res = self._execute_pipeline(in_doc, raises_on_error=raises_on_error)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 432, in _execute_pipeline
    pipeline = self._get_pipeline(in_doc.format)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 394, in _get_pipeline
    self.initialized_pipelines[cache_key] = pipeline_class(
                                            ~~~~~~~~~~~~~~^
        pipeline_options=pipeline_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\pipeline\standard_pdf_pipeline.py", line 422, in __init__
    self._init_models()
    ~~~~~~~~~~~~~~~~~^^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\pipeline\standard_pdf_pipeline.py", line 444, in _init_models
    self.layout_model = layout_factory.create_instance(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        options=self.pipeline_options.layout_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        artifacts_path=art_path,
        ^^^^^^^^^^^^^^^^^^^^^^^^
        accelerator_options=self.pipeline_options.accelerator_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\models\factories\base_factory.py", line 57, in create_instance
    return _cls(options=options, **kwargs)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\models\layout_model.py", line 83, in __init__
    self.layout_predictor = LayoutPredictor(
                            ~~~~~~~~~~~~~~~^
        artifact_path=str(artifacts_path),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        device=device,
        ^^^^^^^^^^^^^^
        num_threads=accelerator_options.num_threads,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling_ibm_models\layoutmodel\layout_predictor.py", line 77, in __init__
    raise FileNotFoundError(f"Missing model config file: {self._model_config}")
FileNotFoundError: Missing model config file: C:\Users\106761\.cache\huggingface\hub\models--docling-project--docling-layout-heron\snapshots\bdb7099d742220552d703932cc0ce0a26a7a8da8\config.json
2025-12-16 17:29:48,402 - ERROR - Extraction failed: Missing model config file: C:\Users\106761\.cache\huggingface\hub\models--docling-project--docling-layout-heron\snapshots\bdb7099d742220552d703932cc0ce0a26a7a8da8\config.json
Traceback (most recent call last):
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\extractors\docling_extractor.py", line 101, in extract
    result = converter.convert(file_path)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\pydantic\_internal\_validate_call.py", line 39, in wrapper_function
    return wrapper(*args, **kwargs)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\pydantic\_internal\_validate_call.py", line 136, in __call__
    res = self.__pydantic_validator__.validate_python(pydantic_core.ArgsKwargs(args, kwargs))
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 265, in convert
    return next(all_res)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 288, in convert_all
    for conv_res in conv_res_iter:
                    ^^^^^^^^^^^^^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 364, in _convert
    for item in map(
                ~~~^
        process_func,
        ^^^^^^^^^^^^^
        input_batch,
        ^^^^^^^^^^^^
    ):
    ^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 411, in _process_document
    conv_res = self._execute_pipeline(in_doc, raises_on_error=raises_on_error)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 432, in _execute_pipeline
    pipeline = self._get_pipeline(in_doc.format)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\document_converter.py", line 394, in _get_pipeline
    self.initialized_pipelines[cache_key] = pipeline_class(
                                            ~~~~~~~~~~~~~~^
        pipeline_options=pipeline_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\pipeline\standard_pdf_pipeline.py", line 422, in __init__
    self._init_models()
    ~~~~~~~~~~~~~~~~~^^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\pipeline\standard_pdf_pipeline.py", line 444, in _init_models
    self.layout_model = layout_factory.create_instance(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        options=self.pipeline_options.layout_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        artifacts_path=art_path,
        ^^^^^^^^^^^^^^^^^^^^^^^^
        accelerator_options=self.pipeline_options.accelerator_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\models\factories\base_factory.py", line 57, in create_instance
    return _cls(options=options, **kwargs)
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling\models\layout_model.py", line 83, in __init__
    self.layout_predictor = LayoutPredictor(
                            ~~~~~~~~~~~~~~~^
        artifact_path=str(artifacts_path),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        device=device,
        ^^^^^^^^^^^^^^
        num_threads=accelerator_options.num_threads,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\.venv\Lib\site-packages\docling_ibm_models\layoutmodel\layout_predictor.py", line 77, in __init__
    raise FileNotFoundError(f"Missing model config file: {self._model_config}")
FileNotFoundError: Missing model config file: C:\Users\106761\.cache\huggingface\hub\models--docling-project--docling-layout-heron\snapshots\bdb7099d742220552d703932cc0ce0a26a7a8da8\config.json

✗ Extraction failed: Extraction error: Missing model config file: C:\Users\106761\.cache\huggingface\hub\models--docling-project--docling-layout-heron\snapshots\bdb7099d742220552d703932cc0ce0a26a7a8da8\config.json
-> Cannot close object, library is destroyed. This may cause a memory leak!
(.venv) PS C:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project> git status
