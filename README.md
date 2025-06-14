# Korean OCR with Tesseract

This project uses Tesseract OCR to extract text from Korean documents, with a focus on identifying question marks and bracketed text. It includes functionality to convert PDFs to images and perform OCR with bounding box visualization.

## Features

- PDF to PNG conversion with adjustable DPI
- Korean text recognition using Tesseract OCR
- Bounding box visualization for detected text
- Filtering for specific text patterns (question marks, brackets)
- Confidence score display for each detected text

## Requirements

- Python 3.6+
- Tesseract OCR
- Korean language pack for Tesseract

## Installation

1. Install Tesseract OCR and Korean language pack:
```bash
# macOS
brew install tesseract
brew install tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-kor
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Convert PDF to images:
```python
from test_tesseract import pdf_to_images

# Convert PDF to PNG images
image_paths = pdf_to_images("path/to/your.pdf", "output_directory", dpi=300)
```

2. Run OCR on images:
```python
# The script will automatically process images and create:
# - output.txt: Extracted text
# - ocr_results.csv: Detailed OCR results
# - output_with_boxes.png: Visualization of detected text
```

## Project Structure

- `test_tesseract.py`: Main script with OCR and PDF conversion functionality
- `requirements.txt`: Python package dependencies
- `tessdata/`: Directory for Tesseract language data
- `output_images/`: Directory for converted PDF pages

## License

MIT License 