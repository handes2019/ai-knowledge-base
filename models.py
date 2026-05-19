from pydantic import BaseModel,Field
from datetime import datetime

class Note(BaseModel):
    id: str # UUID
    title: str
    content: str
    tags: list[str]=Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Tag(BaseModel):
    name: str
    count: int = 0
    

