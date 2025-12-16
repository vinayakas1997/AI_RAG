"""
PDF Visualizer - Mark extracted elements on PDF for visual inspection
"""

import os
from typing import Dict, List, Optional
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class PDFVisualizer:
    """
    Visualize extraction results by marking regions on PDF
    """
    
    # Color scheme for different element types
    COLORS = {
        'text': (0, 0, 255),        # Blue
        'Title': (255, 0, 0),       # Red
        'NarrativeText': (0, 0, 255),  # Blue
        'ListItem': (0, 255, 0),    # Green
        'Table': (255, 165, 0),     # Orange
        'Image': (255, 0, 255),     # Magenta
        'Figure': (255, 0, 255),    # Magenta
        'Header': (128, 0, 128),    # Purple
        'Footer': (128, 128, 128),  # Gray
        'default': (0, 0, 0)        # Black
    }
    
    def __init__(self):
        """Initialize PDF Visualizer"""
        self.available = PYMUPDF_AVAILABLE and PIL_AVAILABLE
        
        if not PYMUPDF_AVAILABLE:
            print("Warning: PyMuPDF not installed. Install with: pip install PyMuPDF")
        if not PIL_AVAILABLE:
            print("Warning: Pillow not installed. Install with: pip install Pillow")
    
    def visualize_extraction(
        self,
        pdf_path: str,
        extraction_result: Dict,
        output_path: str = None,
        show_labels: bool = True,
        opacity: float = 0.3
    ) -> Dict:
        """
        Create annotated PDF showing extracted elements
        
        Args:
            pdf_path: Path to original PDF
            extraction_result: Result dict from extractor
            output_path: Path for output PDF (auto-generated if None)
            show_labels: Show element type labels
            opacity: Transparency of highlights (0.0 to 1.0)
            
        Returns:
            dict: {
                'success': bool,
                'output_path': str,
                'pages_processed': int
            }
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Required libraries not available'
            }
        
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Generate output path if not provided
            if not output_path:
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_dir = "extraction_results/visualized"
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{base_name}_annotated.pdf")
            
            # Get elements with coordinates
            elements = extraction_result.get('metadata', {}).get('elements', [])
            
            if not elements:
                return {
                    'success': False,
                    'error': 'No elements with coordinates found'
                }
            
            # Group elements by page
            elements_by_page = {}
            for element in elements:
                metadata = element.get('metadata', {})
                
                # Get page number
                page_num = metadata.get('page_number')
                if page_num is None:
                    continue
                
                # Get coordinates
                coordinates = metadata.get('coordinates')
                if not coordinates:
                    continue
                
                if page_num not in elements_by_page:
                    elements_by_page[page_num] = []
                
                elements_by_page[page_num].append({
                    'type': element.get('type', 'unknown'),
                    'text': element.get('text', ''),
                    'coordinates': coordinates
                })
            
            # Annotate each page
            pages_processed = 0
            for page_num, page_elements in elements_by_page.items():
                if page_num > len(doc) - 1:
                    continue
                
                page = doc[page_num]
                
                # Draw rectangles for each element
                for i, elem in enumerate(page_elements):
                    coords = elem['coordinates']
                    elem_type = elem['type']
                    
                    # Get bounding box from coordinates
                    bbox = self._get_bbox_from_coordinates(coords, page)
                    
                    if bbox:
                        # Get color for element type
                        color = self.COLORS.get(elem_type, self.COLORS['default'])
                        rgb = [c / 255.0 for c in color]  # Normalize to 0-1
                        
                        # Draw rectangle
                        rect = fitz.Rect(bbox)
                        annot = page.add_rect_annot(rect)
                        annot.set_colors(stroke=rgb)
                        annot.set_opacity(opacity)
                        annot.update()
                        
                        # Add label if requested
                        if show_labels:
                            label = f"{elem_type} #{i+1}"
                            self._add_label(page, bbox, label, color)
                
                pages_processed += 1
            
            # Save annotated PDF
            doc.save(output_path)
            doc.close()
            
            return {
                'success': True,
                'output_path': output_path,
                'pages_processed': pages_processed,
                'total_elements': len(elements),
                'elements_by_page': {k: len(v) for k, v in elements_by_page.items()}
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_bbox_from_coordinates(self, coordinates: Dict, page) -> Optional[List]:
        """
        Extract bounding box from coordinates
        
        Args:
            coordinates: Coordinates dict from metadata
            page: PyMuPDF page object
            
        Returns:
            list: [x0, y0, x1, y1] or None
        """
        try:
            # Handle different coordinate formats
            if 'points' in coordinates:
                # Format: {'points': [[x1,y1], [x2,y2], ...]}
                points = coordinates['points']
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                return [
                    min(x_coords),
                    min(y_coords),
                    max(x_coords),
                    max(y_coords)
                ]
            
            elif 'layout_width' in coordinates and 'layout_height' in coordinates:
                # Format: {'points': [...], 'layout_width': w, 'layout_height': h}
                points = coordinates['points']
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                return [
                    min(x_coords),
                    min(y_coords),
                    max(x_coords),
                    max(y_coords)
                ]
            
            else:
                return None
        
        except Exception as e:
            print(f"Error parsing coordinates: {e}")
            return None
    
    def _add_label(self, page, bbox: List, label: str, color: tuple):
        """
        Add text label to element
        
        Args:
            page: PyMuPDF page object
            bbox: Bounding box [x0, y0, x1, y1]
            label: Label text
            color: RGB color tuple
        """
        try:
            # Position label above the box
            x = bbox[0]
            y = bbox[1] - 5
            
            # Normalize color
            rgb = [c / 255.0 for c in color]
            
            # Insert text
            page.insert_text(
                (x, y),
                label,
                fontsize=8,
                color=rgb
            )
        except Exception as e:
            print(f"Error adding label: {e}")
    
    def create_comparison_view(
        self,
        pdf_path: str,
        extraction_results: Dict[str, Dict],
        output_path: str = None
    ) -> Dict:
        """
        Create side-by-side comparison of multiple extraction results
        
        Args:
            pdf_path: Path to original PDF
            extraction_results: Dict of {extractor_name: result}
            output_path: Output path for comparison PDF
            
        Returns:
            dict: Operation result
        """
        # TODO: Implement side-by-side comparison
        # This would create a multi-column PDF showing different extractions
        pass
    
    def export_as_images(
        self,
        pdf_path: str,
        extraction_result: Dict,
        output_dir: str = None,
        dpi: int = 150
    ) -> Dict:
        """
        Export annotated pages as images
        
        Args:
            pdf_path: Path to original PDF
            extraction_result: Extraction result
            output_dir: Output directory for images
            dpi: Image resolution
            
        Returns:
            dict: {
                'success': bool,
                'images': list of image paths
            }
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Required libraries not available'
            }
        
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Generate output directory
            if not output_dir:
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_dir = f"extraction_results/visualized/{base_name}_images"
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Get elements
            elements = extraction_result.get('metadata', {}).get('elements', [])
            elements_by_page = {}
            
            for element in elements:
                metadata = element.get('metadata', {})
                page_num = metadata.get('page_number')
                
                if page_num is None:
                    continue
                
                if page_num not in elements_by_page:
                    elements_by_page[page_num] = []
                
                elements_by_page[page_num].append(element)
            
            # Convert pages to images with annotations
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Render page to image
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                draw = ImageDraw.Draw(img, 'RGBA')
                
                # Draw elements for this page
                if page_num in elements_by_page:
                    for elem in elements_by_page[page_num]:
                        metadata = elem.get('metadata', {})
                        coords = metadata.get('coordinates')
                        
                        if coords:
                            bbox = self._get_bbox_from_coordinates(coords, page)
                            
                            if bbox:
                                # Scale bbox to image coordinates
                                scale = dpi / 72
                                scaled_bbox = [int(coord * scale) for coord in bbox]
                                
                                # Get color
                                elem_type = elem.get('type', 'unknown')
                                color = self.COLORS.get(elem_type, self.COLORS['default'])
                                color_with_alpha = color + (int(255 * 0.3),)
                                
                                # Draw rectangle
                                draw.rectangle(scaled_bbox, outline=color, width=2, fill=color_with_alpha)
                                
                                # Draw label
                                label = elem_type
                                draw.text(
                                    (scaled_bbox[0], scaled_bbox[1] - 15),
                                    label,
                                    fill=color
                                )
                
                # Save image
                image_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.png")
                img.save(image_path, "PNG")
                image_paths.append(image_path)
            
            doc.close()
            
            return {
                'success': True,
                'output_dir': output_dir,
                'images': image_paths,
                'page_count': len(image_paths)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_statistics(self, extraction_result: Dict) -> Dict:
        """
        Generate statistics about extracted elements
        
        Args:
            extraction_result: Extraction result
            
        Returns:
            dict: Statistics
        """
        elements = extraction_result.get('metadata', {}).get('elements', [])
        
        stats = {
            'total_elements': len(elements),
            'by_type': {},
            'by_page': {},
            'with_coordinates': 0,
            'without_coordinates': 0
        }
        
        for elem in elements:
            # Count by type
            elem_type = elem.get('type', 'unknown')
            stats['by_type'][elem_type] = stats['by_type'].get(elem_type, 0) + 1
            
            # Count by page
            metadata = elem.get('metadata', {})
            page_num = metadata.get('page_number')
            if page_num is not None:
                stats['by_page'][page_num] = stats['by_page'].get(page_num, 0) + 1
            
            # Count coordinates
            if metadata.get('coordinates'):
                stats['with_coordinates'] += 1
            else:
                stats['without_coordinates'] += 1
        
        return stats