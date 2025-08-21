import asyncio
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from db import db_equora
import hashlib
from datetime import datetime

async def create_admin_user():
    username = "admin"
    password = "admin123"  # Altere em produção!
    existing_user = await db_equora.users.find_one({"username": username})
    if existing_user:
        print(f"Usuário '{username}' já existe!")
        return
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user = {
        "id": username,
        "username": username,
        "email": "admin@equora.com",
        "password_hash": password_hash,
        "is_active": True,
        "is_admin": True,
        "twofa_secret": "123456",
        "created_at": datetime.utcnow()
    }
    await db_equora.users.insert_one(user)
    print(f"Usuário admin criado! Usuário: {username} | Senha: {password} | 2FA: 123456")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
