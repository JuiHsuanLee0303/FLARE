import logging
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel, PeftConfig
import re
from typing import Optional, Dict, Any
from functools import lru_cache
import time
import torch

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMError(Exception):
    """自定義異常類別"""
    pass

class LLMHandler:
    def __init__(self, 
                 fine_tuned_model_path: str,
                 generation_config: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 use_cpu: bool = False):
        self.fine_tuned_model_path = fine_tuned_model_path
        self.fine_tuned_model = None
        self.fine_tuned_tokenizer = None
        self.generation_config = generation_config or {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.use_cpu = use_cpu
        self.device = "cpu" if use_cpu else ("cuda" if torch.cuda.is_available() else "cpu")
        self._is_initialized = False

    def __del__(self):
        """清理資源"""
        self.close()

    def close(self):
        """顯式關閉資源"""
        try:
            if hasattr(self, '_is_initialized') and self._is_initialized:
                if hasattr(self, 'fine_tuned_model') and self.fine_tuned_model is not None:
                    del self.fine_tuned_model
                    self.fine_tuned_model = None
                if hasattr(self, 'fine_tuned_tokenizer') and self.fine_tuned_tokenizer is not None:
                    del self.fine_tuned_tokenizer
                    self.fine_tuned_tokenizer = None
                self._is_initialized = False
                logger.info("資源已成功清理")
        except Exception as e:
            logger.error(f"清理資源時發生錯誤: {str(e)}")

    def find_latest_checkpoint(self, base_path: str) -> str:
        """找到最新的檢查點目錄"""
        for attempt in range(self.max_retries):
            try:
                base_path = Path(base_path)
                checkpoint_dirs = [d for d in base_path.glob("checkpoint-*") if d.is_dir()]
                
                if not checkpoint_dirs:
                    raise LLMError(f"No checkpoint directories found in {base_path}")
                
                checkpoint_numbers = []
                for d in checkpoint_dirs:
                    match = re.search(r'checkpoint-(\d+)', d.name)
                    if match:
                        checkpoint_numbers.append(int(match.group(1)))
                
                if not checkpoint_numbers:
                    raise LLMError("No valid checkpoint numbers found")
                
                latest_checkpoint = max(checkpoint_numbers)
                latest_checkpoint_dir = base_path / f"checkpoint-{latest_checkpoint}"
                
                logger.info(f"Found latest checkpoint at: {latest_checkpoint_dir}")
                return str(latest_checkpoint_dir)
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(self.retry_delay)
                else:
                    raise LLMError(f"Failed to find latest checkpoint after {self.max_retries} attempts: {str(e)}")

    def load_fine_tuned_model(self):
        """載入微調後的模型"""
        for attempt in range(self.max_retries):
            try:
                logger.info("Loading fine-tuned model...")
                
                latest_checkpoint = self.find_latest_checkpoint(self.fine_tuned_model_path)
                
                peft_config = PeftConfig.from_pretrained(latest_checkpoint)
                
                # 配置量化參數
                quantization_config = None
                if not self.use_cpu and torch.cuda.is_available():
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        llm_int8_enable_fp32_cpu_offload=True
                    )
                
                # 設定記憶體配置
                memory_config = {
                    0: "12GiB",  # GPU 記憶體
                    "cpu": "24GiB"  # CPU 記憶體
                }
                
                # 載入基礎模型
                base_model = AutoModelForCausalLM.from_pretrained(
                    peft_config.base_model_name_or_path,
                    quantization_config=quantization_config,
                    device_map="auto" if not self.use_cpu else None,
                    trust_remote_code=True,
                    max_memory=memory_config,
                    offload_folder="offload",
                    offload_state_dict=True,
                    offload_buffers=True
                )
                
                # 載入tokenizer
                self.fine_tuned_tokenizer = AutoTokenizer.from_pretrained(
                    peft_config.base_model_name_or_path,
                    trust_remote_code=True
                )
                
                # 載入LoRA權重
                self.fine_tuned_model = PeftModel.from_pretrained(
                    base_model,
                    latest_checkpoint,
                    device_map="auto" if not self.use_cpu else None,
                    max_memory=memory_config,
                    offload_folder="offload",
                    offload_state_dict=True,
                    offload_buffers=True
                )
                
                if self.use_cpu:
                    self.fine_tuned_model = self.fine_tuned_model.to(self.device)
                
                self._is_initialized = True
                logger.info(f"Fine-tuned model loaded successfully on {self.device}")
                return
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(self.retry_delay)
                else:
                    raise LLMError(f"Failed to load model after {self.max_retries} attempts: {str(e)}")

    @lru_cache(maxsize=100)
    def generate_fine_tuned_response(self, instruction: str, input_text: str) -> str:
        """使用微調後的模型生成回應"""
        if not self._is_initialized:
            raise LLMError("Model not initialized. Please call load_fine_tuned_model() first.")
            
        for attempt in range(self.max_retries):
            try:
                prompt = f"Instruction: {instruction}\nInput: {input_text}\nOutput:"
                inputs = self.fine_tuned_tokenizer(prompt, return_tensors="pt").to(self.device)
                outputs = self.fine_tuned_model.generate(
                    **inputs,
                    **self.generation_config
                )
                response = self.fine_tuned_tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = response.split("Output:")[-1].strip()
                return response
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(self.retry_delay)
                else:
                    raise LLMError(f"Failed to generate response after {self.max_retries} attempts: {str(e)}")
