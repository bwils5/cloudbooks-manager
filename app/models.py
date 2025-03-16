from sqlalchemy import Table, Column, Integer, String, DateTime, func
from app.database import metadata

# Define the books table
books = Table(
    "books",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("author", String(255), nullable=False),
    Column("description", String(2000), nullable=True),
)

# Define the activity log table
activity_log = Table(
    "activity_log",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("action", String(255), nullable=False),
    Column("detail", String(500), nullable=False),
    Column("timestamp", DateTime, server_default=func.now()),
)

# Define the users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(255), unique=True, nullable=False),
    Column("hashed_password", String(255), nullable=False),
    Column("role", String(50), nullable=False, default="user"),
)

# Ensure tables are created
# metadata.create_all()
