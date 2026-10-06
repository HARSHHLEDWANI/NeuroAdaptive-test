from app.db.session import engine

try:
    connection = engine.connect()
    print("✅ SUCCESS: Database connected successfully!")
    connection.close()
except Exception as e:
    print(f"Database connection failed: {type(e).__name__}")