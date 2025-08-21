# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from pydantic import BaseModel, EmailStr
from typing import Optional

# -------------------------------------------------------------------
# Schemas de Usuário
# -------------------------------------------------------------------
class UserCreate(BaseModel):
    """Dados necessários para criar um usuário"""
    username: str
    email: EmailStr
    password: str
    enable_2fa: bool = False

class UserPasswordLogin(BaseModel):
    """Dados de login por senha"""
    username: str
    password: str

class User2FALogin(BaseModel):
    """Dados de login 2FA"""
    temp_token: str
    twofa_code: str

class UserOut(BaseModel):
    """Representação de usuário retornada pela API"""
    id: str
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    twofa_secret: Optional[str] = None
    provisioning_uri: Optional[str] = None

class UserUpdate(BaseModel):
    """Campos que podem ser atualizados em um usuário"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    enable_2fa: Optional[bool] = None

# -------------------------------------------------------------------
# Schemas de Cliente
# -------------------------------------------------------------------
class ClientCreate(BaseModel):
    """Dados necessários para criar um cliente"""
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr

class ClientOut(BaseModel):
    """Representação de cliente retornada pela API"""
    id: str
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: EmailStr
