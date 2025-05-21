import requests
import numpy as np
from typing import List, Union, Dict, Any

class BGEEmbedding:
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "bge-m3:latest"):
        """
        初始化 BGEEmbedding 類別
        
        Args:
            base_url (str): Ollama API 的基礎 URL
        """
        self.base_url = base_url
        self.model_name = model_name
        
    def _call_ollama_api(self, prompt: str) -> Dict[str, Any]:
        """
        調用 Ollama API
        
        Args:
            prompt (str): 輸入文本
            
        Returns:
            Dict[str, Any]: API 響應
        """
        url = f"{self.base_url}/api/embed"
        payload = {
            "model": self.model_name,
            "input": prompt
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        獲取單個文本的嵌入向量
        
        Args:
            text (str): 輸入文本
            
        Returns:
            np.ndarray: 文本的嵌入向量（一維數組）
        """
        if not text.strip():
            raise ValueError("輸入文本不能為空")
            
        response = self._call_ollama_api(text)
        embedding = np.array(response["embeddings"])
        
        if len(embedding) == 0:
            raise ValueError("獲取到的嵌入向量為空")
            
        # 確保返回一維向量
        return embedding.flatten()
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        獲取多個文本的嵌入向量
        
        Args:
            texts (List[str]): 輸入文本列表
            
        Returns:
            np.ndarray: 文本嵌入向量矩陣
        """
        if not texts:
            raise ValueError("輸入文本列表不能為空")
            
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        return np.array(embeddings)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        計算兩個文本之間的相似度
        
        Args:
            text1 (str): 第一個文本
            text2 (str): 第二個文本
            
        Returns:
            float: 相似度分數（範圍：-1 到 1）
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        # 計算向量範數
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        # 檢查是否為零向量
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        # 計算餘弦相似度
        similarity = np.dot(emb1, emb2) / (norm1 * norm2)
        
        # 確保結果在有效範圍內
        return float(np.clip(similarity, -1.0, 1.0))
