import ollama
from pathlib import Path
import os

# Bypass proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'
# prompt_check = """Convert this flowchart to structured markdown format. 
    
# Include:
# - All text content
# - Flow direction (arrows)
# - Box types and relationships
# - Table headers and structure
# - Database/storage symbols

# Preserve the Japanese text exactly as shown."""

# prompt_check = """Convert this flowchart to Mermaid diagram syntax.

# Include:
# - All boxes as nodes with their Japanese text
# - All arrows/connections with proper direction
# - Database symbols as cylindrical nodes
# - Dotted/dashed lines where shown
# - Grouping/subgraphs if applicable

# Output valid Mermaid code that can be rendered."""

prompt_check = """<|grounding|>Convert this document to markdown.

This is a process flow diagram with:
- Header table
- Two separate flowcharts
- Multiple process boxes
- Arrow connections
- Database symbols (cylinders)
- Dotted and solid lines

Preserve spatial relationships and flow logic."""

def deepseek_ocr(
    image_path,
    prompt=prompt_check,
    model_name="deepseek-ocr:3b",
    host="http://localhost:11434"  # Explicitly set host
):
    """
    Run DeepSeek-OCR using Ollama library
    """
    # Create client with explicit host
    client = ollama.Client(host=host)
    
    response = client.generate(
        model=model_name,
        prompt=prompt,
        images=[image_path]
    )
    
    return response['response']

def deepseek_ocr_stream(
    image_path,
    prompt=prompt_check,
    model_name="deepseek-ocr:3b",
    host="http://localhost:11434"
):
    """Run with streaming"""
    client = ollama.Client(host=host)
    
    stream = client.generate(
        model=model_name,
        prompt=prompt,
        images=[image_path],
        stream=True
    )
    
    for chunk in stream:
        yield chunk['response']

def deepseek_ocr_chat(
    image_path,
    prompt=prompt_check,
    model_name="deepseek-ocr:3b",
    host="http://localhost:11434"
):
    """Chat API version"""
    client = ollama.Client(host=host)
    
    response = client.chat(
        model=model_name,
        messages=[
            {
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }
        ]
    )
    
    return response['message']['content']

# Example usage
if __name__ == "__main__":
    # Set proxy bypass FIRST
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    os.environ['no_proxy'] = 'localhost,127.0.0.1'
    
    image_file = 'table_img.png'
    output_path = 'output'
    
    print("Running OCR...")
    try:
        result = deepseek_ocr(
            image_path=image_file,
            prompt="Convert the document to markdown.",
            host="http://127.0.0.1:11434"  # Try explicit IP
        )
        
        print("OCR Result:")
        print(result)
        
        # Save result
        Path(output_path).mkdir(parents=True, exist_ok=True)
        output_file = Path(output_path) / f"table_result_{Path(image_file).stem}_ocr.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"\nSaved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")