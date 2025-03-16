from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy import insert
from app.database import engine
from app.models import users  # Import users table

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_user(username: str):
    with engine.connect() as conn:
        result = conn.execute(select(users).where(users.c.username == username)).fetchone()
        if result:
            return dict(result._mapping)
    return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def register_user(username: str, password: str, role: str):
    with engine.connect() as conn:
        # Check if user already exists
        result = conn.execute(select(users).where(users.c.username == username)).fetchone()
        if result:
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash the password and insert into the database
        hashed_password = hash_password(password)
        query = insert(users).values(
            username=username,
            hashed_password=hashed_password,
            role=role
        )
        conn.execute(query)
        conn.commit()

    return {"message": "User registered successfully!"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def is_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action")
    return user
