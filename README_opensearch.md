# OpenSearch Data Insertion for History Exam Bounding Box Data

This project provides Python scripts to insert history exam bounding box data from CSV files into OpenSearch.

## Features

- Bulk insertion of CSV data into OpenSearch
- Automatic index creation with proper mapping
- Data cleaning and validation
- Error handling and logging
- Search functionality for inserted data
- Support for authentication and SSL

## Prerequisites

- Python 3.7+
- OpenSearch cluster running
- Required Python packages (see requirements.txt)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your OpenSearch cluster is running and accessible.

## Configuration

Edit the configuration in `insert_to_opensearch.py` or set environment variables:

```python
config = {
    'host': 'localhost',           # OpenSearch host
    'port': 9200,                  # OpenSearch port
    'username': None,              # Username (if authentication required)
    'password': None,              # Password (if authentication required)
    'use_ssl': False,              # Use HTTPS
    'verify_certs': False          # Verify SSL certificates
}
```

## Usage

### Basic Usage

Run the main script to insert data:

```bash
python insert_to_opensearch.py
```

### Using the Class Directly

```python
from insert_to_opensearch import OpenSearchDataInserter

# Initialize inserter
inserter = OpenSearchDataInserter(
    host='localhost',
    port=9200
)

# Insert data from CSV
success = inserter.insert_data('data/processed/history_exam/74/74_bbox_info.csv')

if success:
    print("Data inserted successfully!")
```

### Search Examples

```python
# Search for all questions from exam 74
results = inserter.search_data({
    "term": {"exam_id": "74"}
})

# Search for specific question
results = inserter.search_data({
    "bool": {
        "must": [
            {"term": {"exam_id": "74"}},
            {"term": {"question_no": 1.0}}
        ]
    }
})

# Search for questions with specific dimensions
results = inserter.search_data({
    "bool": {
        "must": [
            {"term": {"artifact_type": "question"}},
            {"range": {"width": {"gte": 1000}}},
            {"range": {"height": {"gte": 1500}}}
        ]
    }
})
```

## Data Structure

The script processes CSV data with the following columns:

- `image_path`: Path to the image file
- `page`: Page identifier
- `artifact_type`: Type of artifact (question, split_page, etc.)
- `question_no`: Question number (for questions)
- `bounding_box`: Bounding box coordinates as string
- `left`: Left coordinate
- `top`: Top coordinate
- `width`: Width of bounding box
- `height`: Height of bounding box

### Index Mapping

The script creates an index with the following mapping:

```json
{
  "mappings": {
    "properties": {
      "image_path": {"type": "keyword"},
      "page": {"type": "keyword"},
      "artifact_type": {"type": "keyword"},
      "question_no": {"type": "float"},
      "bounding_box": {"type": "keyword"},
      "left": {"type": "float"},
      "top": {"type": "float"},
      "width": {"type": "float"},
      "height": {"type": "float"},
      "exam_id": {"type": "keyword"},
      "timestamp": {"type": "date"}
    }
  }
}
```

## Error Handling

The script includes comprehensive error handling:

- Connection errors
- Data parsing errors
- Bulk insertion errors
- Index creation errors

All errors are logged with appropriate detail levels.

## Logging

The script uses Python's logging module with the following levels:

- INFO: General information about operations
- WARNING: Non-critical issues
- ERROR: Critical errors that prevent operation

## Troubleshooting

### Connection Issues

1. Check if OpenSearch is running:
```bash
curl http://localhost:9200
```

2. Verify network connectivity and firewall settings

3. Check authentication credentials if required

### Data Issues

1. Verify CSV file format and encoding
2. Check for missing or malformed data
3. Review logs for specific error messages

### Performance Issues

1. Adjust chunk size in bulk operations
2. Monitor cluster resources
3. Consider using multiple shards for large datasets

## Security Considerations

- Use HTTPS in production environments
- Implement proper authentication
- Restrict network access to OpenSearch cluster
- Use environment variables for sensitive configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
