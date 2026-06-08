"""工具函數: Markdown 渲染、文本截斷等"""

from rich.markdown import Markdown

def render_markdown(content: str) -> Markdown:
    """將 Markdown 文本轉換為 Rich 可渲染對象"""
    return Markdown(content)

def truncate_text(text: str, max_len: int = 200) -> str:
    """截斷文本, 添加省略號"""
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."
