from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
import time

# Load environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Metadata for table creation
metadata = MetaData()

# Connection test to debug Render issue
try:
    with engine.connect() as conn:
        print("✅ Connected to the database successfully!")
except Exception as e:
    print(f"❌ Failed to connect to the database: {e}")
    time.sleep(60)  # Keeps the logs visible for debugging before Render restarts

# Function to initialize DB (for migrations, etc.)
def init_db():
    metadata.create_all(bind=engine)

