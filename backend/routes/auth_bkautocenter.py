from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..schemas.schemas_bkautocenter import AdminAuth, AdminUser
from ..db import db_bkautocenter
import hashlib
import jwt
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/auth", tags=["Authentication BKAutoCenter"])

# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash da senha usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verificar senha"""
    return hash_password(password) == hashed_password

def create_access_token(data: dict):
    """Criar token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT e retornar usuário atual"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = await db_bkautocenter.admin_users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    return AdminUser(**user)

@router.post("/register")
async def register_admin(user_data: AdminAuth):
    """Registrar novo usuário admin (apenas para desenvolvimento)"""
    try:
        # Verificar se usuário já existe
        existing_user = await db_bkautocenter.admin_users.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Usuário já existe")
        
        # Criar novo usuário
        hashed_password = hash_password(user_data.password)
        admin_user = AdminUser(
            username=user_data.username,
            password_hash=hashed_password
        )
        
        await db_bkautocenter.admin_users.insert_one(admin_user.model_dump())
        return {"message": "Usuário criado com sucesso"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")

@router.post("/login")
async def login(user_data: AdminAuth):
    """Login do usuário admin"""
    try:
        # Buscar usuário
        user = await db_bkautocenter.admin_users.find_one({"username": user_data.username})
        if not user or not verify_password(user_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        # Criar token
        access_token = create_access_token(data={"sub": user["username"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer login: {str(e)}")

@router.get("/me")
async def get_current_user_info(current_user: AdminUser = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    return {
        "username": current_user.username,
        "id": current_user.id,
        "created_at": current_user.created_at
    }
