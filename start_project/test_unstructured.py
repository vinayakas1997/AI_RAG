"""
Test PDF visualization
"""

from extractors import UnstructuredExtractor
from utils import FileUtils, PDFVisualizer
import os

def test_visualization(file_path: str):
    """Test extraction and visualization"""
    
    print("=" * 60)
    print("PDF EXTRACTION AND VISUALIZATION TEST")
    print("=" * 60)
    
    # Step 1: Extract content
    print("\nStep 1: Extracting content...")
    extractor = UnstructuredExtractor(
        strategy="hi_res",
        languages=['jpn', 'eng']
    )
    
    result = extractor.extract(file_path)
    
    if not result['success']:
        print(f"✗ Extraction failed: {result['error']}")
        return
    
    print(f"✓ Extraction successful!")
    print(f"  Elements: {result['metadata']['total_elements']}")
    print(f"  Tables: {result['metadata']['table_count']}")
    print(f"  Duration: {result['metadata']['duration_seconds']:.2f}s")
    
    # Step 2: Save extraction results
    print("\nStep 2: Saving extraction results...")
    save_result = FileUtils.save_extraction_results(
        result=result,
        output_dir="extraction_results",
        file_name=os.path.splitext(os.path.basename(file_path))[0]
    )
    
    if save_result['success']:
        print(f"✓ Results saved to: {save_result['output_dir']}")
    
    # Step 3: Create annotated PDF
    print("\nStep 3: Creating annotated PDF...")
    visualizer = PDFVisualizer()
    
    if not visualizer.available:
        print("✗ Visualizer not available (missing libraries)")
        print("  Install with: pip install PyMuPDF Pillow")
        return
    
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
    
    # Step 4: Export as images
    print("\nStep 4: Exporting pages as annotated images...")
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
    
    # Step 5: Generate statistics
    print("\nStep 5: Element statistics...")
    stats = visualizer.generate_statistics(result)
    
    print(f"  Total elements: {stats['total_elements']}")
    print(f"  With coordinates: {stats['with_coordinates']}")
    print(f"  Without coordinates: {stats['without_coordinates']}")
    
    print("\n  Elements by type:")
    for elem_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"    {elem_type}: {count}")
    
    print("\n  Elements by page:")
    for page_num, count in sorted(stats['by_page'].items()):
        print(f"    Page {page_num + 1}: {count} elements")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print(f"\nCheck these directories:")
    if save_result['success']:
        print(f"  • Text results: {save_result['output_dir']}")
    if viz_result.get('success'):
        print(f"  • Annotated PDF: {os.path.dirname(viz_result['output_path'])}")
    if img_result.get('success'):
        print(f"  • Page images: {img_result['output_dir']}")

if __name__ == "__main__":
    file_path = r"C:\Users\106761\Desktop\Rag_Test_Files\下野部工場\02AC001：下野部工場　機密区域管理要領\02AC001(1)：下野部工場　機密区域管理要領.pdf"
    
    test_visualization(file_path)