from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from backend.schemas.schemas_equora import UserCreate, UserPasswordLogin, User2FALogin, UserOut, ClientCreate, ClientOut, UserUpdate
from backend.db import db_equora
from pydantic import EmailStr
from typing import List, Optional
import uuid, hashlib, os, time
from datetime import datetime, timedelta
import secrets
import pyotp
import qrcode
import io
import base64

router = APIRouter(prefix="/admin", tags=["Painel Admin Equora"])

SESSION_COOKIE_NAME = "equora_session"
SESSION_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
	return hashlib.sha256(password.encode()).hexdigest()

def create_session(user_id: str):
	session_id = secrets.token_urlsafe(32)
	expire = datetime.utcnow() + timedelta(minutes=SESSION_EXPIRE_MINUTES)
	db_equora.sessions.insert_one({"session_id": session_id, "user_id": user_id, "expire": expire})
	return session_id

async def verify_session(session_id: str):
	session = await db_equora.sessions.find_one({"session_id": session_id})
	if not session or session["expire"] < datetime.utcnow():
		return None
	return session["user_id"]

# --- Usuários ---
@router.post("/users", response_model=UserOut)
async def create_user(user: UserCreate):
    if await db_equora.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    user_dict = user.dict()
    user_dict["password_hash"] = hash_password(user.password)
    user_dict["is_active"] = True
    user_dict["is_admin"] = False
    user_dict["id"] = str(uuid.uuid4())
    del user_dict["password"]

    if user.enable_2fa:
        # Gerar um segredo TOTP
        twofa_secret = pyotp.random_base32()
        user_dict["twofa_secret"] = twofa_secret
        
        # Gerar URI de provisionamento para o QR Code
        provisioning_uri = pyotp.totp.TOTP(twofa_secret).provisioning_uri(
            name=user.email, issuer_name="Equora Systems"
        )
        user_dict["provisioning_uri"] = provisioning_uri
    else:
        user_dict["twofa_secret"] = None

    await db_equora.users.insert_one(user_dict)
    return UserOut(**user_dict)

@router.get("/users", response_model=List[UserOut])
async def list_users():
	users = await db_equora.users.find().to_list(100)
	return [UserOut(**u) for u in users]

@router.put("/users/{user_id}", response_model=UserOut)

@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: str, user_update: UserUpdate, request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=401, detail="Não autenticado")
    user_id_session = await verify_session(session_id)
    if not user_id_session:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    user_session = await db_equora.users.find_one({"id": user_id_session})
    if not user_session or not user_session.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar usuários")

    user = await db_equora.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_fields = {}
    if user_update.username is not None and user_update.username != user.get("username"):
        update_fields["username"] = user_update.username
    if user_update.email is not None and user_update.email != user.get("email"):
        update_fields["email"] = user_update.email
    if user_update.is_active is not None and user_update.is_active != user.get("is_active"):
        update_fields["is_active"] = user_update.is_active
    if user_update.is_admin is not None and user_update.is_admin != user.get("is_admin"):
        update_fields["is_admin"] = user_update.is_admin
    if user_update.password and user_update.password.strip():
        update_fields["password_hash"] = hash_password(user_update.password)
    if user_update.enable_2fa is not None:
        is_currently_enabled = bool(user.get("twofa_secret"))
        is_being_enabled = user_update.enable_2fa
        if is_being_enabled and (not is_currently_enabled or not user.get("provisioning_uri")):
            twofa_secret = pyotp.random_base32()
            update_fields["twofa_secret"] = twofa_secret
            provisioning_uri = pyotp.totp.TOTP(twofa_secret).provisioning_uri(
                name=user_update.email or user.get("email"), issuer_name="Equora Systems"
            )
            update_fields["provisioning_uri"] = provisioning_uri
            update_fields["provisioning_uri_used"] = False
        elif not is_being_enabled and is_currently_enabled:
            update_fields["twofa_secret"] = None
            update_fields["provisioning_uri"] = None
            update_fields["provisioning_uri_used"] = None
    if update_fields:
        result = await db_equora.users.update_one({"id": user_id}, {"$set": update_fields})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Falha ao atualizar: usuário não encontrado")
        if result.modified_count == 0 and not all(update_fields.get(k) == user.get(k) for k in update_fields):
            raise HTTPException(status_code=500, detail="Erro de servidor: os dados do usuário não foram modificados.")
    updated_user = await db_equora.users.find_one({"id": user_id})
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado após a atualização")
    return UserOut(**updated_user)
    user = await db_equora.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_fields = {}

    # Compara e adiciona campos alterados
    if user_update.username is not None and user_update.username != user.get("username"):
        update_fields["username"] = user_update.username
    if user_update.email is not None and user_update.email != user.get("email"):
        update_fields["email"] = user_update.email
    if user_update.is_active is not None and user_update.is_active != user.get("is_active"):
        update_fields["is_active"] = user_update.is_active
    if user_update.is_admin is not None and user_update.is_admin != user.get("is_admin"):
        update_fields["is_admin"] = user_update.is_admin

    # Adiciona a nova senha se fornecida e não estiver vazia.
    if user_update.password and user_update.password.strip():
        update_fields["password_hash"] = hash_password(user_update.password)

    # Lógica de 2FA robusta
    if user_update.enable_2fa is not None:
        is_currently_enabled = bool(user.get("twofa_secret"))
        is_being_enabled = user_update.enable_2fa

        # Habilitar 2FA: Força a regeneração se o estado estiver incompleto (sem URI)
        if is_being_enabled and (not is_currently_enabled or not user.get("provisioning_uri")):
            twofa_secret = pyotp.random_base32()
            update_fields["twofa_secret"] = twofa_secret
            
            provisioning_uri = pyotp.totp.TOTP(twofa_secret).provisioning_uri(
                name=user_update.email or user.get("email"), issuer_name="Equora Systems"
            )
            update_fields["provisioning_uri"] = provisioning_uri
            update_fields["provisioning_uri_used"] = False

        # Desabilitar 2FA
        elif not is_being_enabled and is_currently_enabled:
            update_fields["twofa_secret"] = None
            update_fields["provisioning_uri"] = None
            update_fields["provisioning_uri_used"] = None
    
    # Executa a atualização se houver alterações
    if update_fields:
        result = await db_equora.users.update_one({"id": user_id}, {"$set": update_fields})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Falha ao atualizar: usuário não encontrado")
        if result.modified_count == 0 and not all(update_fields.get(k) == user.get(k) for k in update_fields):
             # Se nenhum documento foi modificado, mas deveria ter sido, algo está errado.
            raise HTTPException(status_code=500, detail="Erro de servidor: os dados do usuário não foram modificados.")

    # Retorna o documento mais recente do banco de dados
    updated_user = await db_equora.users.find_one({"id": user_id})
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado após a atualização")
        
    return UserOut(**updated_user)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=401, detail="Não autenticado")
    user_id_session = await verify_session(session_id)
    if not user_id_session:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    user_session = await db_equora.users.find_one({"id": user_id_session})
    if not user_session or not user_session.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem excluir usuários")
    result = await db_equora.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Login + Sessão + 2FA ---
# Rota para retornar dados do usuário logado
@router.get("/login/me")
async def get_logged_user(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=401, detail="Não autenticado")
    user_id = await verify_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    user = await db_equora.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"user": UserOut(**user)}

# Dicionário para armazenar tokens temporários
temp_tokens = {}

@router.post("/login/password")
async def login_password(data: UserPasswordLogin):
    # Busca de usuário case-insensitive
    user = await db_equora.users.find_one({"username": {"$regex": f"^{data.username}$", "$options": "i"}})
    if not user or user["password_hash"] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    if user.get("twofa_secret"):
        # Gerar token temporário para a segunda etapa
        temp_token = secrets.token_urlsafe(32)
        temp_tokens[temp_token] = {"user_id": user["id"], "expire": datetime.utcnow() + timedelta(minutes=5)}
        
        # Verificar se o usuário precisa configurar o 2FA (primeiro login com 2FA)
        needs_setup = not user.get("provisioning_uri_used", False)
        provisioning_uri = user.get("provisioning_uri") if needs_setup else None

        return {"2fa_required": True, "temp_token": temp_token, "provisioning_uri": provisioning_uri}
    else:
        # Login direto sem 2FA
        session_id = create_session(user["id"])
        response = JSONResponse(content={"message": "Login realizado", "user": UserOut(**user).dict()})
        response.set_cookie(key=SESSION_COOKIE_NAME, value=session_id, httponly=True, max_age=SESSION_EXPIRE_MINUTES*60)
        return response

@router.post("/login/2fa")
async def login_2fa(data: User2FALogin, response: Response):
    # Validar token temporário
    token_info = temp_tokens.get(data.temp_token)
    if not token_info or token_info["expire"] < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token temporário inválido ou expirado")

    user = await db_equora.users.find_one({"id": token_info["user_id"]})
    if not user or not user.get("twofa_secret"):
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou 2FA não habilitado")

    # Validar código 2FA
    try:
        totp = pyotp.TOTP(user["twofa_secret"])
        if not totp.verify(data.twofa_code):
            raise HTTPException(status_code=401, detail="Código 2FA inválido")
    except Exception:
        if data.twofa_code != user["twofa_secret"]: # Fallback para o método antigo
            raise HTTPException(status_code=401, detail="Código 2FA inválido")

    # Marcar que o QR Code foi usado
    if not user.get("provisioning_uri_used", False):
        await db_equora.users.update_one({"id": user["id"]}, {"$set": {"provisioning_uri_used": True}})

    # Limpar token temporário e criar sessão final
    del temp_tokens[data.temp_token]
    session_id = create_session(user["id"])
    response.set_cookie(key=SESSION_COOKIE_NAME, value=session_id, httponly=True, max_age=SESSION_EXPIRE_MINUTES*60)
    return {"message": "Login realizado", "user": UserOut(**user).dict()}

@router.post("/logout")
async def logout(request: Request, response: Response):
	session_id = request.cookies.get(SESSION_COOKIE_NAME)
	if session_id:
		await db_equora.sessions.delete_one({"session_id": session_id})
		response.delete_cookie(SESSION_COOKIE_NAME)
	return {"message": "Logout realizado"}

# --- Clientes ---
@router.post("/clients", response_model=ClientOut)
async def create_client(client_in: ClientCreate, request: Request):
	session_id = request.cookies.get(SESSION_COOKIE_NAME)
	user_id = await verify_session(session_id)
	if not user_id:
		raise HTTPException(status_code=401, detail="Não autenticado")
	client_dict = client_in.dict()
	client_dict["id"] = str(uuid.uuid4())
	# Corrigir para usar a collection 'clients' no banco Equora
	await db_equora["clients"].insert_one(client_dict)
	return ClientOut(**client_dict)

@router.get("/clients", response_model=List[ClientOut])
async def list_clients(request: Request):
	session_id = request.cookies.get(SESSION_COOKIE_NAME)
	user_id = await verify_session(session_id)
	if not user_id:
		raise HTTPException(status_code=401, detail="Não autenticado")
	clients = await db_equora.clients.find().to_list(100)
	return [ClientOut(**c) for c in clients]


from fastapi import Body
import geoip2.database
import os
from pydantic import BaseModel

# Caminho do banco de dados GeoLite2 (deve ser baixado e colocado no backend)
GEOIP_DB_PATH = os.getenv("GEOIP_DB_PATH", "c:/Pessoal/Projetos/equora/backend/GeoLite2-City.mmdb")

def get_location_from_ip(ip: str):
	# Ignorar IPs locais
	if ip in ["127.0.0.1", "localhost", "::1"]:
		return {
			"country": "Local",
			"city": "Desenvolvimento",
			"latitude": 0.0,
			"longitude": 0.0
		}
	try:
		with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
			response = reader.city(ip)
			return {
				"country": response.country.name,
				"city": response.city.name,
				"latitude": response.location.latitude,
				"longitude": response.location.longitude
			}
	except Exception as e:
		print(f"Erro ao geolocalizar IP {ip}: {e}")
		return None


# Modelo para requisição de acesso
class AccessRequest(BaseModel):
	ip: str

@router.post("/stats/access")
async def record_access(data: AccessRequest):
	# Geolocalização automática
	location = get_location_from_ip(data.ip)
	access = {
		"ip": data.ip,
		"location": location,
		"timestamp": datetime.utcnow()
	}
	result = await db_equora.access_stats.insert_one(access)
	access["_id"] = str(result.inserted_id)
	return {"message": "Acesso registrado", "access": access}
# --- Estatísticas de acesso ---
@router.get("/stats/access")
async def access_stats():
	# Exemplo: retorna contagem de acessos e IPs
	stats = await db_equora.access_stats.find().to_list(100)

	for access in stats:
		if "_id" in access:
			access["_id"] = str(access["_id"])
	return stats

@router.delete("/stats/access")
async def clear_access_stats():
	result = await db_equora.access_stats.delete_many({})
	return {"message": f"{result.deleted_count} registros removidos."}
