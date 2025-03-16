import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure DATABASE_URL is set
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables")
