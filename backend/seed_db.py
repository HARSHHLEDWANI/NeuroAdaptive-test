from app.db.session import SessionLocal
from app.modules.content.models import Article, Paragraph

def seed_data():
    # Open a connection to the database
    db = SessionLocal()

    # 1. Check if we already have data (so we don't duplicate it if you run this twice)
    if db.query(Article).first():
        print("Database already has articles! Skipping seed.")
        db.close()
        return

    print("Seeding database with sample articles...")

    # --- ARTICLE 1: Technology ---
    article1 = Article(title="Introduction to Quantum Computing", topic="Technology")
    db.add(article1)
    db.commit() # We commit here so 'article1' gets an ID assigned by PostgreSQL

    paragraphs1 = [
        Paragraph(article_id=article1.id, order_index=1, original_text="Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics to solve problems too complex for classical computers."),
        Paragraph(article_id=article1.id, order_index=2, original_text="Instead of using standard bits that are either 0 or 1, quantum computers use 'qubits'. These qubits can exist in multiple states simultaneously, a magical property known as superposition."),
        Paragraph(article_id=article1.id, order_index=3, original_text="This allows quantum computers to process massive amounts of possibilities all at once, making them incredibly powerful for things like discovering new medicines or cracking encryption.")
    ]
    db.add_all(paragraphs1)

    # --- ARTICLE 2: Science ---
    article2 = Article(title="The Anatomy of a Black Hole", topic="Science")
    db.add(article2)
    db.commit()

    paragraphs2 = [
        Paragraph(article_id=article2.id, order_index=1, original_text="A black hole is a region of spacetime where gravity is so strong that nothing—no particles or even electromagnetic radiation such as light—can escape from it."),
        Paragraph(article_id=article2.id, order_index=2, original_text="The boundary of no escape is called the event horizon. Crossing this invisible line means you are permanently trapped by the black hole's gravitational pull.")
    ]
    db.add_all(paragraphs2)

    # Save all the paragraphs to the database
    db.commit()
    db.close()
    
    print("✅ Seeding complete! Added 2 articles and their paragraphs to the library.")

if __name__ == "__main__":
    seed_data()