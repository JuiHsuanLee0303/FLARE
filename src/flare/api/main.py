from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..rag.qdrant_handler import QdrantHandler, Distance
from ..embedding.main import BGEEmbedding
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

app = FastAPI(title="FLARE API", description="API for FLARE RAG system")

# 初始化 QdrantHandler
qdrant_handler = QdrantHandler(host=os.getenv("QDRANT_HOST"), port=os.getenv("QDRANT_PORT"))

# 初始化 BGEEmbedding
embedder = BGEEmbedding()

# 請求模型
class CollectionConfig(BaseModel):
    collection_name: str = "default_collection"
    vector_size: int = 1024
    distance: str = "COSINE"

class VectorRequest(BaseModel):
    collection_name: str
    chunk: str
    payloads: List[Dict[str, Any]]

class SearchRequest(BaseModel):
    collection_name: str
    query: str
    limit: int = 10
    score_threshold: Optional[float] = None
    payload_filter: Optional[Dict[str, Any]] = None
    filter_conditions: Optional[List[Dict[str, Any]]] = None
    filter_type: str = "must"

def ensure_handler_initialized():
    """確保 Qdrant 處理器已初始化"""
    if not qdrant_handler.client:
        qdrant_handler.start()

@app.post("/collection/create")
async def create_collection(config: CollectionConfig):
    """創建新的 collection"""
    try:
        ensure_handler_initialized()
        qdrant_handler.create_collection(
            collection_name=config.collection_name,
            vector_size=config.vector_size,
            distance=Distance[config.distance]
        )
        return {"message": f"Collection {config.collection_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add")
async def add_vectors(request: VectorRequest):
    """添加chunk到集合"""
    try:
        ensure_handler_initialized()
        vectors = embedder.get_embedding(request.chunk)
        # 將 numpy 數組轉換為 Python 列表
        vectors_list = vectors.tolist()
        
        # 生成 UUID 作為點 ID
        point_id = str(uuid.uuid4())
        
        # 合併原始文字到 payloads
        merged_payloads = []
        for payload in request.payloads:
            merged_payload = payload.copy()
            merged_payload["text"] = request.chunk
            merged_payloads.append(merged_payload)
        
        qdrant_handler.add(
            collection_name=request.collection_name,
            vectors=[vectors_list],  # 包裝成二維列表
            payloads=merged_payloads,
            ids=[point_id]
        )
        return {"message": "Vectors added successfully", "id": point_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_vectors(request: SearchRequest):
    """搜索相似向量"""
    try:
        ensure_handler_initialized()
        vectors = embedder.get_embedding(request.query)
        # 將 numpy 數組轉換為 Python 列表
        vectors_list = vectors.tolist()
        results = qdrant_handler.search(
            collection_name=request.collection_name,
            query_vector=vectors_list,
            limit=request.limit,
            score_threshold=request.score_threshold,
            payload_filter=request.payload_filter,
            filter_conditions=request.filter_conditions,
            filter_type=request.filter_type
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/collection/{collection_name}")
async def delete_collection(collection_name: str):
    """刪除指定的集合"""
    try:
        ensure_handler_initialized()
        result = qdrant_handler.manage("delete", collection_name=collection_name)
        return {"message": f"Collection {collection_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collection/{collection_name}/info")
async def get_collection_info(collection_name: str):
    """獲取指定集合的信息"""
    try:
        ensure_handler_initialized()
        info = qdrant_handler.manage("get_info", collection_name=collection_name)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
async def list_collections():
    """列出所有可用的集合"""
    try:
        ensure_handler_initialized()
        collections = qdrant_handler.list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
