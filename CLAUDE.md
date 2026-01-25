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
│   └── kor.traineddata    # Korean Tesseract language model
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

# Start OpenSearch container with persistent storage
docker run --rm --name es01 --network opensearch-net \
  -e "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=hanSHin@1" \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "plugins.security.disabled=true" \
  -v opensearch-data:/usr/share/opensearch/data \
  opensearchproject/opensearch:3.1.0

# Start OpenSearch Dashboards (optional, in another terminal)
docker run -d --rm --name opensearch-dashboards --network opensearch-net \
  -p 8002:5601 \
  -e OPENSEARCH_USERNAME=admin \
  -e OPENSEARCH_PASSWORD=hanSHin@1 \
  -e DISABLE_SECURITY_DASHBOARDS_PLUGIN=true \
  -e OPENSEARCH_SSL_VERIFICATIONMODE=none \
  -e NODE_OPTIONS="--openssl-legacy-provider" \
  -e OPENSEARCH_HOSTS='["http://es01:9200"]' \
  opensearchproject/opensearch-dashboards:3.1.0

# Or use the convenience script
bash scripts/opensearch.sh
```

**Access points:**
- OpenSearch API: http://localhost:9200
- OpenSearch Dashboards: http://localhost:8002

### Execution

```bash
# Activate conda environment first
conda activate korea_history

# Process exam PDF and extract questions
python problem_parsing.py

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

## Known Issues

1. **Hardcoded credentials** in `insert_to_opensearch.py:285-286` - OpenSearch password exposed
2. **SSL verification disabled** in `problem_parsing.py:50` - Security risk
3. **Exam ID (74) hardcoded** throughout - Not parameterized for multiple exams

## Additional Documentation

When working on specific topics, consult these files:

| Topic | File |
|-------|------|
| Architectural patterns & design decisions | `.claude/docs/architectural_patterns.md` |
