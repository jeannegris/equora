# repositories/twofactor_repository.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

def _as_objid(user_id: str):
    if not ObjectId.is_valid(user_id):
        return None
    return ObjectId(user_id)

async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str):
    oid = _as_objid(user_id)
    if not oid:
        return None
    return await db.colaboradores.find_one({"_id": oid})

async def save_user_totp_secret(db: AsyncIOMotorDatabase, user_id: str, secret: str):
    oid = _as_objid(user_id)
    if not oid:
        return None
    return await db.colaboradores.update_one(
        {"_id": oid},
        {"$set": {"totp_secret": secret, "twoFactorAuth": True}}
    )
