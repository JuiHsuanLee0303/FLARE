from qdrant_handler import QdrantHandler
import numpy as np
import logging
from datetime import datetime
import uuid

# 設定日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Qdrant demo application")
    
    # Initialize QdrantHandler
    logger.info("Initializing QdrantHandler with parameters:")
    logger.info("Host: localhost, Port: 6333, Collection: demo_collection")
    handler = QdrantHandler(
        host="localhost",
        port=6333,
        collection_name="demo_collection",
        vector_size=4,  # Use a smaller vector size for demonstration
        distance="Cosine"
    )
    
    # Start client
    logger.info("Starting Qdrant client...")
    handler.start()
    logger.info("Qdrant client started successfully")
    
    # Create some example vectors and related data
    logger.info("Creating example vectors and payloads...")
    vectors = [
        [0.1, 0.2, 0.3, 0.4],
        [0.2, 0.3, 0.4, 0.5],
        [0.3, 0.4, 0.5, 0.6],
        [0.4, 0.5, 0.6, 0.7]
    ]
    
    payloads = [
        {"text": "This is the first document", "category": "A"},
        {"text": "This is the second document", "category": "B"},
        {"text": "This is the third document", "category": "A"},
        {"text": "This is the fourth document", "category": "B"}
    ]
    
    # Generate UUID as point IDs
    ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
    
    logger.info(f"Created {len(vectors)} vectors and corresponding payloads")
    
    # Add vectors and data to the collection
    logger.info("Adding vectors and payloads to collection...")
    start_time = datetime.now()
    handler.add(vectors=vectors, payloads=payloads, ids=ids)
    end_time = datetime.now()
    logger.info(f"Data addition completed in {(end_time - start_time).total_seconds():.2f} seconds")
    
    # Create a query vector
    logger.info("Creating query vector for similarity search...")
    query_vector = [0.2, 0.3, 0.4, 0.5]
    
    # Search for the most similar vectors
    logger.info("Performing similarity search...")
    start_time = datetime.now()
    results = handler.search(
        query_vector=query_vector,
        limit=2,
        score_threshold=0.7
    )
    end_time = datetime.now()
    logger.info(f"Search completed in {(end_time - start_time).total_seconds():.2f} seconds")
    
    # Display search results
    print("\nSearch results:")
    logger.info(f"Found {len(results)} matching results")
    for idx, result in enumerate(results, 1):
        logger.info(f"Processing result {idx}/{len(results)}")
        print(f"ID: {result['id']}")
        print(f"Similarity score: {result['score']:.4f}")
        print(f"Content: {result['payload']}")
        print("---")
    
    # Get collection information
    logger.info("Retrieving collection information...")
    collection_info = handler.manage("get_info")
    print("\nCollection information:")
    print(f"Vector count: {collection_info.vectors_count}")
    print(f"Vector dimension: {collection_info.config.params.vectors.size}")
    logger.info(f"Collection contains {collection_info.vectors_count} vectors")
    
    # Clean up: Delete the demo collection
    logger.info("Cleaning up: Deleting demo collection...")
    handler.manage("delete")
    logger.info("Demo collection successfully deleted")
    print("\nDemo collection deleted")
    
    logger.info("Demo application completed successfully")

if __name__ == "__main__":
    main()
