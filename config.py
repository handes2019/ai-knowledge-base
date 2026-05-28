from pathlib import Path

# 項目根目錄
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# SQLite 數據庫路徑 (存儲筆記元數據,標簽)
SQLITE_PATH= DATA_DIR / "knowledge.db"

# ChromaDB 持久化目錄
CHROMA_DIR = DATA_DIR / "chroma_db"

# Ollama API 地址
OLLAMA_URL = "http://localhost:11434/api/generate"

# 使用的本地模型
LLM_MODEL = "qwen3.5:0.8b"

# Embedding 模型名稱
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# 語義檢索返回的筆記數量
SEARCH_TOP_K = 5

# Ollama 生成参数
OLLAMA_TEMPERATURE = 0.2
OLLAMA_MAX_TOKENS = 512
OLLAMA_TOP_P=0.9
