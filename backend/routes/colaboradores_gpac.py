from fastapi import APIRouter, HTTPException, Body, status
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from ..db import db_gpac
from bson import ObjectId
import hashlib

router = APIRouter(prefix="/colaboradores", tags=["Colaboradores GPAC"])

class Colaborador(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: str  # 'medico' | 'enfermeiro' | 'recepcionista' | 'administrador' (compatível com valores antigos também)
    specialty: Optional[list] = None
    crm: Optional[str] = None
    gender: Optional[str] = None  # 'masculino' | 'feminino' | 'outros'
    birthDate: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    rgOrgan: Optional[str] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    cep: Optional[str] = None
    photo: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None  # Esta será hasheada antes de salvar
    changePasswordOnFirstLogin: Optional[bool] = False
    twoFactorAuth: Optional[bool] = False
    userProfile: Optional[str] = None  # 'administradores' | 'gestores' | 'equipe_medica' | 'cadastro'
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    message: str
    requiresPasswordChange: Optional[bool] = False
    twoFactorAuth: Optional[bool] = False

@router.post("/login", response_model=LoginResponse)
async def login_colaborador(login_data: LoginRequest):
    """
    Endpoint para autenticação de colaboradores
    """
    try:
        print(f"[DEBUG] Tentativa de login para username: {login_data.username}")
        
        # Buscar colaborador pelo username
        colaborador = await db_gpac.colaboradores.find_one({"username": login_data.username})
        
        if not colaborador:
            print(f"[DEBUG] Usuário não encontrado: {login_data.username}")
            return LoginResponse(
                success=False,
                message="Usuário não encontrado"
            )
        
        print(f"[DEBUG] Usuário encontrado: {colaborador.get('name')}")
        
        # Verificar senha (hash)
        password_hash = hashlib.sha256(login_data.password.encode()).hexdigest()
        stored_password = colaborador.get("password")
        
        print(f"[DEBUG] Senha fornecida (hash): {password_hash}")
        print(f"[DEBUG] Senha armazenada: {stored_password}")
        
        # Verificar se a senha armazenada está hasheada ou não
        if stored_password == password_hash:
            # Senha hasheada confere
            print("[DEBUG] Senha hasheada confere")
        elif stored_password == login_data.password:
            # Senha em texto simples confere (backward compatibility)
            print("[DEBUG] Senha em texto simples confere")
        elif not stored_password and login_data.password in ['admin', 'admin123', '123456']:
            # Senha não definida no banco, aceitar senhas padrão temporariamente
            print("[DEBUG] Senha não definida, usando senha padrão temporária")
            # Atualizar a senha no banco com hash
            await db_gpac.colaboradores.update_one(
                {"_id": ObjectId(colaborador["_id"])},
                {"$set": {"password": password_hash}}
            )
        else:
            print("[DEBUG] Senha não confere")
            return LoginResponse(
                success=False,
                message="Senha incorreta"
            )
        
        # Preparar dados do usuário para retorno (sem senha)
        user_data = {
            "id": str(colaborador["_id"]),
            "name": colaborador.get("name"),
            "email": colaborador.get("email"),
            "role": migrate_role_to_portuguese(colaborador.get("role", "")),  # Migrar role automaticamente
            "username": colaborador.get("username"),
            "userProfile": colaborador.get("userProfile"),
            "specialty": colaborador.get("specialty", []),
            "crm": colaborador.get("crm")
        }
        
        print(f"[DEBUG] Login bem-sucedido para: {colaborador.get('name')}")
        
        return LoginResponse(
            success=True,
            user=user_data,
            message="Login realizado com sucesso",
            requiresPasswordChange=colaborador.get("changePasswordOnFirstLogin", False),
            twoFactorAuth=colaborador.get("twoFactorAuth", False)
        )
        
    except Exception as e:
        print(f"[ERROR] Erro no login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/debug/{username}")
async def debug_colaborador(username: str):
    """
    Endpoint de debug para verificar dados do colaborador
    """
    try:
        colaborador = await db_gpac.colaboradores.find_one({"username": username})
        if not colaborador:
            return {"found": False, "username": username}
        
        return {
            "found": True,
            "username": colaborador.get("username"),
            "name": colaborador.get("name"),
            "email": colaborador.get("email"),
            "role": colaborador.get("role"),
            "has_password": bool(colaborador.get("password")),
            "password_length": len(colaborador.get("password", "")),
            "password_looks_hashed": len(colaborador.get("password", "")) == 64
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/test-login")
async def test_login(login_data: LoginRequest):
    """
    Endpoint de teste simplificado para debug
    """
    return {
        "received_username": login_data.username,
        "received_password": login_data.password,
        "message": "Endpoint funcionando"
    }

@router.post("/reset-password/{username}")
async def reset_password(username: str, new_password: str = Body(..., embed=True)):
    """
    Endpoint para resetar senha de um colaborador (apenas para debug/teste)
    """
    try:
        # Hash da nova senha
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        result = await db_gpac.colaboradores.update_one(
            {"username": username},
            {"$set": {"password": password_hash}}
        )
        
        if result.modified_count == 0:
            return {"success": False, "message": "Usuário não encontrado ou senha já é a mesma"}
        
        return {
            "success": True, 
            "message": f"Senha resetada para o usuário {username}",
            "password_hash": password_hash
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/")
async def criar_colaborador(colaborador: Colaborador):
    colaborador_dict = colaborador.dict()
    
    # Validar se o perfil de usuário existe
    if colaborador_dict.get("userProfile"):
        profile = await db_gpac.profiles.find_one({"name": colaborador_dict["userProfile"]})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Perfil '{colaborador_dict['userProfile']}' não encontrado. Por favor, selecione um perfil válido."
            )
    
    # Hash da senha se fornecida
    if colaborador_dict.get("password"):
        colaborador_dict["password"] = hashlib.sha256(colaborador_dict["password"].encode()).hexdigest()
    
    result = await db_gpac.colaboradores.insert_one(colaborador_dict)
    colaborador_dict["_id"] = str(result.inserted_id)
    
    # Remove a senha do retorno
    if "password" in colaborador_dict:
        del colaborador_dict["password"]
        
    return colaborador_dict

@router.get("/")
async def listar_colaboradores():
    colaboradores = []
    async for doc in db_gpac.colaboradores.find():
        colaborador = {
            "_id": str(doc["_id"]),
            "name": doc.get("name", ""),
            "email": doc.get("email", ""),
            "phone": doc.get("phone", ""),
            "role": migrate_role_to_portuguese(doc.get("role", "")),  # Migrar role automaticamente
            "specialty": doc.get("specialty", []),
            "crm": doc.get("crm", ""),
            "gender": doc.get("gender", ""),
            "birthDate": doc.get("birthDate", ""),
            "cpf": doc.get("cpf", ""),
            "rg": doc.get("rg", ""),
            "rgOrgan": doc.get("rgOrgan", ""),
            "address": doc.get("address", ""),
            "neighborhood": doc.get("neighborhood", ""),
            "city": doc.get("city", ""),
            "state": doc.get("state", ""),
            "cep": doc.get("cep", ""),
            "photo": doc.get("photo", ""),
            "username": doc.get("username", ""),
            # Nunca retornar a senha
            "changePasswordOnFirstLogin": doc.get("changePasswordOnFirstLogin", False),
            "twoFactorAuth": doc.get("twoFactorAuth", False),
            "userProfile": doc.get("userProfile", ""),
            "createdAt": doc.get("createdAt", datetime.utcnow()),
        }
        colaboradores.append(colaborador)
    return colaboradores

@router.put("/{id}")
async def atualizar_colaborador(id: str, colaborador: dict = Body(...)):
    try:
        # Validar se o perfil de usuário existe (se fornecido)
        if colaborador.get("userProfile"):
            profile = await db_gpac.profiles.find_one({"name": colaborador["userProfile"]})
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Perfil '{colaborador['userProfile']}' não encontrado. Por favor, selecione um perfil válido."
                )
        
        # Hash da senha se fornecida
        if colaborador.get("password"):
            colaborador["password"] = hashlib.sha256(colaborador["password"].encode()).hexdigest()
        elif "password" in colaborador and not colaborador["password"]:
            # Remove o campo password se estiver vazio (para não atualizar)
            del colaborador["password"]
            
        result = await db_gpac.colaboradores.update_one(
            {"_id": ObjectId(id)},
            {"$set": colaborador}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Colaborador não encontrado ou dados iguais")
        return {"message": "Colaborador atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def excluir_colaborador(id: str):
    try:
        result = await db_gpac.colaboradores.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Colaborador não encontrado")
        return {"message": "Colaborador excluído com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Função de migração para converter roles antigas para portuguesas
def migrate_role_to_portuguese(old_role: str) -> str:
    """Converte roles antigas em inglês para português"""
    role_migration = {
        'doctor': 'medico',
        'nurse': 'enfermeiro', 
        'receptionist': 'recepcionista',
        'admin': 'administrador'
    }
    return role_migration.get(old_role, old_role)

@router.post("/migrate-roles")
async def migrate_all_roles():
    """Endpoint para migrar todas as roles do inglês para português"""
    try:
        updated_count = 0
        async for colaborador in db_gpac.colaboradores.find():
            old_role = colaborador.get('role', '')
            new_role = migrate_role_to_portuguese(old_role)
            
            if new_role != old_role:
                await db_gpac.colaboradores.update_one(
                    {"_id": colaborador["_id"]},
                    {"$set": {"role": new_role}}
                )
                updated_count += 1
        
        return {
            "message": f"Migração concluída. {updated_count} colaboradores foram atualizados.",
            "updated_count": updated_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na migração: {str(e)}")

# Middleware para garantir compatibilidade ao ler roles
def normalize_role_response(colaborador_data: dict) -> dict:
    """Normaliza a role na resposta para garantir compatibilidade"""
    if 'role' in colaborador_data:
        colaborador_data['role'] = migrate_role_to_portuguese(colaborador_data['role'])
    return colaborador_data
