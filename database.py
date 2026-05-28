"""数据库操作： SQLite 存储元数据, ChromaDB 存储向量索引"""
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Iterable

import chromadb
from chromadb.utils import embedding_functions

from config import SQLITE_PATH, CHROMA_DIR, EMBEDDING_MODEL, SEARCH_TOP_K
from models import Note

# """------------------ SQLite 初始化 -------------------------"""
def _init_sqlite() -> None:
    """创建 SQLite 表结构"""
    with sqlite3.connect(SQLITE_PATH) as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS notes (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags TEXT,              -- JSON 字符串数组
                        created_at TEXT,
                        updated_at TEXT
                     )
                     """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                name TEXT PRIMARY KEY,
                count INTEGER DEFAULT 0 
            )
                     """)

_init_sqlite()

def _note_from_row(row: tuple) -> Note:
    """将数据库行转换为 Note 对象"""
    return Note(
        id=row[0],
        title=row[1],
        content=row[2],
        tags=json.loads(row[3]) if row[3] else [],
        created_at=datetime.fromisoformat(row[4])
        updated_at=datetime.fromisoformat(row[5]),
    )

def get_all_notes() -> list(Note):
    """获取所有笔记,按更新时间倒序"""
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC")
        return [_note_from_row(row) for row in cursor.fetchall()]

def get_note_by_id(note_id: str) -> Note | None:
    """根据ID 获取笔记"""
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        return _note_from_row(row) if row else None

def save_note(note: Note) -> None:
    """保存或更新笔记,并更新标签统计"""
    with sqlite3.connect(SQLITE_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO notes (id, title, content, tags, created_at, updated_at)"
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                note.id,
                note.title,
                note.content,
                json.dumps(note.tags),
                note.created_at.isoformat(),
                note.updated_at.isoformat(),
            ),
        )
        # 重新计算标签计数
        cursor = conn.execute("SELECT tags FROM notes")
        tag_counter: dict[str, int] = {}
        for (tag_json,) in cursor.fetchall():
            for tag in json.loads(tags_json) if tags_json else []:
                tag_counter[tag] = tag_counter.get(tag, 0) + 1
        conn.execute("DELETE FROM tags")
        for tag, cnt in tag_counter.items():
            conn.execute("INSERT INTO tags (name, count) VALUES (?,?)",(tag, cnt))

def delete_note(note_id: str) -> None:
    """删除笔记"""
    with sqlite3.connect(SQLITE_PATH) as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        # 触发标签更急（通过调用save_note 传送一个临时对象重新统计，简便方法）
        # 更好的方法：重新计算，但这里简单重建一次
        notes = get_all_notes()
        tag_counter: dict[str, int] = {}
        for n in notes:
            for tag in n.tags:
                tag_counter[tag] = tag_counter.get(tag, 0) + 1
        conn.execute("DELETE FROM tags")
        for tag, cnt in tag_counter.items():
            conn.execute("INSERT INTO tags (name, count) VALUES (?,?)",(tag, cnt))

def get_all_tags() -> list[Tag]:
    """获取所有标签及其使用次数"""
    from models import Tag
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.execute("SELECT name,count FROM tags ORDER BY name")
        return [Tag(name=row[0], count=row[1]) for row in cursor.fetchall()]


# -------------------------------- ChromaDB 向量存储 -----------------------------------
_chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
_collection = _chroma_client.get_or_create_collection(
    name="notes_embeddings",
    embedding_function=_embed_fn,
    metadata={"hnsw:space":"cosine"}
)

def index_note(note: Note) -> None:
    """添加或更新笔记的向量索引"""
    _collection.upsert(
        ids=[note.id],
        documents=[note.content],
        metadatas=[{"title":note.title,"tags":",".join(note.tags)}]
    )
def delete_note(note_id: str) -> None:
    """删除向量索引"""
    try:
        _collection.delete(ids=[note_id])
    except Exception:
        pass

def semantic_search(query: str,top_k: int = SEARCH_TOP_K) -> list[dict]:
    """语义搜索,返回相关笔记及相似度距离"""
    results = _collection.query(query_texts=[query], n_results=top_k)
    if not results['ids'] or not results['ids'][0]:
        return []
    notes = []
    for i, note_id in enumerate(results['ids'][0]):
        note = get_note_by_id(note_id)
        if note:
            notes.append({
                "note": note,
                "distance": results['distances'][0][i] if results['distances'] else 0.0
            })
    return notes
    


