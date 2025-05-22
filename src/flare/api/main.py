from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..rag.qdrant_handler import QdrantHandler, Distance
from ..embedding.main import BGEEmbedding
from ..utils.document_handler import DocumentHandler
from ..llm.main import LLMHandler
from dotenv import load_dotenv
import os
import uuid
from ..config import FastAPIConfig
load_dotenv()

app = FastAPI(title="FLARE API", description="API for FLARE RAG system")

# 初始化 QdrantHandler
qdrant_handler = QdrantHandler(host=os.getenv("QDRANT_HOST"), port=os.getenv("QDRANT_PORT"))

# 初始化 BGEEmbedding
embedder = BGEEmbedding()

# 初始化 LLMHandler
generation_config = {
    "max_new_tokens": 256,
    "temperature": 0.8,
    "top_p": 0.95,
    "do_sample": True,
    "num_return_sequences": 1
}

llm_handler = LLMHandler(
    fine_tuned_model_path="lora_model",
    generation_config=generation_config,
    max_retries=3,
    retry_delay=1.0,
    use_cpu=os.getenv("USE_CPU") == "True"
)
llm_handler.load_fine_tuned_model()

def ensure_handler_initialized():
    """確保 Qdrant 處理器已初始化"""
    if not qdrant_handler.client:
        qdrant_handler.start()

@app.post("/collection/create")
async def create_collection(collection_name: str, vector_size: int, distance: str):
    """創建新的 collection"""
    try:
        ensure_handler_initialized()
        qdrant_handler.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance=Distance[distance]
        )
        return {"message": f"Collection {collection_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add")
async def add_vectors(collection_name: str, chunk: str, payloads: List[Dict[str, Any]]):
    """添加chunk到集合"""
    try:
        ensure_handler_initialized()
        vectors = embedder.get_embedding(chunk)
        # 將 numpy 數組轉換為 Python 列表
        vectors_list = vectors.tolist()
        
        # 生成 UUID 作為點 ID
        point_id = str(uuid.uuid4())
        
        # 合併原始文字到 payloads
        merged_payloads = []
        for payload in payloads:
            merged_payload = payload.copy()
            merged_payload["text"] = chunk
            merged_payloads.append(merged_payload)
        
        qdrant_handler.add(
            collection_name=collection_name,
            vectors=[vectors_list],  # 包裝成二維列表
            payloads=merged_payloads,
            ids=[point_id]
        )
        return {"message": "Vectors added successfully", "id": point_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_vectors(collection_name: str, query: str, limit: int = FastAPIConfig["search_limit"], score_threshold: Optional[float] = FastAPIConfig["score_threshold"]):
    """搜索相似向量"""
    try:
        ensure_handler_initialized()
        vectors = embedder.get_embedding(query)
        # 將 numpy 數組轉換為 Python 列表
        vectors_list = vectors.tolist()
        results = qdrant_handler.search(
            collection_name=collection_name,
            query_vector=vectors_list,
            limit=limit,
            score_threshold=score_threshold
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


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), collection_name: str = FastAPIConfig["collection_name"], chunk_size: int = FastAPIConfig["chunk_size"], chunk_overlap: int = FastAPIConfig["chunk_overlap"]):
    """上傳文件"""
    try:
        ensure_handler_initialized()
        # 讀取文件內容
        file_content = await file.read()
        # 將文件儲存在tmp
        file_path = f"./tmp/{uuid.uuid4()}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        # 使用 DocumentHandler 處理文件
        document_handler = DocumentHandler()
        chunks = document_handler.process_document(file_path, chunk_size, chunk_overlap)
        # 將 chunks 添加到集合
        for chunk in chunks:
            vectors = embedder.get_embedding(chunk)
            # 將 numpy 數組轉換為 Python 列表
            vectors_list = vectors.tolist()
            qdrant_handler.add(
                collection_name=collection_name,
                vectors=[vectors_list],
                payloads=[{"text": chunk}],
                ids=[str(uuid.uuid4())]
            )
            
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(prompt: str, collection_name: str = FastAPIConfig["collection_name"], limit: int = FastAPIConfig["search_limit"], score_threshold: Optional[float] = FastAPIConfig["score_threshold"]):
    """聊天"""
    try:
        ensure_handler_initialized()
        vectors = embedder.get_embedding(prompt)
        # 將 numpy 數組轉換為 Python 列表
        vectors_list = vectors.tolist()
        results = qdrant_handler.search(
            collection_name=collection_name,
            query_vector=vectors_list,
            limit=limit,
            score_threshold=score_threshold
        )
        print(results)
        result = llm_handler.generate_fine_tuned_response(instruction="", input_text=prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
