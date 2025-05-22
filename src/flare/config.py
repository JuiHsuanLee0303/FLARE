DocumentHandlerConfig = {
    "chunk_size": 1000,
    "chunk_overlap": 200
}

QdrantConfig = {
    "url": "http://localhost:6333",
    "api_key": "1234567890"
}

EmbeddingConfig = {
    "model_name": "bge-m3:latest"
}

FastAPIConfig = {
    "collection_name": "default_collection",
    "vector_size": 1024,
    "distance": "COSINE",
    "search_limit": 10,
    "score_threshold": 0.5,
    "chunk_size": 2000,
    "chunk_overlap": 200
}

LLMConfig = {
    "model_path": "lora_model",
    "use_cpu": True
}