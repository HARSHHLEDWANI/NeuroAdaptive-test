from pydantic import BaseModel
from typing import List

# How a single paragraph should look
class ParagraphResponse(BaseModel):
    id: int
    order_index: int
    original_text: str
    adapted_text: str
    class Config:
        from_attributes = True  # Tells Pydantic to read SQLAlchemy objects

# How the whole article should look (including its paragraphs)
class ArticleResponse(BaseModel):
    id: int
    title: str
    topic: str
    paragraphs: List[ParagraphResponse]

    class Config:
        from_attributes = True