# Korea History OCR Project

Korean history exam document processing system that extracts questions from PDF workbooks using OCR, segments them with bounding box annotations, and indexes to OpenSearch for searchable access.

## Tech Stack

- **Python 3.6+**
- **PyMuPDF (fitz)**: PDF to image conversion
- **Tesseract OCR + pytesseract**: Korean text recognition
- **PIL/Pillow**: Image processing and cropping
- **OpenSearch**: Document indexing and search
- **pandas/numpy**: Data manipulation
- **matplotlib**: Bounding box visualization
- **Docker**: OpenSearch container orchestration

## Project Structure

```
/korea_history/
├── problem_parsing.py     # Main workflow: PDF → OCR → question segmentation
├── anwser_parsing.py      # Answer key extraction from PDF
├── insert_to_opensearch.py # OpenSearch data indexing (class-based)
├── data/
│   ├── raw/history_exam/  # Original PDF files
│   └── processed/         # Processed output (images, CSV, JSONL)
├── utils/
│   ├── parsing.py         # Reusable PDF/drawing utilities
│   └── (kor.traineddata)  # Korean Tesseract model (auto-downloaded at runtime)
├── scripts/
│   └── opensearch.sh      # Docker deployment for OpenSearch
├── temp/                  # Experimental/test scripts
└── box_outputs/           # Visualization outputs
```

## Key Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| `problem_parsing.py` | Main pipeline | PDF conversion (L24-36), OCR filtering (L68-76), question detection (L96-143) |
| `insert_to_opensearch.py` | Data indexing | `OpenSearchDataInserter` class (L18-276), bulk insertion (L188-246) |
| `anwser_parsing.py` | Answer extraction | Regex parsing for circled answers (L1-46) |
| `utils/parsing.py` | Utilities | `pdf_to_images()` (L10-58), `draw_rect()` (L60-67) |

## Commands

### Installation

```bash
# Install Tesseract OCR (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-kor

# Create and activate conda environment
conda create -n korea_history python=3.10 -y
conda activate korea_history

# Install Python dependencies
pip install -r requirements.txt
```

### Docker Setup (OpenSearch)

```bash
# Create Docker network (first time only)
docker network create opensearch-net

# Create persistent volume (first time only)
docker volume create opensearch-data

# Set password via environment variable (or edit .env file)
export OPENSEARCH_PASSWORD=your_password_here

# Or use the convenience script (starts both OpenSearch and Dashboards)
bash scripts/opensearch.sh
```

**Access points:**
- OpenSearch API: http://localhost:9200
- OpenSearch Dashboards: http://localhost:8002

### Execution

```bash
# Activate conda environment first
conda activate korea_history

# Process exam PDF and extract questions (default exam 74)
python problem_parsing.py

# Process a specific exam number
python problem_parsing.py --exam-no 74

# Extract answer keys
python anwser_parsing.py

# Insert data into OpenSearch (ensure container is running)
python insert_to_opensearch.py
```

## Data Flow

```
PDF → Split Pages (PNG) → OCR → Question Detection → Segmentation → Metadata (CSV/JSONL) → OpenSearch
```

## Output Schemas

**Bounding Box Metadata** (`74_bbox_info.csv`):
- `image_path`: Path to cropped question image
- `page`: Source page filename
- `question_no`: Question number (1-50)
- `bounding_box`: `[left, top, width, height]`
- `artifact_type`: Always "question"

**OpenSearch Index Fields** (`insert_to_opensearch.py:50-91`):
- Keyword fields: `image_path`, `page`, `artifact_type`, `exam_id`
- Float fields: `question_no`, `left`, `top`, `width`, `height`
- Date field: `timestamp`

## OCR Configuration

Tesseract config (`problem_parsing.py:69`):
```
--oem 3 --psm 6 -l kor
```
- OEM 3: LSTM neural network engine
- PSM 6: Single column text mode
- Confidence threshold: >= 70

## Configuration

- OpenSearch credentials are configured via environment variables (see `.env.example`)
- Exam ID is parameterized via `--exam-no` argument in `problem_parsing.py`

## Additional Documentation

When working on specific topics, consult these files:

| Topic | File |
|-------|------|
| Architectural patterns & design decisions | `.claude/docs/architectural_patterns.md` |
