"""
Test script for VLMProcessor with visualization
"""

import sys
import os
sys.path.insert(0, os.path.abspath('..'))  # Add parent directory to path


from extractors import VLMProcessor
from utils import FileUtils, PDFVisualizer
import os

if __name__ == "__main__":
    file_path = "test_pdf.pdf"
    
    print("=" * 60)
    print("Testing VLMProcessor")
    print("=" * 60)
    
    # Initialize VLM Processor
    extractor = VLMProcessor(
        model_name="qwen3-vl:latest",
        ollama_host="http://localhost:11434",
        auto_pull=True,
        timeout=300
    )
    
    # Check if available
    if not extractor.available:
        print("\n✗ VLM Processor not available!")
        print("\nPossible issues:")
        print("  1. Ollama not running → Start with: ollama serve")
        print("  2. Model not available → Will auto-download if Ollama is running")
        print("  3. PIL not installed → pip install Pillow")
        print("  4. PyMuPDF not installed → pip install PyMuPDF")
        exit(1)

    # Extract from PDF
    print(f"\nExtracting: {os.path.basename(file_path)}")
    print("⚠️  This may take several minutes (VLM processes each page)...")
    
    result = extractor.extract(file_path=file_path)

    if result['success']:
        print(f"\n✓ Extraction successful!")
        print(f"Extracted text (first 200 chars): {result['text'][:200]}...")
        print(f"Total pages processed: {result['metadata']['pages_processed']}")
        print(f"Duration: {result['metadata']['duration_seconds']:.2f}s")
        
        # Show per-page info
        if 'pages_data' in result['metadata']:
            print(f"\nPer-page details:")
            for page_data in result['metadata']['pages_data']:
                print(f"  Page {page_data['page_number']}: {page_data['tokens_used']} tokens, {len(page_data['text'])} chars")
        
        # Save extraction results
        print(f"\n{'=' * 60}")
        print("Saving extraction results...")
        print("=" * 60)
        
        save_result = FileUtils.save_extraction_results(
            result=result,
            output_dir="extraction_results/vlm",
            file_name=os.path.splitext(os.path.basename(file_path))[0]
        )
        
        if save_result['success']:
            print("\n✓ Results saved successfully!")
            print(f"\nOutput directory: {save_result['output_dir']}")
            print(f"\nSaved files:")
            for key, path in save_result['saved_files'].items():
                print(f"  • {key}: {os.path.basename(path)}")
        
        # Visualize extraction (VLM doesn't provide coordinates, so this will show the limitation)
        print(f"\n{'=' * 60}")
        print("Visualization (Note: VLM doesn't provide coordinates)")
        print("=" * 60)
        
        visualizer = PDFVisualizer()
        
        if not visualizer.available:
            print("✗ Visualizer not available (missing PyMuPDF or Pillow)")
        else:
            viz_result = visualizer.visualize_extraction(
                pdf_path=file_path,
                extraction_result=result,
                show_labels=True,
                opacity=0.3
            )
            
            if viz_result['success']:
                print(f"✓ Annotated PDF created!")
                print(f"  Output: {viz_result['output_path']}")
            else:
                print(f"⚠️  Visualization skipped: {viz_result['error']}")
                print(f"  (This is expected - VLM extracts text but doesn't provide coordinates)")
            
            # Export pages as images (original pages)
            print(f"\nExporting original PDF pages as images...")
            img_result = visualizer.export_as_images(
                pdf_path=file_path,
                extraction_result=result,
                dpi=150
            )
            
            if img_result['success']:
                print(f"✓ Images exported!")
                print(f"  Output directory: {img_result['output_dir']}")
                print(f"  Total pages: {img_result['page_count']}")
        
        print(f"\n{'=' * 60}")
        print("TEST COMPLETE!")
        print("=" * 60)
        print(f"\n📁 Check these directories:")
        if save_result['success']:
            print(f"  • VLM results: {save_result['output_dir']}")
        if img_result and img_result.get('success'):
            print(f"  • Page images: {img_result['output_dir']}")
        
        print(f"\n💡 VLM Advantages:")
        print(f"  ✓ Understands visual layout (flowcharts, diagrams)")
        print(f"  ✓ Handles complex documents")
        print(f"  ✓ Can describe images and graphics")
        print(f"\n⚠️  VLM Limitations:")
        print(f"  • Slower than traditional extractors")
        print(f"  • No coordinate information")
        print(f"  • Requires Ollama server running")
    else:
        print(f"\n✗ Extraction failed: {result['error']}")