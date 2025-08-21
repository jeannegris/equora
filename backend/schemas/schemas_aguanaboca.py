
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class Produto(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price: float
    category: str  # 'bolos' ou 'doces'
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProdutoCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None

class ProdutoUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
