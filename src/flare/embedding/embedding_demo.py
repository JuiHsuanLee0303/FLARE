from main import BGEEmbedding
import logging

# 設定日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 初始化
logger.info("初始化 BGEEmbedding...")
embedder = BGEEmbedding()
logger.info("BGEEmbedding 初始化完成")

# 獲取單個文本的嵌入向量
logger.info("開始獲取單個文本的嵌入向量...")
embedding = embedder.get_embedding("你好，世界")
logger.info(f"獲取到的向量維度: {len(embedding)}")

# 獲取多個文本的嵌入向量
logger.info("開始獲取多個文本的嵌入向量...")
embeddings = embedder.get_embeddings(["你好", "世界"])
logger.info(f"獲取到的向量數量: {len(embeddings)}")

# 計算相似度
logger.info("開始計算文本相似度...")
similarity = embedder.compute_similarity("你好", "您好")
logger.info(f"相似度分數: {similarity:.4f}")