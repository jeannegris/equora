# -------------------------------------------------------------------
# Imports padrão e externos
# -------------------------------------------------------------------
import os
import uuid
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional
import io
import base64

import pyotp
import qrcode
import geoip2.database
from fastapi import APIRouter, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

# -------------------------------------------------------------------
# Imports internos
# -------------------------------------------------------------------
from backend.db import db_equora
from backend.schemas.schemas_equora import (
    UserCreate, UserPasswordLogin, User2FALogin, UserOut, 
    ClientCreate, ClientOut, UserUpdate
)




# -------------------------------------------------------------------
# Configurações de sessão
# -------------------------------------------------------------------
router = APIRouter(prefix="/admin", tags=["Painel Admin Equora"])
SESSION_COOKIE_NAME = "equora_session"
SESSION_EXPIRE_MINUTES = 30

# -------------------------------------------------------------------
# Estatísticas de Acesso (rota usada pelo frontend AdminStatistics)
# Coleção: stats_access
# Campos esperados: { ip: str, location?: {country, city, latitude, longitude}, timestamp: datetime }
# -------------------------------------------------------------------


class AccessIn(BaseModel):
    ip: str


@router.get("/stats/access")
async def list_access_stats(start: Optional[str] = None, end: Optional[str] = None):
    """Retorna acessos salvos (opcional filtro por intervalo ISO date yyyy-mm-dd)."""
    query = {}
    if start or end:
        # converter strings para datetimes simples (com hora 00:00) para filtrar
        try:
            if start:
                start_dt = datetime.fromisoformat(start)
            else:
                start_dt = None
            if end:
                end_dt = datetime.fromisoformat(end)
            else:
                end_dt = None
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use ISO yyyy-mm-dd or full datetime")

        if start_dt and end_dt:
            query["timestamp"] = {"$gte": start_dt, "$lte": end_dt}
        elif start_dt:
            query["timestamp"] = {"$gte": start_dt}
        elif end_dt:
            query["timestamp"] = {"$lte": end_dt}

    cursor = db_equora["stats_access"].find(query).sort("timestamp", -1).limit(1000)
    results = []
    async for doc in cursor:
        # normalizar retorno para o frontend
        loc = doc.get("location")
        norm_loc = None
        if loc and isinstance(loc, dict):
            # aceitar várias formas de chaves e converter strings para números
            lat = None
            lon = None
            if "latitude" in loc:
                lat = loc.get("latitude")
            elif "lat" in loc:
                lat = loc.get("lat")
            if "longitude" in loc:
                lon = loc.get("longitude")
            elif "lng" in loc:
                lon = loc.get("lng")

            try:
                if isinstance(lat, str):
                    lat = float(lat)
                if isinstance(lon, str):
                    lon = float(lon)
            except Exception:
                lat = None
                lon = None

            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                norm_loc = {
                    "country": loc.get("country"),
                    "city": loc.get("city"),
                    "latitude": lat,
                    "longitude": lon
                }
        results.append({
            "ip": doc.get("ip"),
            "location": norm_loc,
            "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None
        })
    return results


@router.post("/stats/access", status_code=201)
async def create_access_stat(access: AccessIn):
    """Insere um registro simples de acesso. O frontend envia apenas o IP."""
    doc = {"ip": access.ip, "timestamp": datetime.utcnow()}
    # tentativa simples de lookup geoip se banco local estiver presente (opcional)
    try:
        # inserir sem bloquear caso geoip não esteja configurado
        reader_path = os.getenv("GEOIP_DB_PATH")
        if not reader_path:
            # tentar fallback relativo ao diretório backend
            this_dir = os.path.dirname(__file__)
            reader_path = os.path.abspath(os.path.join(this_dir, '..', 'GeoLite2-City.mmdb'))
        if reader_path and os.path.exists(reader_path):
            try:
                with geoip2.database.Reader(reader_path) as reader:
                    r = reader.city(access.ip)
                    loc = {"country": r.country.name, "city": r.city.name, "latitude": r.location.latitude, "longitude": r.location.longitude}
                    doc["location"] = loc
            except Exception:
                pass
    except Exception:
        pass

    await db_equora["stats_access"].insert_one(doc)
    return {"result": "ok"}


@router.delete("/stats/access")
async def clear_access_stats(request: Request):
    """Limpa todos os registros de acesso — requer sessão de admin."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=401, detail="Não autenticado")
    user_id = await verify_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    user = await db_equora.users.find_one({"id": user_id})
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem limpar estatísticas")
    await db_equora["stats_access"].delete_many({})
    return {"result": "cleared"}


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
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

# Token temporário para login 2FA
# Nota: não usar armazenamento em memória para temp tokens quando backend
# roda em múltiplas instâncias (pm2, cluster). Usaremos a coleção MongoDB
# `temp_tokens` para prover consistência entre processos.

# -------------------------------------------------------------------
# Usuários
# -------------------------------------------------------------------
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
        twofa_secret = pyotp.random_base32()
        user_dict["twofa_secret"] = twofa_secret
        user_dict["provisioning_uri"] = pyotp.TOTP(twofa_secret).provisioning_uri(
            name=user.email, issuer_name="Equora Systems"
        )
    else:
        user_dict["twofa_secret"] = None

    await db_equora.users.insert_one(user_dict)
    return UserOut(**user_dict)

@router.get("/users", response_model=List[UserOut])
async def list_users():
    users = await db_equora.users.find().to_list(100)
    return [UserOut(**u) for u in users]

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

    # Campos básicos
    if user_update.username and user_update.username != user.get("username"):
        update_fields["username"] = user_update.username
    if user_update.email and user_update.email != user.get("email"):
        update_fields["email"] = user_update.email
    if user_update.is_active is not None and user_update.is_active != user.get("is_active"):
        update_fields["is_active"] = user_update.is_active
    if user_update.is_admin is not None and user_update.is_admin != user.get("is_admin"):
        update_fields["is_admin"] = user_update.is_admin
    if user_update.password and user_update.password.strip():
        update_fields["password_hash"] = hash_password(user_update.password)

    # Lógica 2FA
    if user_update.enable_2fa is not None:
        is_enabled = bool(user.get("twofa_secret"))
        if user_update.enable_2fa and (not is_enabled or not user.get("provisioning_uri")):
            secret = pyotp.random_base32()
            update_fields["twofa_secret"] = secret
            update_fields["provisioning_uri"] = pyotp.TOTP(secret).provisioning_uri(
                name=user_update.email or user.get("email"), issuer_name="Equora Systems"
            )
            update_fields["provisioning_uri_used"] = False
        elif not user_update.enable_2fa and is_enabled:
            update_fields["twofa_secret"] = None
            update_fields["provisioning_uri"] = None
            update_fields["provisioning_uri_used"] = None

    if update_fields:
        result = await db_equora.users.update_one({"id": user_id}, {"$set": update_fields})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Falha ao atualizar: usuário não encontrado")

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

# -------------------------------------------------------------------
# Login / Sessão / 2FA
# -------------------------------------------------------------------
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

@router.post("/login/password")
async def login_password(data: UserPasswordLogin):
    user = await db_equora.users.find_one({"username": {"$regex": f"^{data.username}$", "$options": "i"}})
    if not user or user["password_hash"] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    if user.get("twofa_secret"):
        temp_token = secrets.token_urlsafe(32)
        expire = datetime.utcnow() + timedelta(minutes=5)
        db_equora.temp_tokens.insert_one({"token": temp_token, "user_id": user["id"], "expire": expire})
        needs_setup = not user.get("provisioning_uri_used", False)
        provisioning_uri = user.get("provisioning_uri") if needs_setup else None
        return {"2fa_required": True, "temp_token": temp_token, "provisioning_uri": provisioning_uri}
    else:
        session_id = create_session(user["id"])
        response = JSONResponse(content={"message": "Login realizado", "user": UserOut(**user).dict()})
        response.set_cookie(key=SESSION_COOKIE_NAME, value=session_id, httponly=True, max_age=SESSION_EXPIRE_MINUTES*60)
        return response

@router.post("/login/2fa")
async def login_2fa(data: User2FALogin, response: Response):
    token_info = await db_equora.temp_tokens.find_one({"token": data.temp_token})
    if not token_info or token_info["expire"] < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token temporário inválido ou expirado")

    user = await db_equora.users.find_one({"id": token_info["user_id"]})
    if not user or not user.get("twofa_secret"):
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou 2FA não habilitado")

    totp = pyotp.TOTP(user["twofa_secret"])
    if not totp.verify(data.twofa_code):
        raise HTTPException(status_code=401, detail="Código 2FA inválido")

    if not user.get("provisioning_uri_used", False):
        await db_equora.users.update_one({"id": user["id"]}, {"$set": {"provisioning_uri_used": True}})

    await db_equora.temp_tokens.delete_one({"token": data.temp_token})
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

# -------------------------------------------------------------------
# Clientes
# -------------------------------------------------------------------
@router.post("/clients", response_model=ClientOut)
async def create_client(client_in: ClientCreate, request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    user_id = await verify_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Não autenticado")
    client_dict = client_in.dict()
    client_dict["id"] = str(uuid.uuid4())
    await db_equora["clients"].insert_one(client_dict)
    return ClientOut(**client_dict)

@router.get("/clients", response_model=List[ClientOut])
async def list_clients(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    user_id = await verify_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Não autenticado")

