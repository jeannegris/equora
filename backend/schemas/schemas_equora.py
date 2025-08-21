from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    enable_2fa: bool = False

class UserPasswordLogin(BaseModel):
    username: str
    password: str

class User2FALogin(BaseModel):
    temp_token: str
    twofa_code: str

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    twofa_secret: Optional[str] = None
    provisioning_uri: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    enable_2fa: Optional[bool] = None

class ClientCreate(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr

class ClientOut(BaseModel):
    id: str
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: EmailStr
