# 🔥 FLARE: Fine-tuned LLMs with Augmented Retrieval for Enhanced Security

FLARE 是一個創新的安全增強系統，結合了微調的大型語言模型 (LLMs) 和增強檢索技術 (RAG)，旨在提供更智慧且可信的資安管理解決方案。FLARE 能夠根據檢索到的真實資料生成精準的回應，有效應對多樣化的資安場景。


## 🚀 主要特點

- **先進的語言模型微調技術**  
  使用 LoRA 等高效參數微調方法，針對資安資料集進行專業調校。

- **增強的檢索系統**  
  結合向量資料庫與語義查詢能力，提升生成內容的真實性與關聯性。

- **專注於安全性提升**  
  適用於資安報告生成、威脅分析輔助、異常事件回顧等場景。

- **高效能的處理機制**  
  可自訂 chunk 大小與 overlap，並支援多種硬體運行環境（CPU/GPU）。

## 🛠️ 系統架構

```
+---------------------+
\|  使用者查詢 (Query) |
+----------+----------+
|
v
+------------------------+
\| 向量資料庫檢索 (RAG)   |
+------------------------+
|
v
+------------------------+
\| 微調後語言模型 (LLM)   |
+------------------------+
|
v
+------------------------+
\| 安全回應生成 (Response)|
+------------------------+
````


## 📦 安裝說明

### 前置需求

- Python 3.10+
- pip / poetry
- CUDA 環境（如使用 GPU 模型）
- Docker（如需使用向量資料庫）

### 安裝步驟

```bash
# 1. 克隆專案
git clone https://github.com/your-username/flare-security.git
cd flare-security

# 2. 建立虛擬環境（可選）
python -m venv venv
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動向量資料庫（例如 Qdrant）
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# 5. 執行主程式
python src/main.py
````


## 🔧 設定檔（`.env`）

```env
LLM_MODEL_NAME=Qwen/Qwen1.5-7B-Chat
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=6333
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
CHUNK_SIZE=1024
CHUNK_OVERLAP=128
```


## 🧪 測試與驗證

```bash
# 執行單元測試
pytest tests/
```


## 📄 使用案例

* 自動產出資安事件摘要與報告
* 資安知識庫查詢輔助
* 生成威脅應對建議
* 提供即時 SOC 智慧回應

## 🧠 模型訓練說明（可選）

若需自行進行微調：

```bash
# 使用 LoRA 進行模型微調
python scripts/train.py --model Qwen/Qwen1.5-7B-Chat --dataset ./data/security_dataset.json --output ./checkpoints/flare-7b
```


## 📚 資源引用

* [Qwen LLM by Alibaba](https://huggingface.co/Qwen)
* [PEFT / LoRA 微調技術](https://github.com/huggingface/peft)
* [Qdrant 向量資料庫](https://qdrant.tech/)
* [Transformers by Hugging Face](https://huggingface.co/docs/transformers/index)


## 👤 貢獻者

* Warren Lee - 系統設計與模型微調

歡迎提交 PR 或 Issue！


## 📜 授權條款

本專案採用 MIT License 授權，詳情請參閱 `LICENSE` 檔案。