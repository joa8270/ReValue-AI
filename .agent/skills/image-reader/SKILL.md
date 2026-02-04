---
name: image-reader
description: Comprehensive image analysis and OCR toolkit for reading, extracting text from, and analyzing images. Use when users need to extract text from screenshots, read document images, analyze visual content, or process uploaded images.
license: MIT
---

# Image Reader & OCR Toolkit

A complete toolkit for reading, processing, and extracting information from images using Python libraries and OCR technologies.

## Overview

This guide covers:
- **Image Loading**: Read various image formats (PNG, JPG, WEBP, etc.)
- **Text Extraction (OCR)**: Extract text using Tesseract OCR
- **Image Analysis**: Basic visual analysis and description
- **Image Processing**: Resize, crop, convert formats
- **Vision API**: Optional cloud-based image analysis

## Quick Start

```python
from PIL import Image
import pytesseract

# Read an image
image = Image.open('screenshot.png')

# Extract text using OCR
text = pytesseract.image_to_string(image)
print(f"Extracted text: {text}")
```

## Installation

```bash
# Required packages
pip install pillow pytesseract pdf2image easyocr

# Optional: Tesseract OCR engine
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

## Core Operations

### Load Image

```python
from PIL import Image

# Load image
image = Image.open('image.png')

# Get image info
print(f"Size: {image.size}")
print(f"Mode: {image.mode}")
print(f"Format: {image.format}")
```

### Convert Between Formats

```python
from PIL import Image

# PNG to JPEG
img = Image.open('image.png')
img.save('output.jpg', 'JPEG')

# With quality control
img.save('output.jpg', 'JPEG', quality=95)

# PNG to WEBP
img.save('output.webp', 'WEBP', quality=90)
```

### Resize Image

```python
from PIL import Image

img = Image.open('image.png')

# Resize with aspect ratio maintained
img.thumbnail((800, 800))
img.save('resized.png')

# Or specific dimensions
resized = img.resize((1200, 800), Image.LANCZOS)
resized.save('resized.png')
```

### Crop Image

```python
from PIL import Image

img = Image.open('image.png')

# Crop: (left, top, right, bottom)
cropped = img.crop((100, 100, 500, 400))
cropped.save('cropped.png')
```

## OCR (Optical Character Recognition)

### Basic Text Extraction

```python
import pytesseract
from PIL import Image

image = Image.open('document.png')

# Extract text
text = pytesseract.image_to_string(image)
print(text)

# Extract text with confidence
data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
for i, word in enumerate(data['text']):
    if word.strip():
        conf = data['conf'][i]
        print(f"{word} (confidence: {conf}%)")
```

### Multi-Language OCR

```python
# Specify language (eng, chi_sim, chi_tra, jpn, kor, etc.)
text = pytesseract.image_to_string(
    image, 
    lang='chi_sim+eng',  # Simplified Chinese + English
    config='--psm 6'  # Page segmentation mode
)
```

### Advanced OCR Configuration

```python
# Page segmentation modes
config = '--psm 6'  # Assume a single uniform block of text

# Common PSM values:
# 0: Orientation and script detection (OSD) only
# 1: Automatic page segmentation with OSD
# 3: Fully automatic page segmentation (default)
# 6: Assume a single uniform block of text
# 11: Sparse text (as few characters as possible)
# 12: Sparse text with OSD

# OCR with config
text = pytesseract.image_to_string(image, config=config)
```

### OCR for Different Image Types

#### Screenshots (UI Elements)

```python
# Better for screenshots and UI
text = pytesseract.image_to_string(
    image,
    config='--psm 7'  # Treat the image as a single text line
)
```

#### Document Scans

```python
# Better for full documents
text = pytesseract.image_to_string(
    image,
    config='--psm 3 --oem 3'  # Default auto-segmentation + LSTM OCR engine
)
```

#### Tables

```python
# For table extraction, use image_to_data for structure
data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
# Process coordinates and text to reconstruct table
```

## Image Preprocessing for Better OCR

### Convert to Grayscale

```python
from PIL import Image

img = Image.open('image.png').convert('L')
img.save('grayscale.png')
```

### Binarization (Black & White)

```python
from PIL import Image

img = Image.open('image.png').convert('L')

# Apply threshold
threshold = 128
img = img.point(lambda p: p > threshold and 255)
img.save('bw.png')
```

### Upscale Low-Res Images

```python
# Tesseract works better with 300 DPI
img = Image.open('lowres.png')
img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
img.save('upscaled.png')
```

## Alternative: EasyOCR

```python
import easyocr

# Initialize reader
reader = easyocr.Reader(['en', 'ch_sim'])

# Read image
result = reader.readtext('image.png')

for (bbox, text, prob) in result:
    print(f"Text: {text} (Confidence: {prob:.2f})")
    print(f"Bounding box: {bbox}")
```

## Vision API Integration (Optional)

### OpenAI Vision API

```python
import base64
from openai import OpenAI

client = OpenAI()

# Encode image
with open("image.png", "rb") as f:
    base64_image = base64.b64encode(f.read()).decode('utf-8')

# Analyze
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                }
            ]
        }
    ]
)
print(response.choices[0].message.content)
```

### Google Cloud Vision

```python
from google.cloud import vision

client = vision.ImageAnnotatorClient()

with open('image.png', 'rb') as f:
    response = client.label_detection(image=f.read())

for label in response.label_annotations:
    print(f"{label.description}: {label.score}")
```

## Image Analysis

### Basic Properties

```python
from PIL import Image
import numpy as np

img = Image.open('image.png')

# Color analysis
colors = img.getcolors(maxcolors=10)
print("Dominant colors:", colors)

# Image statistics
arr = np.array(img)
print(f"Mean RGB: {arr.mean(axis=(0,1))}")
print(f"Std RGB: {arr.std(axis=(0,1))}")
```

### Detect Elements (using OpenCV)

```python
import cv2

img = cv2.imread('image.png')

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detect edges
edges = cv2.Canny(gray, 100, 200)

# Find contours
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Found {len(contours)} objects")
```

## Common Use Cases

### Read Screenshot Text

```python
from PIL import Image
import pytesseract

img = Image.open('screenshot.png')

# Screenshots often have text on simple backgrounds
text = pytesseract.image_to_string(img, config='--psm 7')
print("Extracted text:", text)
```

### Process Document Scan

```python
from PIL import Image
import pytesseract

# Preprocess for documents
img = Image.open('scan.png').convert('L')

# Apply threshold for clean text
threshold = 200
img = img.point(lambda p: p > threshold and 255)

# OCR with Chinese support
text = pytesseract.image_to_string(img, lang='chi_sim+eng')
with open('extracted.txt', 'w', encoding='utf-8') as f:
    f.write(text)
```

### Extract Text from Multiple Images

```python
import os
from PIL import Image
import pytesseract

# Process all images in directory
for filename in os.listdir('images/'):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        img = Image.open(f'images/{filename}')
        text = pytesseract.image_to_string(img)
        
        # Save extracted text
        txt_file = f'output/{filename}.txt'
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Processed {filename}")
```

### Analyze Dashboard/Screenshot

```python
from PIL import Image
import pytesseract

img = Image.open('dashboard.png')

# Extract all text
text = pytesseract.image_to_string(img, config='--psm 6')

# Analyze for numbers (metrics, scores, etc.)
import re
numbers = re.findall(r'\d+[.,]?\d*', text)
print("Found numbers:", numbers)

# Look for key terms
keywords = ['users', 'revenue', 'errors', 'abm', 'citizens']
found = [kw for kw in keywords if kw.lower() in text.lower()]
print("Found keywords:", found)
```

## Quick Reference

| Task | Tool | Command/Code |
|------|-------|--------------|
| Read image | PIL | `Image.open('file.png')` |
| OCR text | pytesseract | `image_to_string(img)` |
| Multi-language OCR | pytesseract | `image_to_string(img, lang='chi_sim+eng')` |
| Resize image | PIL | `img.resize((w, h))` |
| Crop image | PIL | `img.crop((x1, y1, x2, y2))` |
| Convert format | PIL | `img.save('out.jpg', 'JPEG')` |
| Better OCR | Preprocess | Grayscale, threshold, upscale |
| Vision API | OpenAI | Vision API calls |

## Tips for Better Results

1. **Image Quality**: 300 DPI or higher works best
2. **Lighting**: Even, bright lighting without glare
3. **Contrast**: High contrast between text and background
4. **Preprocessing**: Grayscale and binarization often help
5. **Language**: Specify correct language codes (chi_sim, chi_tra, eng, etc.)
6. **PSM**: Choose right page segmentation mode for your image type

## Troubleshooting

### OCR Returns Empty Text
- Check if text is actually readable by humans
- Try different PSM modes
- Preprocess: grayscale → threshold
- Upscale low-resolution images
- Verify tesseract installation path

### Low Confidence Results
- Improve image quality (better resolution)
- Enhance contrast
- Try EasyOCR as alternative
- Use Vision API for complex images

### Tesseract Not Found
```python
# Set tesseract path if needed
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Dependencies

```bash
# Core
pip install pillow numpy

# OCR
pip install pytesseract easyocr

# Optional
pip install opencv-python openai google-cloud-vision
```
