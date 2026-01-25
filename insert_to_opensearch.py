#!/usr/bin/env python3
"""
Script to insert history exam bounding box data into OpenSearch
"""

import pandas as pd
import json
import ast
from opensearchpy import OpenSearch, helpers
import logging
from typing import Dict, Any, List
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenSearchDataInserter:
    def __init__(self, host: str = 'localhost', port: int = 5601, 
                 username: str = None, password: str = None, 
                 use_ssl: bool = False, verify_certs: bool = False):
        """
        Initialize OpenSearch client
        
        Args:
            host: OpenSearch host
            port: OpenSearch port
            username: Username for authentication
            password: Password for authentication
            use_ssl: Whether to use SSL
            verify_certs: Whether to verify SSL certificates
        """
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=(username, password) if username and password else None,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            ssl_show_warn=False
        )
        
        self.index_name = 'history_exam_bbox'
        
    def create_index_mapping(self) -> Dict[str, Any]:
        """
        Create the index mapping for the bounding box data
        
        Returns:
            Dictionary containing the index mapping
        """
        mapping = {
            "mappings": {
                "properties": {
                    "image_path": {
                        "type": "keyword"
                    },
                    "page": {
                        "type": "keyword"
                    },
                    "artifact_type": {
                        "type": "keyword"
                    },
                    "question_no": {
                        "type": "float"
                    },
                    "bounding_box": {
                        "type": "keyword"
                    },
                    "left": {
                        "type": "float"
                    },
                    "top": {
                        "type": "float"
                    },
                    "width": {
                        "type": "float"
                    },
                    "height": {
                        "type": "float"
                    },
                    "exam_id": {
                        "type": "keyword"
                    },
                    "timestamp": {
                        "type": "date"
                    }
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            }
        }
        return mapping
    
    def create_index(self) -> bool:
        """
        Create the index if it doesn't exist
        
        Returns:
            True if index was created or already exists, False otherwise
        """
        try:
            if not self.client.indices.exists(index=self.index_name):
                mapping = self.create_index_mapping()
                response = self.client.indices.create(
                    index=self.index_name,
                    body=mapping
                )
                logger.info(f"Created index: {self.index_name}")
                return True
            else:
                logger.info(f"Index {self.index_name} already exists")
                return True
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False
    
    def parse_bounding_box(self, bbox_str: str) -> List[float]:
        """
        Parse bounding box string to list of floats
        
        Args:
            bbox_str: Bounding box string like "[170, 643, 1348, 1885]"
            
        Returns:
            List of float values
        """
        if pd.isna(bbox_str) or bbox_str == '':
            return []
        
        try:
            # Remove brackets and split by comma
            bbox_str = bbox_str.strip('[]')
            values = [float(x.strip()) for x in bbox_str.split(',')]
            return values
        except Exception as e:
            logger.warning(f"Error parsing bounding box '{bbox_str}': {e}")
            return []
    
    def clean_data(self, row: pd.Series) -> Dict[str, Any]:
        """
        Clean and prepare a row of data for indexing
        
        Args:
            row: Pandas Series containing a row of data
            
        Returns:
            Dictionary with cleaned data
        """
        # Extract exam ID from image path
        exam_id = None
        if pd.notna(row['image_path']):
            path_parts = row['image_path'].split('/')
            for part in path_parts:
                if part.isdigit():
                    exam_id = part
                    break
        
        # Clean numeric fields
        question_no = float(row['question_no']) if pd.notna(row['question_no']) else None
        left = float(row['left']) if pd.notna(row['left']) else None
        top = float(row['top']) if pd.notna(row['top']) else None
        width = float(row['width']) if pd.notna(row['width']) else None
        height = float(row['height']) if pd.notna(row['height']) else None
        
        # Parse bounding box
        bbox_values = self.parse_bounding_box(row['bounding_box'])
        
        document = {
            "image_path": row['image_path'] if pd.notna(row['image_path']) else None,
            "page": row['page'] if pd.notna(row['page']) else None,
            "artifact_type": row['artifact_type'] if pd.notna(row['artifact_type']) else None,
            "question_no": question_no,
            "bounding_box": row['bounding_box'] if pd.notna(row['bounding_box']) else None,
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "exam_id": exam_id,
            "bbox_values": bbox_values if bbox_values else None
        }
        
        # Remove None values
        document = {k: v for k, v in document.items() if v is not None}
        
        return document
    
    def insert_data(self, csv_file_path: str) -> bool:
        """
        Insert data from CSV file into OpenSearch
        
        Args:
            csv_file_path: Path to the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read CSV file
            logger.info(f"Reading CSV file: {csv_file_path}")
            df = pd.read_csv(csv_file_path)
            logger.info(f"Loaded {len(df)} records from CSV")
            
            # Create index if it doesn't exist
            if not self.create_index():
                return False
            
            # Prepare documents for bulk insertion
            documents = []
            for index, row in df.iterrows():
                try:
                    doc = self.clean_data(row)
                    if doc:  # Only add non-empty documents
                        documents.append({
                            "_index": self.index_name,
                            "_source": doc
                        })
                except Exception as e:
                    logger.warning(f"Error processing row {index}: {e}")
                    continue
            
            logger.info(f"Prepared {len(documents)} documents for insertion")
            
            # Bulk insert documents
            if documents:
                success, failed = helpers.bulk(
                    self.client,
                    documents,
                    chunk_size=100,
                    request_timeout=30
                )
                
                logger.info(f"Successfully inserted {success} documents")
                if failed:
                    logger.warning(f"Failed to insert {len(failed)} documents")
                    for error in failed[:5]:  # Log first 5 errors
                        logger.error(f"Error: {error}")
                
                return True
            else:
                logger.warning("No valid documents to insert")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            return False
    
    def search_data(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search data in the index
        
        Args:
            query: Search query (optional)
            
        Returns:
            List of search results
        """
        if query is None:
            query = {"match_all": {}}
        
        try:
            response = self.client.search(
                index=self.index_name,
                body={"query": query},
                size=100
            )
            
            hits = response['hits']['hits']
            results = [hit['_source'] for hit in hits]
            
            logger.info(f"Found {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Error searching data: {e}")
            return []

def main():
    """Main function to run the data insertion"""
    
    # Configuration - modify these values according to your OpenSearch setup
    config = {
        'host': 'localhost',
        'port': 9200,
        'username': "admin",  # Set if authentication is required
        'password': "hanSHin@1",  # Set if authentication is required
        'use_ssl': False,  # Set to True if using HTTPS
        'verify_certs': False  # Set to True if you want to verify SSL certificates
    }
    
    # CSV file path
    csv_file_path = 'data/processed/history_exam/74/74_bbox_info.csv'
    
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        logger.error(f"CSV file not found: {csv_file_path}")
        return
    
    # try:
    # Initialize inserter
    inserter = OpenSearchDataInserter(**config)
    
    # Test connection
    logger.info("Testing OpenSearch connection...")
    health = inserter.client.cluster.health()
    logger.info(f"OpenSearch cluster health: {health['status']}")
    
    # Insert data
    logger.info("Starting data insertion...")
    success = inserter.insert_data(csv_file_path)
    
    if success:
        logger.info("Data insertion completed successfully!")
        
        # Optional: Search for some data to verify insertion
        logger.info("Searching for inserted data...")
        results = inserter.search_data()
        
        if results:
            logger.info(f"Sample result: {results[0]}")
        
    else:
        logger.error("Data insertion failed!")
            
    # except Exception as e:
    #     logger.error(f"Error in main execution: {e}")

if __name__ == "__main__":
    main() 