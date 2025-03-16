from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure DATABASE_URL is set
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Create database engine
engine = create_engine(DATABASE_URL)

# Create metadata instance
metadata = MetaData()

# Ensure tables are created
def init_db():
    metadata.create_all(bind=engine)  # Pass 'bind' explicitly

init_db()


