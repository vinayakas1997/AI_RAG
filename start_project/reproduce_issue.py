
import sys
import os
import json

# Add extractors directory to path to allow direct import
# sys.path.append(os.path.abspath(r"c:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\extractors"))
# sys.path.append(os.path.abspath(r"c:\Users\106761\Desktop\3_AI_RAG_PROJECT\start_project\utils")) # For logger likely needed by base_extractor/utils imports

os.environ['NO_PROXY'] = 'localhost,127.0.0.1,huggingface.co'
os.environ['HF_HUB_OFFLINE'] = '1'

from extractors import UnstructuredExtractor

def test_extraction():
    file_path = r"C:\Users\106761\Desktop\Rag_Test_Files\下野部工場\02AC001：下野部工場　機密区域管理要領\02AC001(1)：下野部工場　機密区域管理要領.pdf"
    
    print(f"Testing extraction on: {file_path}")
    
    # Initialize with Japanese and English
    extractor = UnstructuredExtractor(
        strategy="hi_res",
        languages=['jpn', 'eng']
    )
    
    # Extract
    result = extractor.extract(file_path)
    
    if result['success']:
        print("Extraction Successful")
        print(f"Total elements: {result['metadata']['total_elements']}")
        
        # Check tables
        print(f"Tables found: {len(result['tables'])}")
        for i, table in enumerate(result['tables']):
            meta = table.get('metadata', {})
            langs = meta.get('languages', [])
            print(f"Table {i+1} languages: {langs}")
            print(f"Table {i+1} text start: {table['text'][:50]}...")
            
    else:
        print(f"Extraction Failed: {result.get('error')}")

if __name__ == "__main__":
    test_extraction()
