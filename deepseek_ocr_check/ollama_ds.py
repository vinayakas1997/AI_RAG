import ollama
from pathlib import Path
import base64
import os 
# Bypass proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'


def encode_image(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def deepseek_ocr(
    image_path,
    prompt="Convert the document to markdown.",
    model_name="deepseek-ocr:3b"
):
    """
    Run DeepSeek-OCR using Ollama library
    
    Args:
        image_path: Path to the image file
        prompt: OCR prompt (default: markdown conversion)
        model_name: Ollama model name (default: "deepseek-ocr")
    
    Returns:
        str: OCR result text
    """
    response = ollama.generate(
        model=model_name,
        prompt=prompt,
        images=[image_path]  # Can pass path directly or base64
    )
    
    return response['response']

def deepseek_ocr_stream(
    image_path,
    prompt="Convert the document to markdown.",
    model_name="deepseek-ocr:3b"
):
    """
    Run DeepSeek-OCR with streaming output
    
    Args:
        image_path: Path to the image file
        prompt: OCR prompt
        model_name: Ollama model name
    
    Yields:
        str: Streamed OCR result chunks
    """
    stream = ollama.generate(
        model=model_name,
        prompt=prompt,
        images=[image_path],
        stream=True
    )
    
    for chunk in stream:
        yield chunk['response']

def deepseek_ocr_chat(
    image_path,
    prompt="Convert the document to markdown.",
    model_name="deepseek-ocr:3b"
):
    """
    Run DeepSeek-OCR using chat API (alternative approach)
    
    Args:
        image_path: Path to the image file
        prompt: OCR prompt
        model_name: Ollama model name
    
    Returns:
        str: OCR result text
    """
    response = ollama.chat(
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
    image_file = 'text_img.png'
    output_path = 'output'
    
    # Method 1: Simple generate (non-streaming)
    print("Running OCR...")
    result = deepseek_ocr(
        image_path=image_file,
        prompt="Convert the document to markdown."
    )
    
    print("OCR Result:")
    print(result)
    
    # Save result
    Path(output_path).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_path) / f"{Path(image_file).stem}_ocr.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\nSaved to: {output_file}")
    
    # Method 2: Streaming version
    print("\n--- Streaming OCR ---")
    full_response = ""
    for chunk in deepseek_ocr_stream(image_file):
        print(chunk, end='', flush=True)
        full_response += chunk
    print("\n")
    
    # Method 3: Chat API
    print("\n--- Using Chat API ---")
    chat_result = deepseek_ocr_chat(image_file)
    print(chat_result)