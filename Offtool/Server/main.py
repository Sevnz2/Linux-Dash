from fastapi import FastAPI, WebSocket
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import json
import subprocess
import os
import psutil
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Optional, List
from sqlmodel import select
from passlib.context import CryptContext  # pip install passlib[bcrypt]
import jwt
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from database import create_tables, get_session
SECRET_KEY = "mynameisromanus"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
if not os.path.exists("../logs/"):
    os.makedirs("../logs/")
if not os.path.exists("../logs/webserverlogs.txt"):
    open("../logs/webserverlogs.txt", "x")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
class UserCreate(BaseModel):
    username: str
    password: str
def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()
DATABASE_URL = "sqlite:///./database.db"
engine= create_engine(DATABASE_URL, echo=True)
ram = psutil.virtual_memory()
templates = Jinja2Templates(directory="templates")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""""
Gebruiker aanmaken post, wordt momenteel niet gebruikt omdat ik de enige gebruiker zal zijn.
@app.post("/login", response_model=User)
async def create_note(payload:UserCreate, session: Session = Depends(get_session)):
    note = User.model_validate(payload)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note
"""

class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "username": "noah",
                "password": "pi123"
            }]
        }
    }

@app.on_event('startup')
def startup():
    create_tables()
@app.post("/create-user")
async def create_user_endpoint(
        user_create: UserCreate,  # ← UserCreate ipv dict!
        session: Session = Depends(get_session)
):
    hashed_pw = pwd_context.hash(user_create.password)  # ← .password ipv ["password"]

    user = User(username=user_create.username, password_hash=hashed_pw)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "username": user.username}



@app.post("/api/login")
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    # Vind user
    user = session.exec(select(User).where(User.username == request.username)).first()

    if not user or not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Foute credentials")

    # Maak JWT token
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@app.get("/status")
async def status(request: Request):
    return templates.TemplateResponse("status.html", {"request": request})
@app.get("/logs")
async def logs(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})
@app.get("/running")
async def running(request: Request):
    return "pi status: Running"
@app.get("/ram")
async def ram(request: Request):
    ram_info = (f"Totale ram: {ram.total / (1024**3):.if}, Gebruikt {ram.percent}%, Over {ram.used/ (1024**3):.if}")