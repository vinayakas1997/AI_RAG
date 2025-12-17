import ollama
from pathlib import Path
import json
import re
from PIL import Image, ImageDraw, ImageFont
import os

# STEP 0: Bypass proxy (critical for your network)
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

def deepseek_ocr_with_grounding(
    image_path,
    prompt="<|grounding|>Convert the document to markdown.",
    model_name="deepseek-ocr:3b",
    host="http://localhost:11434"
):
    """Extract text with bounding box coordinates"""
    client = ollama.Client(host=host)
    
    response = client.generate(
        model=model_name,
        prompt=prompt,
        images=[image_path]
    )
    
    return response['response']

def parse_grounding_output(text):
    """
    Parse the grounding output to extract text and coordinates
    DeepSeek returns: <box>[[x1,y1,x2,y2]]</box>text or <ref>text</ref><box>[[x1,y1,x2,y2]]</box>
    """
    # Try multiple patterns
    pattern1 = r'<box>\[\[(\d+),(\d+),(\d+),(\d+)\]\]</box>\s*([^<]+)'
    pattern2 = r'<ref>([^<]+)</ref><box>\[\[(\d+),(\d+),(\d+),(\d+)\]\]</box>'
    pattern3 = r'([^<]+)<box>\[\[(\d+),(\d+),(\d+),(\d+)\]\]</box>'
    
    grounding_data = []
    
    # Try all patterns
    for match in re.finditer(pattern1, text):
        x1, y1, x2, y2 = map(int, match.groups()[:4])
        content = match.group(5).strip()
        grounding_data.append({'text': content, 'bbox': [x1, y1, x2, y2]})
    
    for match in re.finditer(pattern2, text):
        content = match.group(1).strip()
        x1, y1, x2, y2 = map(int, match.groups()[1:5])
        grounding_data.append({'text': content, 'bbox': [x1, y1, x2, y2]})
    
    for match in re.finditer(pattern3, text):
        content = match.group(1).strip()
        x1, y1, x2, y2 = map(int, match.groups()[1:5])
        grounding_data.append({'text': content, 'bbox': [x1, y1, x2, y2]})
    
    return grounding_data

def visualize_grounding(
    image_path,
    grounding_data,
    output_path,
    box_color=(0, 255, 0),
    text_color=(255, 0, 0),
    box_width=3
):
    """Draw bounding boxes on image"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    for idx, item in enumerate(grounding_data):
        bbox = item['bbox']
        
        # Draw rectangle
        draw.rectangle(
            [bbox[0], bbox[1], bbox[2], bbox[3]],
            outline=box_color,
            width=box_width
        )
        
        # Draw ID number
        draw.text((bbox[0], bbox[1] - 15), f"#{idx+1}", fill=text_color, font=font)
    
    img.save(output_path)
    print(f"✓ Saved visualization: {output_path}")
    return img

# MAIN EXECUTION
if __name__ == "__main__":
    # Configuration
    image_file = 'table_img.png'  # Change this to your image
    output_dir = Path('output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("DeepSeek-OCR with Grounding Visualization")
    print("=" * 60)
    
    # Check if image exists
    if not Path(image_file).exists():
        print(f"❌ Error: Image '{image_file}' not found!")
        exit(1)
    
    # Step 1: Extract with grounding
    print(f"\n📸 Processing: {image_file}")
    print("Step 1: Extracting text with grounding data...")
    
    try:
        result = deepseek_ocr_with_grounding(
            image_file,
            prompt="<|grounding|>Extract all text elements with their positions."
        )
        
        # Save raw result
        raw_file = output_dir / f"{Path(image_file).stem}_raw.txt"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✓ Raw output saved: {raw_file}")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        exit(1)
    
    # Step 2: Parse grounding data
    print("\nStep 2: Parsing grounding data...")
    grounding_data = parse_grounding_output(result)
    
    if len(grounding_data) == 0:
        print("⚠️  Warning: No grounding data found in output!")
        print("The model may not have returned coordinates.")
        print("\nRaw output preview:")
        print(result[:500])
    else:
        print(f"✓ Found {len(grounding_data)} grounded elements")
        
        # Save JSON
        json_file = output_dir / f"{Path(image_file).stem}_grounding.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(grounding_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Grounding data saved: {json_file}")
        
        # Step 3: Visualize
        print("\nStep 3: Creating visualization...")
        vis_file = output_dir / f"{Path(image_file).stem}_visualization.png"
        visualize_grounding(image_file, grounding_data, vis_file)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ COMPLETE!")
        print("=" * 60)
        print(f"Total elements detected: {len(grounding_data)}")
        print(f"Visualization: {vis_file}")
        print(f"JSON data: {json_file}")
        print(f"Raw text: {raw_file}")
        
        # Show first few elements
        print("\n📋 First 5 detected elements:")
        for i, item in enumerate(grounding_data[:5]):
            text_preview = item['text'][:40] + "..." if len(item['text']) > 40 else item['text']
            print(f"  {i+1}. '{text_preview}' at {item['bbox']}")