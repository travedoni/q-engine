import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": os.getenv("DB_PORT"),
}

def setup_db():
    """Create all tables from schema.sql"""

    # Read SQL schema
    with open('sql/schema.sql', 'r') as f:
        schema_sql = f.read()

    # Execute schema
    conn = psycopg2.connect(**DB_CONFIG)
    curr = conn.cursor()

    try:
        curr.execute(schema_sql)
        conn.commit()
        print("Database setup complete")
    except Exception as e:
        conn.rollback()
        print(f"Database setup failed: {e}")
    finally:
        curr.close()
        conn.close()

if __name__ == "__main__":
    setup_db()