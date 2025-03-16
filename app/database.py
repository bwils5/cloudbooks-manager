from sqlalchemy import create_engine, MetaData
from app.config import DATABASE_URL

# Use PostgreSQL instead of MySQL
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
metadata = MetaData()

# Initialize the database
def init_db():
    metadata.create_all(engine)

init_db()

