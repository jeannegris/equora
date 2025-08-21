from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional
import pyotp, qrcode, io, base64
from datetime import datetime
from bson import ObjectId

from ..db import db_gpac
from ..repositories.twofactor_repository import get_user_by_id, save_user_totp_secret


router = APIRouter(tags=["2FA GPAC"])

# aceita camelCase e snake_case do front
class SetupRequest(BaseModel):
    user_id: str = Field(alias="userId")
    model_config = {"populate_by_name": True}

class VerifyRequest(BaseModel):
    user_id: str = Field(alias="userId")
    code: str
    model_config = {"populate_by_name": True}

class DisableReq(BaseModel):
    user_id: str = Field(alias="userId")
    reason: Optional[str] = None
    model_config = {"populate_by_name": True}

# troque por seu guard real (JWT/role admin)
def require_admin():
    return True

def _qr_data_url(otpauth_url: str) -> str:
    img = qrcode.make(otpauth_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

@router.get("/status")
async def twofa_status(userId: Optional[str] = Query(None), user_id: Optional[str] = Query(None)):
    uid = userId or user_id
    if not uid:
        raise HTTPException(status_code=422, detail="userId obrigatório")
    user = await get_user_by_id(db_gpac, uid)
    return {"enrolled": bool(user and user.get("totp_secret"))}

@router.post("/setup")
async def setup_2fa(data: SetupRequest):
    user = await get_user_by_id(db_gpac, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # não gere novo segredo se já estiver matriculado
    if user.get("totp_secret"):
        return {"alreadyEnrolled": True}

    secret = pyotp.random_base32()
    await save_user_totp_secret(db_gpac, data.user_id, secret)

    account = user.get("email") or user.get("username") or data.user_id
    otpauth_url = pyotp.TOTP(secret).provisioning_uri(name=account, issuer_name="GPAC")
    return {"qrCode": _qr_data_url(otpauth_url), "secret": secret}

@router.post("/verify")
async def verify_2fa(data: VerifyRequest):
    user = await get_user_by_id(db_gpac, data.user_id)
    if not user or not user.get("totp_secret"):
        return {"valid": False}
    totp = pyotp.TOTP(user["totp_secret"])
    return {"valid": bool(totp.verify(data.code, valid_window=1))}

@router.post("/disable", dependencies=[Depends(require_admin)])
async def disable_2fa(req: DisableReq):
    """Desliga 2FA do usuário e apaga o segredo TOTP."""
    if not ObjectId.is_valid(req.user_id):
        raise HTTPException(status_code=400, detail="userId inválido")
    oid = ObjectId(req.user_id)
    res = await db_gpac.colaboradores.update_one(
        {"_id": oid},
        {
            "$unset": {"totp_secret": "", "backup_codes": ""},
            "$set": {
                "twoFactorAuth": False,
                "mfaDisabledAt": datetime.utcnow(),
                "mfaDisabledReason": req.reason or "admin disabled",
            },
            "$inc": {"sessionVersion": 1},  # opcional: derruba sessões antigas
        },
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"ok": True}
