"""AI 推理模塊： 連接本地 Ollama 服務"""

import requests
from config import OLLAMA_URL, LLM_MODEL, OLLAMA_TEMPERATURE, OLLAMA_MAX_TOKENS, OLLAMA_TOP_P

def generate_answer(question: str,context: str) -> str:
    """
    基於檢索到的上下文生成答案
    - 如果 context 為空, 則直接告知無法回答
    """
    if not context.strip():
        return "知識庫中沒有相關筆記,無法回答該問題.請先添加内容."
    prompt= f"""你是一個知識庫助手,請僅根據下面提供的資料内容回答用戶的問題.如果資料不足以回答問題,請說“根據現有知識無法回答”.
    資料: {context}
    問題: {question}
    回答."""
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "num_predict": OLLAMA_MAX_TOKENS,
            "top_p": OLLAMA_TOP_P,
        }
    }

    try:
        resp = requests.post(OLLAMA_URL,json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["response"].strip()
    except Exception as e:
        return f"()⚠️ 调用本地模型失败：{str(e)}\n请确保 Ollama 已运行（ollama serve）并已拉取模型（ollama pull {LLM_MODEL}）。"
