from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy import update, delete, insert
from app.database import engine
from app.models import books, activity_log, users
from app.auth import authenticate_user, get_current_user, hash_password, is_admin
import shutil
import os
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#  Logging activity
def log_activity(action: str, detail: str):
    query = insert(activity_log).values(action=action, detail=detail)
    with engine.connect() as conn:
        conn.execute(query)
        conn.commit()

#  User Registration Endpoint
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

@app.post("/register/")
async def register_user(user: UserCreate):
    with engine.connect() as conn:
        query = select(users).where(users.c.username == user.username)
        result = conn.execute(query).fetchone()

        if result:
            raise HTTPException(status_code=400, detail="Username already exists")

        hashed_pw = hash_password(user.password)
        query = insert(users).values(username=user.username, hashed_password=hashed_pw, role=user.role)
        conn.execute(query)
        conn.commit()

    return {"message": "User registered successfully!"}

#  Secure File Deletion (Admin Only)
@app.delete("/uploads/{filename}")
async def delete_file(filename: str, current_user: dict = Depends(is_admin)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    log_activity("Deleted file", f"Filename: {filename}")
    return {"message": f"{filename} deleted successfully"}

#  File Upload with Logging
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    log_activity("Uploaded file", f"Filename: {file.filename}")
    return {"filename": file.filename, "path": file_path}

#  File Download
@app.get("/uploads/{filename}")
async def download_file(filename: str, current_user: dict = Depends(get_current_user)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return {"download_url": f"http://127.0.0.1:8000/uploads/{filename}"}

#  Book CRUD Operations with RBAC
class Book(BaseModel):
    title: str
    author: str
    description: Optional[str] = None

@app.post("/books/")
async def create_book(book: Book, current_user: dict = Depends(is_admin)):
    query = insert(books).values(title=book.title, author=book.author, description=book.description)
    with engine.connect() as conn:
        result = conn.execute(query)
        conn.commit()
    log_activity("Created book", f"Title: {book.title}")
    return {"id": result.lastrowid, **book.dict()}

@app.get("/books/", response_model=List[dict])
async def read_books(
    skip: int = 0, 
    limit: int = 10, 
    title: Optional[str] = None, 
    author: Optional[str] = None, 
    current_user: dict = Depends(get_current_user)
) -> List[dict]:
    query = select(books)
    if title:
        query = query.where(books.c.title.like(f"%{title}%"))
    if author:
        query = query.where(books.c.author.like(f"%{author}%"))
    query = query.offset(skip).limit(limit)
    with engine.connect() as conn:
        result = conn.execute(query)
        return [dict(row._mapping) for row in result]

@app.get("/books/{book_id}")
async def read_book(book_id: int, current_user: dict = Depends(get_current_user)) -> dict:
    query = select(books).where(books.c.id == book_id)
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Book not found")
        return dict(result._mapping)

@app.put("/books/{book_id}")
async def update_book(book_id: int, book: Book, current_user: dict = Depends(is_admin)) -> dict:
    query = update(books).where(books.c.id == book_id).values(title=book.title, author=book.author, description=book.description)
    with engine.connect() as conn:
        result = conn.execute(query)
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book not found")
    log_activity("Updated book", f"ID: {book_id}")
    return {"id": book_id, **book.dict()}

@app.delete("/books/{book_id}")
async def delete_book(book_id: int, current_user: dict = Depends(is_admin)) -> dict:
    query = delete(books).where(books.c.id == book_id)
    with engine.connect() as conn:
        result = conn.execute(query)
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book not found")
    log_activity("Deleted book", f"ID: {book_id}")
    return {"message": "Book deleted successfully"}

#  Activity Log Retrieval
@app.get("/activity-log/", response_model=List[dict])
async def get_activity_log(current_user: dict = Depends(is_admin)) -> List[dict]:
    query = select(activity_log)
    with engine.connect() as conn:
        result = conn.execute(query)
        return [dict(row._mapping) for row in result]

#  Token Generation
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["username"], "token_type": "bearer"}
