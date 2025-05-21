from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import numpy as np

class QdrantHandler:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        vector_size: int = 1024,
        distance: Distance = Distance.COSINE
    ):
        """
        Initialize Qdrant handler
        
        Args:
            host: Qdrant server host address
            port: Qdrant server port
            vector_size: vector dimension
            distance: distance metric
        """
        self.host = host
        self.port = port
        self.vector_size = vector_size
        self.distance = distance
        self.client = None

    def start(self) -> None:
        """
        Start Qdrant client
        """
        self.client = QdrantClient(host=self.host, port=self.port)

    def create_collection(
        self,
        collection_name: str,
        vector_size: Optional[int] = None,
        distance: Optional[Distance] = None
    ) -> None:
        """
        Create a new collection
        
        Args:
            collection_name: name of the collection
            vector_size: vector dimension (optional, uses default if not specified)
            distance: distance metric (optional, uses default if not specified)
        """
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call start() first.")
            
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size or self.vector_size,
                    distance=distance or self.distance
                )
            )

    def add(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add vectors and related data to collection
        
        Args:
            collection_name: name of the collection
            vectors: list of vectors
            payloads: list of related data
            ids: optional list of IDs
        """
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call start() first.")
        
        if ids is None:
            ids = [str(i) for i in range(len(vectors))]
            
        self.client.upsert(
            collection_name=collection_name,
            points=models.Batch(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )
        )

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        payload_filter: Optional[Dict[str, Any]] = None,
        filter_conditions: Optional[List[Dict[str, Any]]] = None,
        filter_type: str = "must"
    ) -> List[Dict[str, Any]]:
        """
        Search for most similar vectors
        
        Args:
            collection_name: name of the collection
            query_vector: query vector
            limit: number of results
            score_threshold: similarity threshold
            payload_filter: simple filter conditions for payload fields (e.g. {"category": "news"})
            filter_conditions: complex filter conditions list (e.g. [
                {"key": "category", "match": "news", "range": None},
                {"key": "date", "match": None, "range": {"gte": "2024-01-01"}}
            ])
            filter_type: type of filter combination ("must", "should", "must_not")
            
        Returns:
            list of search results
        """
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call start() first.")
        
        search_params = {}
        if score_threshold is not None:
            search_params["score_threshold"] = score_threshold
            
        if payload_filter is not None or filter_conditions is not None:
            conditions = []
            
            # 處理簡單的 payload_filter
            if payload_filter is not None:
                conditions.extend([
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                    for key, value in payload_filter.items()
                ])
            
            # 處理複雜的 filter_conditions
            if filter_conditions is not None:
                for condition in filter_conditions:
                    field_condition = None
                    
                    # 處理精確匹配
                    if condition.get("match") is not None:
                        field_condition = models.FieldCondition(
                            key=condition["key"],
                            match=models.MatchValue(value=condition["match"])
                        )
                    
                    # 處理範圍查詢
                    if condition.get("range") is not None:
                        range_params = {}
                        if "gte" in condition["range"]:
                            range_params["gte"] = condition["range"]["gte"]
                        if "lte" in condition["range"]:
                            range_params["lte"] = condition["range"]["lte"]
                        if "gt" in condition["range"]:
                            range_params["gt"] = condition["range"]["gt"]
                        if "lt" in condition["range"]:
                            range_params["lt"] = condition["range"]["lt"]
                            
                        field_condition = models.FieldCondition(
                            key=condition["key"],
                            range=models.Range(**range_params)
                        )
                    
                    if field_condition is not None:
                        conditions.append(field_condition)
            
            # 根據 filter_type 建立對應的過濾器
            if filter_type == "must":
                search_params["query_filter"] = models.Filter(must=conditions)
            elif filter_type == "should":
                search_params["query_filter"] = models.Filter(should=conditions)
            elif filter_type == "must_not":
                search_params["query_filter"] = models.Filter(must_not=conditions)
            else:
                raise ValueError(f"Unsupported filter type: {filter_type}")
            
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            **search_params
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]

    def manage(self, action: str, collection_name: str, **kwargs) -> Any:
        """
        Manage collection operations
        
        Args:
            action: operation type ('delete', 'update', 'get_info')
            collection_name: name of the collection
            **kwargs: operation related parameters
            
        Returns:
            operation result
        """
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call start() first.")
            
        if action == "delete":
            return self.client.delete_collection(collection_name=collection_name)
        elif action == "update":
            # Update collection configuration
            return self.client.update_collection(
                collection_name=collection_name,
                **kwargs
            )
        elif action == "get_info":
            return self.client.get_collection(collection_name=collection_name)
        else:
            raise ValueError(f"Unknown action: {action}")

    def list_collections(self) -> List[str]:
        """
        List all available collections
        
        Returns:
            list of collection names
        """
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call start() first.")
            
        collections = self.client.get_collections().collections
        return [collection.name for collection in collections]
