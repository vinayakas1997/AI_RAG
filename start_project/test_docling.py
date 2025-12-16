"""
Test script for DoclingExtractor with visualization
"""


from extractors import DoclingExtractor
from utils import FileUtils, PDFVisualizer
import os

os.environ['NO_PROXY'] = 'localhost,127.0.0.1,huggingface.co'
os.environ['HF_HUB_OFFLINE'] = '0'

if __name__ == "__main__":
    file_path = r"C:\Users\106761\Desktop\Rag_Test_Files\下野部工場\02AC001：下野部工場　機密区域管理要領\02AC001(1)：下野部工場　機密区域管理要領.pdf"
    
    print("=" * 60)
    print("Testing DoclingExtractor")
    print("=" * 60)
    
    # Initialize with Japanese
    extractor = DoclingExtractor(
        extract_tables=True,
        extract_images=True,
        languages=['jpn', 'eng']
    )
    
    # Check if available
    if not extractor.available:
        print("\n✗ Docling library not installed!")
        print("Install with: pip install docling")
        exit(1)

    # Extract from PDF
    print(f"\nExtracting: {os.path.basename(file_path)}")
    result = extractor.extract(file_path=file_path)

    if result['success']:
        print(f"\n✓ Extraction successful!")
        print(f"Extracted text: {result['text'][:100]}...")
        print(f"Found {len(result['tables'])} tables")
        print(f"Found {len(result['images'])} images")
        print(f"Duration: {result['metadata']['duration_seconds']:.2f}s")
        
        # Save extraction results
        print(f"\n{'=' * 60}")
        print("Saving extraction results...")
        print("=" * 60)
        
        save_result = FileUtils.save_extraction_results(
            result=result,
            output_dir="extraction_results/docling",
            file_name=os.path.splitext(os.path.basename(file_path))[0]
        )
        
        if save_result['success']:
            print("\n✓ Results saved successfully!")
            print(f"\nOutput directory: {save_result['output_dir']}")
            print(f"\nSaved files:")
            for key, path in save_result['saved_files'].items():
                print(f"  • {key}: {os.path.basename(path)}")
        
        # Visualize extraction (if coordinates available)
        print(f"\n{'=' * 60}")
        print("Creating annotated PDF...")
        print("=" * 60)
        
        visualizer = PDFVisualizer()
        
        if not visualizer.available:
            print("✗ Visualizer not available (missing PyMuPDF or Pillow)")
            print("  Install with: pip install PyMuPDF Pillow")
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
                print(f"  Pages processed: {viz_result['pages_processed']}")
                print(f"  Total elements: {viz_result['total_elements']}")
            else:
                print(f"✗ Visualization failed: {viz_result['error']}")
            
            # Export as images
            print(f"\nExporting pages as annotated images...")
            img_result = visualizer.export_as_images(
                pdf_path=file_path,
                extraction_result=result,
                dpi=150
            )
            
            if img_result['success']:
                print(f"✓ Images exported!")
                print(f"  Output directory: {img_result['output_dir']}")
                print(f"  Total pages: {img_result['page_count']}")
            else:
                print(f"✗ Image export failed: {img_result['error']}")
            
            # Statistics
            print(f"\n{'=' * 60}")
            print("Element Statistics")
            print("=" * 60)
            stats = visualizer.generate_statistics(result)
            
            print(f"  Total elements: {stats['total_elements']}")
            print(f"  With coordinates: {stats['with_coordinates']}")
            print(f"  Without coordinates: {stats['without_coordinates']}")
            
            if stats['by_type']:
                print(f"\n  Elements by type:")
                for elem_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
                    print(f"    {elem_type}: {count}")
        
        print(f"\n{'=' * 60}")
        print("TEST COMPLETE!")
        print("=" * 60)
        print(f"\n📁 Check these directories:")
        if save_result['success']:
            print(f"  • Text results: {save_result['output_dir']}")
        if viz_result.get('success'):
            print(f"  • Annotated PDF: {os.path.dirname(viz_result['output_path'])}")
        if img_result.get('success'):
            print(f"  • Page images: {img_result['output_dir']}")
    else:
        print(f"\n✗ Extraction failed: {result['error']}")