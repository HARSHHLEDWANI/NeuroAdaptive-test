from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.modules.content.models import Article, ArticleReading
from app.modules.profiling.models import UserProfile
from app.services.adaptation import adaptation_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/articles/{article_id}")
async def get_article(article_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    # 1. Fetch the Article
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 2. Log the Reading Session
    reading = ArticleReading(user_id=user_id, article_id=article.id)
    db.add(reading)
    db.commit()

    # 3. Identify the User Archetype
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    current_archetype = profile.primary_archetype if profile else "THE_PIONEER"

    # 3. Construct Dual-Content Response
    # We map the database objects to a dictionary so we can include 'adapted_text'
    # without modifying the actual database records.
    adapted_paragraphs = []
    for p in article.paragraphs:
        adapted_text = await adaptation_service.adapt_content(
            p.original_text, 
            current_archetype
        ) # The AI-transformed version

        adapted_paragraphs.append({
            "id": p.id,
            "order_index": p.order_index,
            "original_text": p.original_text, # The raw text from DB
            "adapted_text": adapted_text
        })

    return {
        "id": article.id,
        "title": article.title,
        "topic": article.topic,
        "paragraphs": sorted(adapted_paragraphs, key=lambda x: x["order_index"])
    }