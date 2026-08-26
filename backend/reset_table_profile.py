from app.db.session import engine
from app.db.base import Base
from sqlalchemy import text

def reset_table():
    # Use the database connection to drop the table
    with engine.connect() as connection:
        print("Dropping 'user_profiles' table...")
        # This SQL command deletes the table
        connection.execute(text("DROP TABLE IF EXISTS user_profiles CASCADE;"))
        connection.commit()
        print("✅ Table dropped successfully.")

if __name__ == "__main__":
    reset_table()