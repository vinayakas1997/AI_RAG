import ollama
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
import os

# Bypass proxy
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
    Parse DeepSeek-OCR grounding output
    Format: <|ref|>label<|/ref|><|det|>[[x1,y1,x2,y2]]<|/det|>
    """
    grounding_data = []
    
    # Split by lines and parse each line
    lines = text.split('\n')
    
    for line in lines:
        # Check if line contains both ref and det tags
        if '<|ref|>' in line and '<|det|>' in line:
            try:
                # Extract label between <|ref|> and <|/ref|>
                label_start = line.find('<|ref|>') + 7
                label_end = line.find('<|/ref|>')
                label = line[label_start:label_end].strip()
                
                # Extract coordinates between [[ and ]]
                coords_start = line.find('[[') + 2
                coords_end = line.find(']]')
                coords_str = line[coords_start:coords_end]
                
                # Parse coordinates
                coords = [int(x.strip()) for x in coords_str.split(',')]
                
                if len(coords) == 4:
                    grounding_data.append({
                        'id': len(grounding_data) + 1,
                        'label': label,
                        'bbox': coords,
                        'bbox_str': f"[{coords[0]}, {coords[1]}, {coords[2]}, {coords[3]}]"
                    })
                    
            except Exception as e:
                print(f"⚠️  Could not parse line: {line[:50]}... - Error: {e}")
                continue
    
    return grounding_data

def visualize_grounding(
    image_path,
    grounding_data,
    output_path,
    show_labels=True
):
    """Draw bounding boxes on image"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 10)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    # Color mapping
    color_map = {
        'table': (255, 0, 0),       # Red
        'sub_title': (0, 255, 0),   # Green
        'image': (0, 0, 255),       # Blue
        'text': (255, 255, 0),      # Yellow
        'figure': (255, 0, 255),    # Magenta
    }
    
    for item in grounding_data:
        bbox = item['bbox']
        label = item['label']
        
        # Get color
        color = color_map.get(label, (0, 255, 0))
        
        # Draw rectangle
        draw.rectangle(
            [bbox[0], bbox[1], bbox[2], bbox[3]],
            outline=color,
            width=3
        )
        
        if show_labels:
            # Label text
            label_text = f"#{item['id']}: {label}"
            
            # Draw label with background
            text_bbox = draw.textbbox((bbox[0], bbox[1] - 20), label_text, font=font_small)
            draw.rectangle(text_bbox, fill=(255, 255, 255))
            draw.text(
                (bbox[0], bbox[1] - 20),
                label_text,
                fill=color,
                font=font_small
            )
    
    img.save(output_path)
    print(f"✓ Visualization saved: {output_path}")
    return img

# MAIN
if __name__ == "__main__":
    image_file = 'table_img.png'
    output_dir = Path('output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("DeepSeek-OCR with Grounding Visualization")
    print("=" * 60)
    
    if not Path(image_file).exists():
        print(f"❌ Error: Image '{image_file}' not found!")
        exit(1)
    
    # Step 1: Extract
    print(f"\n📸 Processing: {image_file}")
    print("Step 1: Extracting with grounding...")
    
    try:
        result = deepseek_ocr_with_grounding(
            image_file,
            prompt="<|grounding|>Extract all text elements."
        )
        
        raw_file = output_dir / f"{Path(image_file).stem}_raw.txt"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✓ Raw output: {raw_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
    
    # Step 2: Parse
    print("\nStep 2: Parsing coordinates...")
    grounding_data = parse_grounding_output(result)
    
    if len(grounding_data) == 0:
        print("❌ No grounding data found!")
        print("\nFirst 300 chars of output:")
        print(result[:300])
        exit(1)
    
    print(f"✓ Found {len(grounding_data)} elements")
    
    # Save JSON
    json_file = output_dir / f"{Path(image_file).stem}_grounding.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(grounding_data, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON saved: {json_file}")
    
    # Step 3: Visualize
    print("\nStep 3: Creating visualization...")
    vis_file = output_dir / f"{Path(image_file).stem}_visualization.png"
    visualize_grounding(image_file, grounding_data, vis_file)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SUCCESS!")
    print("=" * 60)
    print(f"📊 Total: {len(grounding_data)} elements")
    print(f"🖼️  Image: {vis_file}")
    print(f"📄 JSON: {json_file}")
    
    print("\n📋 Detected Elements:")
    for item in grounding_data:
        print(f"  #{item['id']:2d} [{item['label']:10s}] at {item['bbox_str']}")