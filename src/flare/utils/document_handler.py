import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from pypdf import PdfReader
import docx
import chardet

class DocumentHandler:
    """文件處理器，用於讀取和分塊處理各種格式的文件"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        初始化文件處理器
        
        Args:
            chunk_size (int): 每個文本塊的大小（字符數）
            chunk_overlap (int): 文本塊之間的重疊大小（字符數）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def read_file(self, file_path: str) -> str:
        """
        讀取文件內容
        
        Args:
            file_path (str): 文件路徑
            
        Returns:
            str: 文件內容
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"找不到文件：{file_path}")
            
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.txt':
            return self._read_text_file(file_path)
        elif file_extension == '.pdf':
            return self._read_pdf_file(file_path)
        elif file_extension == '.docx':
            return self._read_docx_file(file_path)
        else:
            raise ValueError(f"不支援的文件格式：{file_extension}")
    
    def _read_text_file(self, file_path: Path) -> str:
        """讀取文本文件"""
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            detected = chardet.detect(raw_data)
            encoding = detected['encoding']
        
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    def _read_pdf_file(self, file_path: Path) -> str:
        """讀取PDF文件"""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _read_docx_file(self, file_path: Path) -> str:
        """讀取Word文件"""
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        將文本分割成塊
        
        Args:
            text (str): 要分割的文本
            
        Returns:
            List[str]: 文本塊列表
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # 如果這不是最後一個塊，嘗試在句子或段落邊界處分割
            if end < text_length:
                # 尋找最近的句子結束符號
                for sep in ['. ', '! ', '? ', '\n']:
                    pos = text.rfind(sep, start, end)
                    if pos != -1:
                        end = pos + 1
                        break
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
            
        return chunks
    
    def process_document(self, file_path: str) -> List[str]:
        """
        處理文件並返回分塊後的文本
        
        Args:
            file_path (str): 文件路徑
            
        Returns:
            List[str]: 文本塊列表
        """
        text = self.read_file(file_path)
        return self.split_into_chunks(text)
