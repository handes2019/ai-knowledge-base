import os

# 項目根目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR,"data")
os.makedirs(DATA_DIR, exist_ok=True)

# SQLite 數據庫路徑 (存儲筆記元數據,標簽)
SQLITE_PATH= os.path.join(DATA_DIR,"knowledge.db")

# ChromaDB 持久化目錄
CHROMA_DIR = os.path.join(DATA_DIR,"chroma_db")

# Ollama API 地址
OLLAMA_URL = "http://localhost:11434/api/generate"

# 使用的本地模型
LLM_MODEL = "qwen3.5:0.8b"

# Embedding 模型名稱
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# 語義檢索返回的筆記數量
SEARCH_TOP_K = 5
